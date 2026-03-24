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
            print(True if list_address else False)
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
    def check_disk_space_info(source_path:Path, destination_pth:Path) -> None:
        """
        Retrieves free space information for the given path.

        """
        try:
            destination_total, destination_used, destination_free = shutil.disk_usage(destination_pth)
            source_total, source_used, source_free = shutil.disk_usage(source_path)

            # return total, used, free
        except FileNotFoundError:
            raise Exception("Invalid target path.")
        
        if source_total >= destination_free:
            raise Exception
            

        if destination_free < 1024 * 1024 * 100:
            raise NotEnoughSpace("Not enough disk space availible in destination path.")
            
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


    def multi_search_and_categorize_files(self, 
                                        source_path_list:list, 
                                        destination_path:Path, 
                                        progressbar
                                        ) -> None:
        """
        Read address's from the listbox and call search_and_categorize_files method
        on them.
        """
        # list(map(lambda address: self.search_and_categorize_files(destination_path, Path(address), progressbar), source_path_list))
        for address in source_path_list:
            self.search_and_categorize_files(destination_path, 
                                        Path(address), 
                                        progressbar)
        

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
            

    def search_and_categorize_files(
        self, distination_path: str, source_path: str, progress_bar
    ) -> None:
        """
        Search all files in all folders from source path and move them to the distination file path.

        Args:
            distination_path: str
                Distination folder address.
            source_path: str
                Source folder Address.
        """
        
        # Set progress bar settings
        total_files = 0
        for root, _, files in os.walk(source_path):
            total_files += len(files)

        progress_bar["maximum"] = total_files
        current_file_count = 0
        
        for item in (source_path).glob("*"):
            if item.is_dir():
                # print(f"We find a Folder but we do nothing and going another element.")
                continue
            else:
                # Its a file
                for category, extentions in self.FILE_CATEGORIES.items():
                    if item.suffix in extentions:
                        try:
                            
                            destination = self.create_new_file_name(distination_path, category, item)
                            shutil.copy(item, destination)

                        except shutil.SameFileError:
                            raise shutil.SameFileError
                        
                        except shutil.Error as e:
                            # Re-raise the error if it's not a "destination exists" error
                            raise e  # Important to re-raise for unexpected errors

                        current_file_count += 1
                        progress_bar["value"] = current_file_count
                        progress_bar.update()