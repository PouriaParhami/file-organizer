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
        return Path(path_value).expanduser().resolve()

    @classmethod
    def validate_source_path(cls, source_path) -> Path:
        path = cls.normalize_path(source_path)

        if not path.exists():
            raise InvalidSourcePath(f"Source path does not exist: {path}")

        if not path.is_dir():
            raise InvalidSourcePath(f"Source path is not a directory: {path}")

        return path

    @classmethod
    def validate_destination_path(cls, destination_path) -> Path:
        path = cls.normalize_path(destination_path)

        if path.exists() and not path.is_dir():
            raise InvalidDestinationPath(f"Destination path is not a directory: {path}")

        return path

    @staticmethod
    def validate_source_destination_relation(
        source_path: Path, destination_path: Path
    ) -> None:
        if source_path == destination_path:
            raise PathError("Source and destination cannot be the same.")

        if destination_path in source_path.parents:
            raise PathError("Destination cannot be a parent of source.")

        if source_path in destination_path.parents:
            raise PathError("Destination cannot be inside source.")

    @classmethod
    def check_path(cls, source_path, destination_path):
        valid_source = cls.validate_source_path(source_path)
        valid_destination = cls.validate_destination_path(destination_path)
        cls.validate_source_destination_relation(valid_source, valid_destination)

        return valid_source, valid_destination


    def collect_files_from_multiple_sources(
        self,
        source_paths: list,
        transfer_mode: TransferMode
    ) -> list[Path]:
        all_files = []

        for source in source_paths:
            source_path = Path(source)
            all_files.extend(self.collect_files(source_path, transfer_mode))

        return all_files
        
    def get_total_size_of_files(self, source_path: Path, transfer_mode: TransferMode) -> int:
        files = self.collect_files(source_path, transfer_mode)
        return self.get_total_size_of_files_from_list(files)

    @classmethod
    def get_total_size_of_multiple_sources(
        cls, source_paths: list, transfer_mode: TransferMode
    ) -> int:
        total_size = 0

        for source in source_paths:
            total_size += cls.get_total_size_of_files(Path(source), transfer_mode)

        return total_size

    @classmethod
    def are_on_same_drive(cls, source_path: Path, destination_path: Path) -> bool:
        return source_path.drive.lower() == destination_path.drive.lower()

    @staticmethod
    def get_folder_size(folder_path: Path) -> int:
        """
        Calcuate total size of a path (it suppose to be a foler.)

        Args:
            folder_path: Path obj
                Address of your folder

        Return:
            total_size: int
                Total size of folder
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
        transfer_plan = self.build_transfer_plan(transfer_mode, source_path)
        use_move = transfer_plan.use_move

        if use_move and self.are_on_same_drive(source_path, destination_path):
            return

        files = self.collect_files(source_path, transfer_mode)
        total_size = self.get_total_size_of_files_from_list(files)
        free_space = shutil.disk_usage(destination_path).free

        if total_size > free_space:
            raise InsufficientSpaceError("There is not enough free space in destination.")

    @classmethod
    def check_disk_space_for_multiple_sources(
        cls, source_paths: list, destination_path: Path, transfer_mode: TransferMode
    ) -> None:
        needs_space_check = False

        for source in source_paths:
            source_path = Path(source)
            transfer_plan = cls.build_transfer_plan(transfer_mode, source_path)
            items = transfer_plan.items
            use_move = transfer_plan.use_move

            if not use_move:
                needs_space_check = True
                break

            if not cls.are_on_same_drive(source_path, destination_path):
                needs_space_check = True
                break

        if not needs_space_check:
            return

        total_size = cls.get_total_size_of_multiple_sources(source_paths, transfer_mode)
        free_space = shutil.disk_usage(destination_path).free

        if total_size > free_space:
            raise InsufficientSpaceError(
                "There is not enough free space in destination."
            )

    @classmethod
    def create_category_directories(cls, destination_path: str) -> None:
        """
        Create all empty directories in distination path.

        Args:
            destination_path: str
                Distination folder address.
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
        category_path = destination_path / category
        category_path.mkdir(parents=True, exist_ok=True)

        new_file_path = category_path / item.name
        counter = 1

        while new_file_path.exists():
            new_file_path = category_path / f"{item.stem}_{counter}{item.suffix}"
            counter += 1

        return new_file_path

    @staticmethod
    def build_transfer_plan(transfer_mode: TransferMode, source_path: Path) -> TransferPlan:
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
        files = self.collect_files(source_path, transfer_mode)
        return len(files)

    def get_file_category(cls, file_path: Path) -> str:
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
    
    def collect_files(self, source_path: Path, transfer_mode: TransferMode) -> list[Path]:
        transfer_plan = self.build_transfer_plan(transfer_mode, source_path)
        files = []

        for item in transfer_plan.items:
            if item.is_file():
                files.append(item)

        return files
    
    def search_and_categorize_files(
        self,
        destination_path: Path,
        source_path: Path,
        transfer_mode: TransferMode,
        progress_callback=None
    ) -> TransferResult:
        result = TransferResult()

        transfer_plan = self.build_transfer_plan(transfer_mode, source_path)
        files = self.collect_files(source_path, transfer_mode)
        total_files = len(files)
        current_file_count = 0

        if progress_callback:
            progress_callback(0)

        for item in files:
            try:
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
