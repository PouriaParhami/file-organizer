# Auto File Organizer

Auto File Organizer is a small desktop utility built to solve a very common problem: a crowded download drive filled with mixed file types. The project scans one or more source folders, detects files by extension, and places them into organized category folders such as `images`, `documents`, `audio`, `video`, `archives`, `scripts`, and `others`.

The application currently provides a Tkinter-based GUI and supports both copy and move operations in shallow and deep modes.

## Story

My download drive became crowded with all kinds of files, which made it hard to find anything quickly. To solve that problem, I wrote this project as a simple file organizer that automatically sorts files into category-based folders.

## Features

- Organize files into category folders based on file extension
- Support for single-source and multi-source transfers
- Copy or move files
- Shallow mode for top-level files only
- Deep mode for recursive file discovery
- Automatic duplicate filename handling
- Destination path and disk space validation
- Progress bar and status updates in the GUI
- Transfer report generation in `report.txt`

## Libraries

This project currently uses only Python standard library modules:

- `tkinter` and `tkinter.ttk` for the desktop GUI
- `threading` for background file transfer
- `pathlib` for path handling
- `shutil` for copy, move, and disk usage operations
- `os` for directory traversal and size calculation
- `enum` for transfer mode definitions
- `dataclasses` for lightweight data containers
- `typing` for type annotations

No third-party package is required.

## Installation

### Requirements

- Python 3.10 or newer recommended
- Windows environment recommended because the current workflow and path handling were clearly developed for Windows-style paths

### Setup

```powershell
git clone <your-repository-url>
cd file_organizer
python main.py
```

If `python` is not available on your system path, use your installed Python launcher instead:

```powershell
py main.py
```

## How It Works

1. Enter a source folder in the GUI.
2. Enter a destination folder.
3. Optionally add multiple source folders to the list.
4. Choose one of the available transfer modes:
   - `Shallow Copy`
   - `Deep Copy`
   - `Shallow Cut`
   - `Deep Cut`
5. The program validates paths, checks disk space when needed, transfers files, and writes a report.

## Transfer Modes

- `SHALLOW_COPY`: Copy only files located directly inside the source folder
- `SHALLOW_MOVE`: Move only files located directly inside the source folder
- `DEEP_COPY`: Copy files from the source folder and all nested subfolders
- `DEEP_MOVE`: Move files from the source folder and all nested subfolders

## Output Categories

Files are organized into these folders under the destination path:

- `images`
- `documents`
- `audio`
- `video`
- `archives`
- `scripts`
- `others`

## Project Structure

```text
file_organizer/
|-- main.py
|-- file_organizer_gui.py
|-- file_organizer_logic.py
|-- file_organizer_custom_exceptions.py
|-- transfer_mode.py
|-- transfer_plan.py
|-- transfer_result.py
|-- report_writer.py
|-- helper_functions.py
|-- report.txt
```

## Technical Description

### Part 1: Classes and Their Responsibilities

#### `FileOrganizerGUI`
Defined in `file_organizer_gui.py`.

This class manages the Tkinter user interface and coordinates user actions with the business logic layer. It collects input paths, starts transfers on a background thread, updates progress safely on the UI thread, and displays success or error messages.

#### `FileOrganizerLogic`
Defined in `file_organizer_logic.py`.

This is the core service class of the application. It validates paths, builds transfer plans, calculates file sizes, checks disk space, determines file categories, performs copy or move operations, and returns transfer results.

#### `ReportWriter`
Defined in `report_writer.py`.

This utility class converts a `TransferResult` into a plain-text report and writes it to disk.

#### `TransferResult`
Defined in `transfer_result.py`.

This dataclass stores the outcome of a transfer operation, including transferred files, skipped files, and errors.

#### `TransferPlan`
Defined in `transfer_plan.py`.

This dataclass represents the result of transfer planning. It stores the iterable collection of discovered items and a boolean flag indicating whether the operation is a move.

#### `TransferMode`
Defined in `transfer_mode.py`.

This enum defines the four supported transfer strategies: shallow copy, shallow move, deep copy, and deep move.

#### `FileOrganizerError` and custom exceptions
Defined in `file_organizer_custom_exceptions.py`.

These classes define application-specific exceptions used to communicate validation and runtime errors more clearly:

- `FileOrganizerError`
- `InvalidSourcePath`
- `InvalidDestinationPath`
- `PathError`
- `InsufficientSpaceError`

### Part 2: Methods of Each Class

#### `FileOrganizerGUI` methods

