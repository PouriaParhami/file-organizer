import os
import shutil
from pathlib import Path
from file_organizer_custom_exceptions import (
    BothPathWrong, DestinationPathWrong, SourcePathWrong, NotEnoughSpace
    )
from transfer_mode import TransferMode

class FileOrganizerLogic:

    FILE_CATEGORIES = {
        "images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".svg", ".webp"],
        "documents": [
            ".pdf",
            ".doc",
            ".docx",
            ".txt",
            ".xls",
            ".xlsx",
            ".ppt",
            ".pptx",
            ".csv",
        ],
        "videos": [".mp4", ".mkv", ".avi", ".mov", ".wmv"],
        "audio": [".mp3", ".wav", ".aac", ".flac", ".ogg", ".m4a"],
        "archives": [".zip", ".rar", ".tar", ".gz", ".7z", ".iso"],
        "programs": [".exe"],
        "folders": [],
        }
    TRANSFER_LIST = []

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
            raise InvalidDistinationPath(
                f"Destination path is not a directory: {path}"
            )

        return path
    
    @staticmethod
    def validate_source_destination_relation(source_path: Path, destination_path: Path) -> None:
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
    
    @staticmethod
    def get_total_size_of_files(source_path: Path, transfering_mode: TransferMode) -> int:
        items, _ = FileOrganizerLogic.transfer_set_setting(transfering_mode, source_path)
        total_size = 0

        for item in items:
            if item.is_file():
                try:
                    total_size += item.stat().st_size
                except OSError:
                    continue

        return total_size

    @classmethod
    def get_total_size_of_multiple_sources(cls, source_paths: list, transfering_mode: TransferMode) -> int:
        total_size = 0

        for source in source_paths:
            total_size += cls.get_total_size_of_files(Path(source), transfering_mode)

        return total_size

    @classmethod
    def are_on_same_drive(cls, source_path: Path, destination_path: Path) -> bool:
        return source_path.drive.lower() == destination_path.drive.lower()


    @staticmethod
    def get_folder_size(folder_path:Path) -> int:
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
        cls,
        source_path: Path,
        destination_path: Path,
        transfering_mode: TransferMode
    ) -> None:
        _, use_move = cls.transfer_set_setting(transfering_mode, source_path)

        if use_move and cls.are_on_same_drive(source_path, destination_path):
            return

        total_size = cls.get_total_size_of_files(source_path, transfering_mode)
        free_space = shutil.disk_usage(destination_path).free

        if total_size > free_space:
            raise InsufficientSpaceError("There is not enough free space in destination.")

    @classmethod
    def check_disk_space_for_multiple_sources(
        cls,
        source_paths: list,
        destination_path: Path,
        transfering_mode: TransferMode
    ) -> None:
        needs_space_check = False

        for source in source_paths:
            source_path = Path(source)
            _, use_move = cls.transfer_set_setting(transfering_mode, source_path)

            if not use_move:
                needs_space_check = True
                break

            if not cls.are_on_same_drive(source_path, destination_path):
                needs_space_check = True
                break

        if not needs_space_check:
            return

        total_size = cls.get_total_size_of_multiple_sources(source_paths, transfering_mode)
        free_space = shutil.disk_usage(destination_path).free

        if total_size > free_space:
            raise InsufficientSpaceError("There is not enough free space in destination.")

    @classmethod
    def create_category_directories(cls, distination_path: str) -> None:
        """
        Create all empty directories in distination path.

        Args:
            distination_path: str
                Distination folder address.
        """
        for category, _ in cls.FILE_CATEGORIES.items():
            (distination_path / category).mkdir(parents=True, exist_ok=True)


    def multi_search_and_categorize_files(
            self,
            source_path_list: list,
            destination_path: Path,
            mode: TransferMode,
            progress_callback=None
        ) -> None:
        for address in source_path_list:
            self.search_and_categorize_files(
                destination_path,
                Path(address),
                mode,
                progress_callback
            )
        

    @staticmethod
    def create_new_file_name(distination_path, category, item):
        """
        Create new file name by adding number.
        """
        counter = 1
        destination_file = distination_path / category / item.name
        while True:
            if Path.exists(destination_file):
                new_filename = f"{item.stem}_{counter}{item.suffix}"
                destination_file = distination_path / category / new_filename
                counter += 1
            else:
                return destination_file 
    
    @staticmethod
    def transfer_set_setting(transfer_mode: TransferMode, address: Path) -> tuple:
        """
        Decide whether files should be copied or moved,
        and whether search should be shallow or deep.
        """

        if transfer_mode == TransferMode.SHALLOW_COPY:
            items = address.glob("*")
            use_move = False

        elif transfer_mode == TransferMode.SHALLOW_MOVE:
            items = address.glob("*")
            use_move = True

        elif transfer_mode == TransferMode.DEEP_COPY:
            items = address.rglob("*")
            use_move = False

        elif transfer_mode == TransferMode.DEEP_MOVE:
            items = address.rglob("*")
            use_move = True

        else:
            raise ValueError(f"Invalid transfer mode: {transfer_mode}")

        return items, use_move

    @classmethod
    def get_number_of_files(cls, address, transfer_mode):
        """
        Return the total files in the path

        Args: 
            address: Path
                Address of the folder you want to check.
        Returns:
            total_fiels: int
                number of files into the address you pass as the argument.
        """
        items, _ = cls.transfer_set_setting(transfer_mode, address)
        total_files = 0
        for item in items:
            if item.is_file():
                total_files += 1

        return total_files


    def search_and_categorize_files(
            self,
            distination_path: Path,
            source_path: Path,
            transfering_mode: TransferMode,
            progress_callback=None
        ) -> None:
        """
        Search all files in source path and move/copy them to categorized folders.
        """

        items, use_move = self.transfer_set_setting(transfering_mode, source_path)
        total_files = self.get_number_of_files(source_path, transfering_mode)
        current_file_count = 0

        if progress_callback:
            progress_callback(0)

        for item in items:
            if item.is_dir():
                continue

            for category, extentions in self.FILE_CATEGORIES.items():
                if item.suffix in extentions:
                    try:
                        destination = self.create_new_file_name(distination_path, category, item)

                        if use_move:
                            shutil.move(item, destination)
                        else:
                            shutil.copy(item, destination)

                        print(item)
                        self.TRANSFER_LIST.append(item.name)

                        current_file_count += 1
                        progress = (current_file_count / total_files) * 100 if total_files > 0 else 0

                        if progress_callback:
                            progress_callback(progress)

                    except shutil.SameFileError:
                        raise shutil.SameFileError

                    except shutil.Error as e:
                        raise e

        if progress_callback:
            progress_callback(100)
                

if __name__ == "__main__":
    print("It seems you need to use me in other class!")