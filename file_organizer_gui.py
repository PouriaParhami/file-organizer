import tkinter as tk
import threading
import shutil
from pathlib import Path
from tkinter import messagebox, ttk
from file_organizer_logic import FileOrganizerLogic
from file_organizer_custom_exceptions import (
        InvalidDestinationPath,
        InvalidSourcePath,
        InsufficientSpaceError,
            PathError,
        FileOrganizerError,
)
from transfer_mode import TransferMode
from report_writer import ReportWriter


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

        self.last_result = None

        # initialize attribiutes
        self.distination_file_name = "file_organizer"
        self.distination_path = Path()
        self.source_path = Path()
        self.source_addresses_list = []

        # Create object from file controller
        self.controller = FileOrganizerLogic()

        # Create the widgets
        self.define_widgets()

        # Put the widgets on the root or window
        self.initialize_positioning_of_widgets()

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
        self.entry_destination_address = tk.Entry(self.frame_left)
        self.entry_source_file_address = tk.Entry(self.frame_left)

        # Buttons
        self.button_shallow_copy = tk.Button(
            self.frame_bottom,
            command=lambda: self.transfer(mode=TransferMode.SHALLOW_COPY),
            text="Shallow Copy",
        )
        self.button_deep_copy = tk.Button(
            self.frame_bottom,
            command=lambda: self.transfer(mode=TransferMode.DEEP_COPY),
            text="Deep Copy",
        )
        self.button_shallow_cut = tk.Button(
            self.frame_bottom,
            command=lambda: self.transfer(mode=TransferMode.SHALLOW_MOVE),
            text="Shallow Cut",
        )
        self.button_deep_cut = tk.Button(
            self.frame_bottom,
            command=lambda: self.transfer(mode=TransferMode.DEEP_MOVE),
            text="Deep Cut",
        )
        self.button_add_source = tk.Button(
            self.frame_bottom,
            command=self.add_source_address,
            text="Add Source Address",
        )
        self.button_clear_list = tk.Button(
            self.frame_bottom, command=self.clear_list, text="clear list"
        )

        # Progress Bar
        self.progress_bar = ttk.Progressbar(
            self.frame_right, orient="horizontal", length=300, mode="determinate"
        )

    def initialize_positioning_of_widgets(self):
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
        self.entry_destination_address.grid(
            row=1, column=1, columnspan=2, sticky=tk.W + tk.E, padx=5, pady=10
        )

        # Button
        self.button_add_source.grid(row=0, column=0, sticky=tk.W + tk.E, padx=2, pady=5)
        self.button_clear_list.grid(row=1, column=0, sticky=tk.W + tk.E, padx=2, pady=5)
        self.button_shallow_copy.grid(
            row=2, column=0, sticky=tk.W + tk.E, padx=2, pady=10
        )
        self.button_deep_copy.grid(row=3, column=0, sticky=tk.W + tk.E, padx=2, pady=10)
        self.button_shallow_cut.grid(
            row=4, column=0, sticky=tk.W + tk.E, padx=2, pady=10
        )
        self.button_deep_cut.grid(row=5, column=0, sticky=tk.W + tk.E, padx=2, pady=10)

        # Progress Bar
        self.progress_bar.grid(
            row=1, column=0, columnspan=2, sticky=tk.W + tk.E, padx=5, pady=5
        )

    def handle_gui_error(self, error: Exception):
        
        self.set_status("Operation failed.", "red")
        
        if isinstance(error, InvalidSourcePath):
            messagebox.showerror("Invalid Source", str(error))

        elif isinstance(error, InvalidDestinationPath):
            messagebox.showerror("Invalid Destination", str(error))

        elif isinstance(error, InsufficientSpaceError):
            messagebox.showerror("Insufficient Disk Space", str(error))

        elif isinstance(error, PathError):
            messagebox.showerror("Path Error", str(error))

        elif isinstance(error, FileOrganizerError):
            messagebox.showerror("Application Error", str(error))

        else:
            messagebox.showerror("Unexpected Error", f"An unexpected error occurred:\n{error}")
    
    def clear_list(self):
        self.source_listbox.delete(0, tk.END)
        self.source_addresses_list = []

    def get_report_path(self):
        return Path(".\\report.txt")

    def add_source_address(self):
        raw_value = self.entry_source_file_address.get().strip()

        if not raw_value:
            messagebox.showerror("Error", "Source path cannot be empty.")
            return

        try:
            source_path = FileOrganizerLogic.validate_source_path(raw_value)
        except Exception as e:
            self.handle_gui_error(e)
            return

        source_path_str = str(source_path)

        if source_path_str in self.source_addresses_list:
            messagebox.showinfo("Info", "This source path is already in the list.")
            return

        self.source_addresses_list.append(source_path_str)
        self.source_listbox.insert(tk.END, source_path_str)
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

    def read_paths_from_inputs(self):
        source_value = self.entry_source_file_address.get().strip()
        destination_value = self.entry_destination_address.get().strip()
        return source_value, destination_value
    
    def has_multiple_sources(self) -> bool:
        return len(self.source_addresses_list) > 0
    
    def prepare_multi_source_transfer(self, transfer_mode):
        self.destination_path = FileOrganizerLogic.validate_destination_path(
            self.destination_path
        )

        for address in self.source_addresses_list:
            source_path = FileOrganizerLogic.validate_source_path(address)
            FileOrganizerLogic.validate_source_destination_relation(
                source_path,
                self.destination_path
            )

        self.controller.check_disk_space_for_multiple_sources(
            self.source_addresses_list,
            self.destination_path,
            transfer_mode
        )
        
    def prepare_transfer(self, transfer_mode):
        if self.has_multiple_sources():
            self.prepare_multi_source_transfer(transfer_mode)
        else:
            self.prepare_single_source_transfer(transfer_mode)
            
    def set_action_buttons_state(self, enabled: bool):
        widgets = (
            self.button_add_source,
            self.button_deep_copy,
            self.button_deep_cut,
            self.button_shallow_copy,
            self.button_shallow_cut,
        )

        state_mode = 1 if enabled else 0
        self.disable_and_enable(state_mode, *widgets)
    
    def start_transfer_thread(self, transfer_mode):
        thread = threading.Thread(
            target=lambda: self.worker(transfer_mode),
            daemon=True
        )
        thread.start()
    
    def prepare_single_source_transfer(self, transfer_mode):
        self.source_path, self.destination_path = FileOrganizerLogic.check_path(
            self.source_path,
            self.destination_path
        )

        self.controller.check_disk_space(
            self.source_path,
            self.destination_path,
            transfer_mode
        )
    
    def worker(self, transfer_mode):
        try:
            self.run_on_ui_thread(
                self.set_status,
                "Transfering Files Please Wait ...",
                "black"
            )

            if self.has_multiple_sources():
                self.last_result = self.controller.multi_search_and_categorize_files(
                    self.source_addresses_list,
                    self.destination_path,
                    transfer_mode,
                    self.safe_update_progress
                )

                self.run_on_ui_thread(self.source_listbox.delete, 0, tk.END)
                self.source_addresses_list = []

            else:
                self.last_result = self.controller.search_and_categorize_files(
                    self.destination_path,
                    self.source_path,
                    transfer_mode,
                    self.safe_update_progress
                )

            self.run_on_ui_thread(
                self.set_status,
                "Transfering is DONE!",
                "green"
            )

        except Exception as e:
            self.run_on_ui_thread(self.handle_gui_error, e)

        finally:
            self.run_on_ui_thread(self.set_action_buttons_state, True)
            self.run_on_ui_thread(self.update_progress, 0)

            if self.last_result is not None:
                try:
                    report_path = self.get_report_path()
                    ReportWriter.write_text_report(self.last_result, report_path)
                    self.run_on_ui_thread(
                        messagebox.showinfo,
                        "Report",
                        f"Report created successfully:\n{report_path}"
                    )
                except Exception as e:
                    self.run_on_ui_thread(
                        messagebox.showerror,
                        "Report Error",
                        str(e)
                    )
    
    def transfer(self, mode: TransferMode):
        self.last_result = None

        source_value, destination_value = self.read_paths_from_inputs()
        self.source_path = source_value
        self.destination_path = destination_value

        try:
            self.prepare_transfer(mode)
        except Exception as e:
            self.handle_gui_error(e)
            return

        self.set_action_buttons_state(False)
        self.start_transfer_thread(mode)
