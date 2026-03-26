import os
import shutil
from pathlib import Path
from file_organizer_custom_exceptions import (
    InvalidDestinationPath,
    InvalidSourcePath,
    InsufficientSpaceError,
    PathError,
)
from transfer_mode import TransferMode
from transfer_result import TransferResult
from transfer_plan import TransferPlan

class FileOrganizerLogic:
    """Core business logic for validating, planning, and transferring files."""

    FILE_CATEGORIES = {
        "images": {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"},
        "documents": {
            ".pdf",
            ".doc",
            ".docx",
            ".txt",
            ".xlsx",
            ".xls",
            ".ppt",
            ".pptx",
            ".csv",
        },
        "audio": {".mp3", ".wav", ".aac", ".flac"},
        "video": {".mp4", ".mkv", ".avi", ".mov"},
        "archives": {".zip", ".rar", ".7z", ".tar", ".gz"},
        "scripts": {".py", ".js", ".html", ".css", ".json", ".xml"},
        "others": set(),
    }

    @staticmethod
    def normalize_path(path_value) -> Path:
        """Expand and resolve a user-provided path value into a `Path` object."""
        return Path(path_value).expanduser().resolve()

    @classmethod
    def collect_files(cls, source_path: Path, transfer_mode: TransferMode) -> list[Path]:
        """Return only file items selected by the given transfer mode."""
        transfer_plan = cls.build_transfer_plan(transfer_mode, source_path)
        files = []

        for item in transfer_plan.items:
            if item.is_file():
                files.append(item)

        return files
    
    @classmethod
    def validate_source_path(cls, source_path) -> Path:
        """Validate that the source exists and points to a directory."""
        path = cls.normalize_path(source_path)

        if not path.exists():
            raise InvalidSourcePath(f"Source path does not exist: {path}")

        if not path.is_dir():
            raise InvalidSourcePath(f"Source path is not a directory: {path}")

        return path

    @classmethod
    def validate_destination_path(cls, destination_path) -> Path:
        """Validate that the destination is a directory path or a creatable directory."""
        path = cls.normalize_path(destination_path)

        if path.exists() and not path.is_dir():
            raise InvalidDestinationPath(f"Destination path is not a directory: {path}")

        return path

    @staticmethod
    def validate_source_destination_relation(
        source_path: Path, destination_path: Path
    ) -> None:
        """Ensure source and destination do not overlap in unsafe ways."""
        if source_path == destination_path:
            raise PathError("Source and destination cannot be the same.")

        if destination_path in source_path.parents:
            raise PathError("Destination cannot be a parent of source.")

        if source_path in destination_path.parents:
            raise PathError("Destination cannot be inside source.")

    @classmethod
    def check_path(cls, source_path, destination_path):
        """Validate both paths and return their normalized `Path` objects."""
        valid_source = cls.validate_source_path(source_path)
        valid_destination = cls.validate_destination_path(destination_path)
        cls.validate_source_destination_relation(valid_source, valid_destination)

        return valid_source, valid_destination

    @staticmethod
    def get_total_size_of_files_from_list(files: list[Path]) -> int:
        """Return the cumulative size of the provided files in bytes."""
        total_size = 0

        for file_path in files:
            try:
                total_size += file_path.stat().st_size
            except OSError:
                continue

        return total_size
    
    
    def collect_files_from_multiple_sources(
        self,
        source_paths: list,
        transfer_mode: TransferMode
    ) -> list[Path]:
        """Collect files from multiple source directories into one list."""
        all_files = []

        for source in source_paths:
            source_path = Path(source)
            all_files.extend(self.collect_files(source_path, transfer_mode))

        return all_files
        
    @classmethod
    def get_total_size_of_files(cls, source_path: Path, transfer_mode: TransferMode) -> int:
        """Calculate the total size of files selected from a single source."""
        files = cls.collect_files(source_path, transfer_mode)
        return cls.get_total_size_of_files_from_list(files)

    @classmethod
    def get_total_size_of_multiple_sources(
        cls, source_paths: list, transfer_mode: TransferMode
    ) -> int:
        """Calculate the total size of files across multiple source directories."""
        total_size = 0

        for source in source_paths:
            total_size += cls.get_total_size_of_files(Path(source), transfer_mode)

        return total_size

    @staticmethod
    def get_disk_usage_target(path: Path) -> Path:
        """Return an existing path that can be used for disk usage checks."""
        current_path = path

        while not current_path.exists():
            parent = current_path.parent
            if parent == current_path:
                raise FileNotFoundError(f"Could not resolve an existing path for: {path}")
            current_path = parent

        return current_path

    @classmethod
    def are_on_same_drive(cls, source_path: Path, destination_path: Path) -> bool:
        """Return `True` when source and destination are on the same drive."""
        return source_path.drive.lower() == destination_path.drive.lower()

    @staticmethod
    def get_folder_size(folder_path: Path) -> int:
        """
        Calculate the total size of all non-symlink files under a folder.
        """
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(folder_path):
            for file_name in filenames:
                filename_path = os.path.join(dirpath, file_name)
                # skip if it is symbolic link
                if not os.path.islink(filename_path):
                    total_size += os.path.getsize(filename_path)
        return total_size

    @classmethod
    def check_disk_space(
        self,
        source_path: Path,
        destination_path: Path,
        transfer_mode: TransferMode
    ) -> None:
        """Ensure the destination has enough free space for a single-source transfer."""
        transfer_plan = self.build_transfer_plan(transfer_mode, source_path)
        use_move = transfer_plan.use_move

        # Moving on the same drive usually only updates directory entries, so a
        # full free-space check is not necessary in that case.
        if use_move and self.are_on_same_drive(source_path, destination_path):
            return

        files = self.collect_files(source_path, transfer_mode)
        total_size = self.get_total_size_of_files_from_list(files)
        disk_usage_target = self.get_disk_usage_target(destination_path)
        free_space = shutil.disk_usage(disk_usage_target).free

        if total_size > free_space:
            raise InsufficientSpaceError("There is not enough free space in destination.")

    
    def check_disk_space_for_multiple_sources(
        self, source_paths: list, destination_path: Path, transfer_mode: TransferMode
    ) -> None:
        """Ensure the destination has enough free space for a multi-source transfer."""
        needs_space_check = False

        for source in source_paths:
            source_path = Path(source)
            transfer_plan = self.build_transfer_plan(transfer_mode, source_path)
            use_move = transfer_plan.use_move

            if not use_move:
                needs_space_check = True
                break

            if not self.are_on_same_drive(source_path, destination_path):
                needs_space_check = True
                break

        if not needs_space_check:
            return

        total_size = self.get_total_size_of_multiple_sources(source_paths, transfer_mode)
        disk_usage_target = self.get_disk_usage_target(destination_path)
        free_space = shutil.disk_usage(disk_usage_target).free

        if total_size > free_space:
            raise InsufficientSpaceError(
                "There is not enough free space in destination."
            )

    @classmethod
    def create_category_directories(cls, destination_path: Path) -> None:
        """
        Create the category folders under the destination path.
        """
        for category, _ in cls.FILE_CATEGORIES.items():
            (destination_path / category).mkdir(parents=True, exist_ok=True)

    def multi_search_and_categorize_files(
        self,
        source_path_list: list,
        destination_path: Path,
        mode,
        progress_callback=None,
    ) -> TransferResult:
        """Run the transfer workflow for multiple sources and combine their results."""
        final_result = TransferResult()

        for address in source_path_list:
            partial_result = self.search_and_categorize_files(
                destination_path, Path(address), mode, progress_callback
            )

            final_result.transferred_files.extend(partial_result.transferred_files)
            final_result.skipped_files.extend(partial_result.skipped_files)
            final_result.errors.extend(partial_result.errors)

        return final_result

    @staticmethod
    def create_new_file_name(destination_path: Path, category: str, item: Path) -> Path:
        """Create a unique destination file path inside the chosen category folder."""
        category_path = destination_path / category
        category_path.mkdir(parents=True, exist_ok=True)

        new_file_path = category_path / item.name
        counter = 1

        # Add a numeric suffix until an unused file name is found.
        while new_file_path.exists():
            new_file_path = category_path / f"{item.stem}_{counter}{item.suffix}"
            counter += 1

        return new_file_path

    @staticmethod
    def build_transfer_plan(transfer_mode: TransferMode, source_path: Path) -> TransferPlan:
        """Translate a transfer mode into item discovery behavior and move/copy intent."""
        if transfer_mode == TransferMode.SHALLOW_COPY:
            items = source_path.glob("*")
            use_move = False

        elif transfer_mode == TransferMode.SHALLOW_MOVE:
            items = source_path.glob("*")
            use_move = True

        elif transfer_mode == TransferMode.DEEP_COPY:
            items = source_path.rglob("*")
            use_move = False

        elif transfer_mode == TransferMode.DEEP_MOVE:
            items = source_path.rglob("*")
            use_move = True

        else:
            raise ValueError(f"Invalid transfer mode: {transfer_mode}")

        return TransferPlan(items=items, use_move=use_move)

    @classmethod
    def get_number_of_files(self, source_path: Path, transfer_mode: TransferMode) -> int:
        """Return the number of files selected from a source by the transfer mode."""
        files = self.collect_files(source_path, transfer_mode)
        return len(files)

    @classmethod
    def get_file_category(cls, file_path: Path) -> str:
        """Map a file extension to one of the configured destination categories."""
        suffix = file_path.suffix.lower()

        for category, extensions in cls.FILE_CATEGORIES.items():
            if category == "others":
                continue

            if suffix in extensions:
                return category

        return "others"

    def transfer_single_file(
        self,
        source_file: Path,
        destination_root: Path,
        use_move: bool
        ) -> Path:
        """Copy or move one file into its categorized destination folder."""
        category = self.get_file_category(source_file)
        destination_file = self.create_new_file_name(
            destination_root,
            category,
            source_file
        )

        if use_move:
            shutil.move(source_file, destination_file)
        else:
            shutil.copy2(source_file, destination_file)

        return destination_file
    
    
    
    def search_and_categorize_files(
        self,
        destination_path: Path,
        source_path: Path,
        transfer_mode: TransferMode,
        progress_callback=None
    ) -> TransferResult:
        """Transfer files from one source directory into categorized destination folders."""
        result = TransferResult()

        transfer_plan = self.build_transfer_plan(transfer_mode, source_path)
        files = self.collect_files(source_path, transfer_mode)
        total_files = len(files)
        current_file_count = 0

        if progress_callback:
            progress_callback(0)

        for item in files:
            try:
                # Each file is processed independently so one failure does not
                # stop the rest of the transfer.
                self.transfer_single_file(
                    source_file=item,
                    destination_root=destination_path,
                    use_move=transfer_plan.use_move
                )
                result.add_transferred(item.name)

            except shutil.SameFileError:
                result.add_error(f"Same file error: {item}")
            except shutil.Error as e:
                result.add_error(f"Shutil error for {item}: {e}")
            except Exception as e:
                result.add_error(f"Unexpected error for {item}: {e}")

            current_file_count += 1
            progress = (current_file_count / total_files) * 100 if total_files > 0 else 0

            if progress_callback:
                progress_callback(progress)

        if progress_callback:
            progress_callback(100)

        return result

if __name__ == "__main__":
    print("It seems you need to use me in other class!")
