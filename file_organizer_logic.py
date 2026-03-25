import os
import shutil
from pathlib import Path
from file_organizer_custom_exceptions import (
    BothPathWrong, DestinationPathWrong, SourcePathWrong, NotEnoughSpace
    )

# TODO change the static methods name
# TODO handel static method exception in one uper level
# TODO is shutil can raise error if the file in source and distination paht have same name?
# TODO Create deep copy and deep move logic

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
    def check_path(
            source_path:Path, 
            destination_path:Path, 
            list_address:list=None, 
            roots:str="b"
            ) -> None:
        """
        This decorator check address's come from two entry.
        Address must be absolute path.

        Args:
            source_path: Path obj
                source folder path

            destination_path: Path obj
                destination folder path

            list_address: list
                A list contain source folders path

            roots: str
                b: Check both tk entry
                s: Check source tk entry
                d: Check distination tk entry
        Return:
            None
            
        """
        # Check both path from tk entries.
        if roots == "b":
            if list_address:
                if not destination_path.is_absolute():
                    raise DestinationPathWrong
            else:
                if (
                    not destination_path.is_absolute()
                    or not source_path.is_absolute()
                ):
                    raise BothPathWrong
        # Check only source input folder path.
        elif roots == "s":
            if not source_path.is_absolute():
                raise SourcePathWrong
        # Check only destination input folder path.
        elif roots == "d":
            if not destination_path.is_absolute():
                raise DestinationPathWrong
    
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
    def check_disk_space(cls, source_path:Path, destination_pth:Path) -> None:
        """
        Retrieves free space information for the given path.

        """
        try:
            destination_total, destination_used, destination_free = shutil.disk_usage(destination_pth)
            source_total_size = cls.get_folder_size(source_path)
            
        except FileNotFoundError as e:
            raise FileNotFoundError
        
        if source_total_size >= destination_free:
            raise NotEnoughSpace
            

        # if destination_free < 1024 * 1024 * 100:
        #     raise NotEnoughSpace("Not enough disk space availible in destination path.")
            
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
            mode: int,
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
    def transfer_set_setting(transfer_mode:int, address: Path) -> tuple:
        """
        Set useing move or copy and see the currend dir or dir + all sub dirs

        Args:
            transfer_mode: int
                0: shallow copy (use copy and only see the dir root)
                1: shallow cut (use move and only see the dir rooe)
                2: deep copy (use copy and see root and all sub dirs)
                3: deep cut (use move and see root and all sub dirs)
        
        Returns:
            items, use_move as tuple
        """
        # Shallow Copy
        if transfer_mode == 0:
            items = (address).glob("*")
            use_move = False
        # Shallow Cut
        elif transfer_mode == 1:
            items = (address).glob("*")
            use_move = True
        # Deep Copy
        elif transfer_mode == 2:
            items = (address).rglob("*")
            use_move = False
        # Deep Cut
        elif transfer_mode == 3:
            items = (address).rglob("*")
            use_move = True
        else:
            raise ValueError("Invalid transfering_mode")
        
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
            transfering_mode: int,
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