import tkinter as tk
import threading
import shutil
from pathlib import Path
from tkinter import messagebox, ttk
from file_organizer_logic import FileOrganizerLogic
from file_organizer_custom_exceptions import (
    BothPathWrong, DestinationPathWrong, SourcePathWrong, NotEnoughSpace
    )


class FileOrganizerGUI:
    """
    Handel GUI and Logic of the File organizer program.
    Detect and organize your files in folders in to six
    Category folders.
    """

    def __init__(self, master_window):

        # Define and initialize basic setting of root or window
        self.master_window = master_window
        self.master_window.title("Auto File Organizer")
        self.master_window.resizable(width=False, height=False)
        # self.master_window.geometry("600x400")

        # Initilize attribiutes
        self.distination_file_name = "file_organizer"
        self.distination_path = Path()
        self.source_path = Path()
        self.source_addresses_list = []

        # Create object from file controller
        self.controller = FileOrganizerLogic()

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
        self.label_message_label = tk.Label(self.frame_left, text="Ready To work!")

        # ListBoxs
        self.source_listbox = tk.Listbox(
            self.frame_right,
        )

        # Entrys
        self.entry_distination_file_address = tk.Entry(self.frame_left)
        self.entry_source_file_address = tk.Entry(self.frame_left)

        # Buttons
        self.button_shallow_copy = tk.Button(self.frame_bottom, command=lambda : self.transfer(mode=0), text="Shallow Copy")
        self.button_deep_copy = tk.Button(self.frame_bottom, command=lambda: self.transfer(mode=2), text="Deep Copy")
        self.button_shallow_cut = tk.Button(self.frame_bottom, command=lambda:self.transfer(mode=1), text="Shallow Cut")
        self.button_deep_cut = tk.Button(self.frame_bottom,command=lambda: self.transfer(mode=3), text="Deep Cut")
        self.button_add_source = tk.Button(
            self.frame_bottom,
            command=self.add_source_address,
            text="Add Source Address",
        )
        self.button_clear_list = tk.Button(self.frame_bottom, command=self.clear_list, text="clear list")

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
        self.label_message_label.grid(
            row=2, column=0, sticky=tk.W + tk.E, padx=10, pady=10
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

        # Button
        self.button_add_source.grid(
            row=0, column=0, sticky=tk.W + tk.E, padx=2, pady=5
        )
        self.button_clear_list.grid(
            row=1, column=0, sticky=tk.W + tk.E, padx=2, pady=5
        )
        self.button_shallow_copy.grid(row=2, column=0, sticky=tk.W + tk.E, padx=2, pady=10)
        self.button_deep_copy.grid(row=3, column=0, sticky=tk.W + tk.E, padx=2, pady=10)
        self.button_shallow_cut.grid(row=4, column=0, sticky=tk.W + tk.E, padx=2, pady=10)
        self.button_deep_cut.grid(row=5, column=0, sticky=tk.W + tk.E, padx=2, pady=10)

        # Progress Bar
        self.progress_bar.grid(
            row=1, column=0, columnspan=2, sticky=tk.W + tk.E, padx=5, pady=5
        )

    def clear_list(self):
        self.source_listbox.delete(0, tk.END)
        self.source_addresses_list = []

    def add_source_address(self):
        """Adds a source address to the source listbox and list."""
        source_path = Path(self.entry_source_file_address.get())
        if source_path:
            self.source_addresses_list.append(source_path)
            self.source_listbox.insert(tk.END, source_path)
            self.label_message_label.configure(text=f"The address is added", fg="blue")
            self.entry_source_file_address.delete(0, tk.END)


    def disable_and_enable(self, mode, *widgets):
        if mode == 0:
            for widget in widgets:
                widget.config(state=tk.DISABLED)
        elif mode == 1:
            for widget in widgets:
                widget.config(state=tk.NORMAL)

    def run_on_ui_thread(self, callback, *args, **kwargs):
        self.master_window.after(0, lambda: callback(*args, **kwargs))

    def update_progress(self, value):
        self.progress_bar["value"] = value

    def safe_update_progress(self, value):
        self.run_on_ui_thread(self.update_progress, value)

    def set_status(self, text, color="black"):
        self.label_message_label.config(text=text, fg=color)

    def transfer(self, mode):
        """
        Start the file creation at the Distination Path, and transfer files from
        Source Path.
        """
        
        # Convert str address to the Path object and keep then in the attributes.
        self.source_path = Path(self.entry_source_file_address.get())
        self.distination_path = Path(self.entry_distination_file_address.get())
        
        try:
            # Check both address fron tk entries.
            self.controller.check_path(source_path=self.source_path, 
                                    destination_path=self.distination_path, 
                                    list_address=self.source_addresses_list, 
                                    roots="b")
            
            # Set the app folder name to the distination adress.
            self.distination_path = self.distination_path / self.distination_file_name

            # Create folders if not exists.
            self.controller.create_category_directories(self.distination_path)
        
            # Check if Distination path have space
            FileOrganizerLogic.check_disk_space(self.source_path, self.distination_path)
        
            # Disable all buttons when app wants to start transfering files.
            self.disable_and_enable(
                0,
                self.button_add_source,
                self.button_deep_copy,
                self.button_deep_cut,
                self.button_shallow_copy,
                self.button_shallow_cut
            )
            self.label_message_label.config(text="Transfering files...", fg="black")
            # self.progress_bar["maximum"] = 100
            # self.progress_bar.start()
            

            # Create a thread
            def worker():
                try:
                    self.run_on_ui_thread(
                        self.set_status,
                        "Transfering Files Please Wait ...",
                        "black"
                    )

                    if self.source_addresses_list:
                        self.controller.multi_search_and_categorize_files(
                            self.source_addresses_list,
                            self.distination_path,
                            mode,
                            self.safe_update_progress
                        )

                        self.run_on_ui_thread(self.source_listbox.delete, 0, tk.END)
                        self.source_addresses_list = []

                    else:
                        self.controller.search_and_categorize_files(
                            self.distination_path,
                            self.source_path,
                            mode,
                            self.safe_update_progress
                        )

                    self.run_on_ui_thread(
                        self.set_status,
                        "Transfering is DONE!",
                        "green"
                    )

                except Exception as e:
                    self.run_on_ui_thread(messagebox.showerror, "Error", str(e))

                finally:
                    self.run_on_ui_thread(
                        self.disable_and_enable,
                        1,
                        self.button_add_source,
                        self.button_deep_copy,
                        self.button_deep_cut,
                        self.button_shallow_copy,
                        self.button_shallow_cut
                    )

                    self.run_on_ui_thread(self.update_progress, 0)

                    msgreport = "\n".join([x for x in FileOrganizerLogic.TRANSFER_LIST])
                    with open(".\\report.txt", "w") as report:
                        report.write(msgreport)

                    self.run_on_ui_thread(messagebox.showinfo, "Files", "Report is created!")
                    
                                

            thread = threading.Thread(target=worker)
            thread.start()

        except BothPathWrong:
            messagebox.showerror("Path Error", "Please check your Both address's. They must be Absoulute Path")
        except DestinationPathWrong:
            messagebox.showerror("Path Error", "Please check your Destination address's.")
        except SourcePathWrong:
            messagebox.showerror("Path Error", "Please check your Source address's.")
        except shutil.SameFileError:
            messagebox.showerror("Error", )
        except FileNotFoundError:
            messagebox.showerror("FileError", "Your address is not exist!")
        except NotEnoughSpace:
            messagebox.showerror("SpaceError", "Your destination file do not have enough space for transfering source data to it.")
        except Exception as e:
            raise e
            

        
