# Decorator
import shutil
from pathlib import Path

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
    
    def check_path(self,
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
                    raise Exception("Check youe destinatiton path folder!")
            else:
                if (
                    not destination_path.is_absolute()
                    or not source_path.is_absolute()
                ):
                    raise Exception("Check Your Both Address's!") 
        # Check only source input folder path.
        elif roots == "s":
            if not source_path.is_absolute():
                raise "Check Your Source Address!"
        # Check only destination input folder path.
        elif roots == "d":
            if not destination_path.is_absolute():
                raise "Check Your Destination Address!"
    

    def check_disk_space_info(self, destination_pth:Path) -> None:
        """
        Retrieves free space information for the given path.

        """
        try:
            total, used, free = shutil.disk_usage(destination_pth)
            # return total, used, free
        except FileNotFoundError:
            raise "Invalid target path."
            

        if free < 1024 * 1024 * 100:
            raise "Not enough disk space availible."
            
    
    def create_category_directories(self, distination_path: str) -> None:
        """
        Create all empty directories in distination path.

        Args:
            distination_path: str
                Distination folder address.
        """
        for category, _ in self.FILE_CATEGORIES.items():
            (distination_path / category).mkdir(parents=True, exist_ok=True)


    def multi_search_and_categorize_files(self) -> None:
        """
        Read address's fromo the listbox and call search_and_categorize_files method
        on them.
        """
        for index in range(len(self.source_addresses)):
            # self.source_listbox.insert(index, "> " + self.source_addresses[index])

            self.search_and_categorize_files(
                self.distination_path, Path(self.source_addresses[index])
            )
            # self.source_listbox.insert(index, self.source_addresses[index])


    def check_source_name(self, distination_path, category, item):
        counter = 1
        while True:
            if Path.exists(destination):
                new_filename = f"{item.stem}_{counter}{item.suffix}"
                destination = distination_path / category / new_filename
                counter += 1
            else:
                return destination 
            
        
    def search_and_categorize_files(
        self, distination_path: str, source_path: str
    ) -> None:
        """
        Search all files in all folders from source path and move them to the distination file path.

        Args:
            distination_path: str
                Distination folder address.
            source_path: str
                Source folder Address.
        """
        self.label_message_label.configure(
            text="Find and transfering files. Please wait ..."
        )
        total_files = 0
        for root, _, files in os.walk(source_path):
            total_files += len(files)

        self.progress_bar["maximum"] = total_files
        current_file_count = 0
        # def worker():
        for item in (source_path).glob("*"):
            if item.is_dir():
                print(f"We find a Folder but we do nothing and going another element.")
                continue
            else:
                # Its a file
                for category, extentions in self.FILE_CATEGORIES.items():
                    if item.suffix in extentions:
                        try:
                            print(f"transfer {item} ==> distination_path / category ")
                            
                            destination = distination_path / category / item.name
                            destination = self.check_source_name(destination, category, item)
                            shutil.copy(item, destination)

                        except shutil.SameFileError as e:
                            messagebox.showerror(
                                "Error",
                                f"Your source address{source_path} and distination address {distination_path} are the same.",
                            )
                        except shutil.Error as e:
                            print(f"We have {e} error for {item} => {distination_path / category}")
                            # Re-raise the error if it's not a "destination exists" error
                            messagebox.showerror("Error", f"{e}")
                            raise e  # Important to re-raise for unexpected errors

                        current_file_count += 1
                        self.progress_bar["value"] = current_file_count
                        self.progress_bar.update()