- `__init__(self, master_window)`: Initializes the main window, default state, logic controller, and UI widgets.
- `define_widgets(self)`: Creates all Tkinter widgets used by the application.
- `initialize_positioning_of_widgets(self)`: Places frames, labels, entries, buttons, listbox, and progress bar using grid layout.
- `handle_gui_error(self, error)`: Maps known application exceptions to user-friendly message boxes.
- `clear_list(self)`: Clears the multi-source listbox and the in-memory source list.
- `get_report_path(self)`: Returns the path used for the generated text report.
- `add_source_address(self)`: Validates and adds a source folder to the list of transfer sources.
- `disable_and_enable(self, mode, *widgets)`: Enables or disables a group of widgets.
- `run_on_ui_thread(self, callback, *args, **kwargs)`: Schedules a callback to run safely on the Tkinter UI thread.
- `update_progress(self, value)`: Updates the progress bar value.
- `safe_update_progress(self, value)`: Routes progress updates through the UI thread.
- `set_status(self, text, color="black")`: Updates the status label text and color.
- `read_paths_from_inputs(self)`: Reads the current source and destination text entry values.
- `has_multiple_sources(self)`: Returns `True` when the user has added source folders to the multi-source list.
- `prepare_multi_source_transfer(self, transfer_mode)`: Validates destination and source relationships for multi-source transfers and checks disk space.
- `prepare_transfer(self, transfer_mode)`: Selects the correct validation flow for single-source or multi-source transfers.
- `set_action_buttons_state(self, enabled)`: Enables or disables transfer action buttons during work.
- `start_transfer_thread(self, transfer_mode)`: Starts the background worker thread.
- `prepare_single_source_transfer(self, transfer_mode)`: Validates single-source inputs and checks disk space.
- `worker(self, transfer_mode)`: Runs the file transfer operation, updates UI status, clears processed sources, and writes the report.
- `transfer(self, mode)`: Entry point for a button-triggered transfer request.

#### `FileOrganizerLogic` methods

- `normalize_path(path_value)`: Converts an input path into a resolved `Path` object.
- `collect_files(cls, source_path, transfer_mode)`: Builds a transfer plan and returns only file items from that plan.
- `validate_source_path(cls, source_path)`: Ensures the source exists and is a directory.
- `validate_destination_path(cls, destination_path)`: Ensures the destination is valid or can be created as a directory.
- `validate_source_destination_relation(source_path, destination_path)`: Prevents invalid path relationships such as identical source and destination, destination inside source, or destination as a parent of source.
- `check_path(cls, source_path, destination_path)`: Validates both paths and their relationship together.
- `get_total_size_of_files_from_list(files)`: Calculates the total size of a list of files.
- `collect_files_from_multiple_sources(self, source_paths, transfer_mode)`: Collects files from multiple source folders.
- `get_total_size_of_files(self, source_path, transfer_mode)`: Calculates the total size of files for one source folder.
- `get_total_size_of_multiple_sources(cls, source_paths, transfer_mode)`: Calculates the total size of files across multiple sources.
- `are_on_same_drive(cls, source_path, destination_path)`: Checks whether source and destination are on the same drive.
- `get_folder_size(folder_path)`: Calculates the size of all files under a folder tree.
- `check_disk_space(self, source_path, destination_path, transfer_mode)`: Verifies there is enough free disk space for a single-source transfer when needed.
- `check_disk_space_for_multiple_sources(self, source_paths, destination_path, transfer_mode)`: Verifies disk space for multi-source transfers.
- `create_category_directories(cls, destination_path)`: Creates category folders under the destination path.
- `multi_search_and_categorize_files(self, source_path_list, destination_path, mode, progress_callback=None)`: Processes multiple source folders and combines all partial results.
- `create_new_file_name(destination_path, category, item)`: Generates a non-conflicting destination filename by appending a counter if necessary.
- `build_transfer_plan(transfer_mode, source_path)`: Builds the iterable item list and move/copy behavior for the selected transfer mode.
- `get_number_of_files(self, source_path, transfer_mode)`: Returns the number of files selected by a transfer mode.
- `get_file_category(cls, file_path)`: Determines the destination category based on file extension.
- `transfer_single_file(self, source_file, destination_root, use_move)`: Copies or moves one file into its category folder.
- `search_and_categorize_files(self, destination_path, source_path, transfer_mode, progress_callback=None)`: Main single-source transfer routine that performs file transfers and reports progress.

#### `ReportWriter` methods

- `build_text_report(result)`: Builds a human-readable report string from a `TransferResult`.
- `write_text_report(result, report_path)`: Writes the generated report string to disk.

#### `TransferResult` methods

- `add_transferred(self, filename)`: Adds a transferred filename to the result.
- `add_skipped(self, filename)`: Adds a skipped filename to the result.
- `add_error(self, message)`: Adds an error message to the result.

### Application Flow

The runtime flow is:

1. `main.py` creates the Tkinter root window and initializes `FileOrganizerGUI`.
2. The GUI collects user paths and the selected transfer mode.
3. `FileOrganizerLogic` validates input paths and disk space rules.
4. A transfer plan is built from the selected `TransferMode`.
5. Files are categorized by extension and copied or moved into destination folders.
6. Results are stored in `TransferResult`.
7. `ReportWriter` creates `report.txt`.

## Error Handling

The application uses custom exceptions to keep validation and operational errors readable:

- Invalid source folder
- Invalid destination folder
- Invalid source/destination relationship
- Insufficient free disk space
- Unexpected runtime errors during file transfer

## Notes and Current Limitations

- The GUI is designed for desktop use with Tkinter.
- File type detection is based only on file extension.
- Empty folders are not transferred, only files.
- `helper_functions.py` looks like an earlier prototype/helper module and is not part of the main runtime flow.
- The generated report is always written as `report.txt` in the project directory.

## Future Improvements

- Add folder browsing dialogs instead of manual path entry
- Add unit tests
- Add logging
- Add support for user-defined categories
- Add configuration file support
- Add packaging for executable distribution
- Improve skipped-file reporting

## Running the Application

```powershell
python main.py
```

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.
