import os
import tkinter as tk
from pathlib import Path
import shutil
from tkinter import messagebox, ttk
import functools
import threading

class FileOrganizerGui:
    """
    Handel GUI and Logic of the File organizer program.
    Detect and organize your files in folders in to six
    Category folders.
    """

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

    def __init__(self, master_window):

        # Define and initialize basic setting of root or window
        self.master_window = master_window
        self.master_window.title("Auto File Organizer")
        self.master_window.resizable(width=False, height=False)
        # self.master_window.geometry("600x400")

        # Initilize attribiutes
        self.distination_file_name = "file_organizer"
        self.distination_path = ""
        self.source_path = ""
        self.source_addresses = []

        # Create the widgets
        self.define_widgets()

        # Put the widgets on the root or window
        self.initilize_positioning_of_widgets()

    def define_widgets(self):
        """
        Define all widgets
        """

        self.frame_top = tk.Frame(self.master_window, width=800, height=100)
        self.frame_mid = tk.Frame(self.master_window, width=800, height=200)
        self.frame_bottom = tk.Frame(self.master_window, width=800)

        self.frame_left = tk.Frame(self.frame_mid, width=400, height=200)
        self.frame_right = tk.Frame(self.frame_mid, width=400, height=200)

        # Lables
        self.label_top_banner = tk.Label(
            self.frame_top,
            text="Auto File Organizer V.1.0.0",
            font=("Tahoma", 15),
        )
        self.label_distination_address = tk.Label(
            self.frame_left, text="distination Address"
        )
        self.label_source_address = tk.Label(self.frame_left, text="Source Address")
        self.label_message_label = tk.Label(self.frame_bottom, text="Ready To work!")

        # ListBox
        self.source_listbox = tk.Listbox(
            self.frame_right,
        )

        # Entry
        self.entry_distination_file_address = tk.Entry(self.frame_left)
        self.entry_source_file_address = tk.Entry(self.frame_left)

        # Button
        self.button_go = tk.Button(self.frame_bottom, command=self.run, text="Transfer")
        self.button_add_source = tk.Button(
            self.frame_bottom,
            command=self.add_source_address,
            text="Add Source Address",
        )

        # Progress Bar
        self.progress_bar = ttk.Progressbar(
            self.frame_right, orient="horizontal", length=300, mode="determinate"
        )

    def initilize_positioning_of_widgets(self):
        """
        Set Position of each widget in the root and frames
        """

        # Frames
        self.frame_top.grid(row=0, column=0, sticky="nsew")
        self.frame_mid.grid(row=1, column=0, sticky="nsew")
        self.frame_left.grid(row=0, column=0, sticky="nsew")
        self.frame_right.grid(row=0, column=1, sticky="nsew")
        self.frame_bottom.grid(row=2, column=0, sticky="nsew")

        # Frame Column Configure
        self.frame_bottom.columnconfigure(0, weight=1)
        self.frame_right.columnconfigure(0, weight=1)

        # Label

        self.label_top_banner.grid(
            row=0, column=2, columnspan=2, sticky="ew", padx=5, pady=5
        )

        self.label_source_address.grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.label_distination_address.grid(
            row=1, column=0, sticky=tk.W, ipady=10, padx=5, pady=10
        )

        # # ListBox
        self.source_listbox.grid(
            row=0, column=0, padx=5, ipadx=50, ipady=50, sticky=tk.W + tk.E
        )

        # Entry
        self.entry_source_file_address.grid(
            row=0, column=1, columnspan=2, sticky=tk.W + tk.E, padx=5, pady=10
        )
        self.entry_distination_file_address.grid(
            row=1, column=1, columnspan=2, sticky=tk.W + tk.E, padx=5, pady=10
        )

        self.label_message_label.grid(
            row=2, column=0, sticky=tk.W + tk.E, padx=10, pady=10
        )

        # Button
        self.button_go.grid(row=1, column=0, sticky=tk.W + tk.E, padx=10, pady=10)
        self.button_add_source.grid(
            row=0, column=0, sticky=tk.W + tk.E, padx=10, pady=10
        )

        # Progress Bar
        self.progress_bar.grid(
            row=1, column=0, columnspan=2, sticky=tk.W + tk.E, padx=5, pady=5
        )

    # Decorator
    def check_path(roots="b"):
        """
        This decorator check address's come from two entry.
        Address must be absolute path.

        Args:
            roots: str
                b: Check both tk entry
                s: Check source tk entry
                d: Check distination tk entry
        """

        def check_both_address(f):
            @functools.wraps(f)
            def wrapper(self):
                self.distination_path = Path(self.entry_distination_file_address.get())
                self.source_path = Path(self.entry_source_file_address.get())

                if roots == "b":
                    if self.source_addresses:
                        if not self.distination_path.is_absolute():
                            self.label_message_label.configure(
                                text="Check Your Distination Address's!"
                            )
                        else:
                            result = f(self)
                            return result
                    else:
                        if (
                            not self.distination_path.is_absolute()
                            or not self.source_path.is_absolute()
                        ):
                            self.label_message_label.configure(
                                text="Check Your Both Address's!"
                            )
                        else:
                            result = f(self)
                            return result
                elif roots == "s":
                    if not self.source_path.is_absolute():
                        self.label_message_label.configure(
                            text="Check Your Source Address!"
                        )
                    else:
                        result = f(self)
                        return result
                elif roots == "d":
                    if not self.distination_path.is_absolute():
                        self.label_message_label.configure(
                            text="Check Your Destination Address!"
                        )
                    else:
                        result = f(self)
                        return result

            return wrapper

        return check_both_address

    # Decorator
    def check_disk_space_info(f):
        """
        Retrieves free space information for the given path.

        """

        @functools.wraps(f)
        def wrapper(self, *args, **kwargs):

            try:
                total, used, free = shutil.disk_usage(args[0])
                # return total, used, free
            except FileNotFoundError:
                messagebox.showerror("Error", "Invalid target path.")
                return

            if free < 0:
                messagebox.showerror("Error", "Not enough disk space availible.")
                return
            else:
                result = f(self, *args, **kwargs)
                return result

        return wrapper

    def create_category_directories(self, distination_path: str) -> None:
        """
        Create all empty directories in distination path.

        Args:
            distination_path: str
                Distination folder address.
        """
        self.label_message_label.configure(text="Creating Folders Please Wait ...")
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

    @check_disk_space_info
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
                            print(f"Tring to transfer {item} ==> distination_path / category ")
                            shutil.copy(item, distination_path / category)
                        except shutil.SameFileError as e:
                            print("We have shutil sameFileError")
                            messagebox.showerror(
                                "Error",
                                f"Your source address{source_path} and distination address {distination_path} are the same.",
                            )
                        except shutil.Error as e:
                            print(f"We have {e} error for {item} => {distination_path / category}")
                            if "already exists" in str(e):
                                new_filename = (
                                    item.name.rsplit(".", 1)[0] + "_1." + item.suffix
                                )
                                print(f"new name {new_filename}")
                                new_destination = (
                                    distination_path / category / new_filename
                                )
                                print(f"tring transfer {item} to new address: {new_destination}")
                                shutil.copy(item, new_destination)
                                self.label_message_label.configure(
                                    text=f"Renamed file to {new_filename} and moved to {distination_path}"
                                )
                                print(
                                    f"Renamed file to {new_filename} and moved to {distination_path}"
                                )
                            else:
                                # Re-raise the error if it's not a "destination exists" error
                                messagebox.showerror("Error", f"{e}")
                                raise e  # Important to re-raise for unexpected errors

                        current_file_count += 1
                        self.progress_bar["value"] = current_file_count
                        self.progress_bar.update()

    @check_path(roots="s")
    def add_source_address(self):
        """Adds a source address to the list."""
        address = self.entry_source_file_address.get()
        if address:
            self.source_addresses.append(address)
            self.source_listbox.insert(tk.END, address)
            self.label_message_label.configure(text=f"The address is added")
            self.entry_source_file_address.delete(0, tk.END)

    @check_path(roots="b")
    def run(self):
        """
        Start the file creation at the Distination Path, and transfer files from
        Source Path.
        """
        self.distination_path = self.distination_path / self.distination_file_name
        self.create_category_directories(self.distination_path)

        self.button_go.config(state=tk.DISABLED)
        self.button_add_source.config(state=tk.DISABLED)
        self.label_message_label.config(text="Transfering files...")
        self.progress_bar["maximum"] = 100
        self.progress_bar.start()

        def worker():
            try:
                if self.source_listbox:
                    self.multi_search_and_categorize_files()
                    self.label_message_label.config(text="Transfering is DONE!")
                else:
                    self.search_and_categorize_files(
                        self.distination_path, self.source_path
                    )
                    self.label_message_label.config(text="Transfering is DONE!")
            except Exception as e:

                messagebox.showerror("Error", str(e))
                raise e
            finally:
                self.button_go.config(state=tk.NORMAL)
                self.button_add_source.config(state=tk.NORMAL)
                self.progress_bar.stop()
                self.progress_bar["value"] = 0

        thread = threading.Thread(target=worker)
        thread.start()

class FileOrganizerController:
    def __init__(self, front_obj):
        self.fron = front_obj