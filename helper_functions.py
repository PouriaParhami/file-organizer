# Import Libes
from pathlib import Path
import shutil
from tkinter import Tk


# Declare Target address for search
TARGET_BASE_ADDRESS = Path(r"C:\Users\User")
PC_DOWNLOAD_FOLDER = "Downloads"

# Declare folder addresses for transport
WAREHOUSE_BASE_ADDRESS = Path("D:\\")
WAREHOUSE_ADDRESS = WAREHOUSE_BASE_ADDRESS / "temp"

# Declare categories and extensions
FILE_CATEGORIES = {

    "images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".svg", ".webp"],
    "documents": [".pdf", ".doc", ".docx", ".txt", ".xls", ".xlsx", ".ppt", ".pptx", "csv"],
    "videos": [".mp4", ".mkv", ".avi", ".mov", ".wmv"],
    "audio": [".mp3", ".wav", ".aac", ".flac", ".ogg"],
    "archives": [".zip", ".rar", ".tar", ".gz", ".7z", "iso"],
    "programs": [".exe"]    

}

def create_category_directories() -> None:
    for category, _ in FILE_CATEGORIES.items():
        (WAREHOUSE_ADDRESS / category).mkdir(parents=True, exist_ok=True)

def search_and_categorize_files():
    print("Find and transfering files. Please wait ...")
    for file in (TARGET_BASE_ADDRESS / PC_DOWNLOAD_FOLDER).rglob("*"):
        for category, extentions in FILE_CATEGORIES.items():
            if file.suffix in extentions:
                try:
                    shutil.move(file, WAREHOUSE_ADDRESS / category)
                except shutil.SameFileError:
                    pass


def main():
    create_category_directories()
    search_and_categorize_files()




if __name__ == "__main__":
    print("Should use my as a moudle!")