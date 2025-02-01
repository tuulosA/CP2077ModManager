from datetime import datetime
from tkinter import ttk, IntVar, Checkbutton, messagebox, Toplevel, DISABLED

from src.api import get_mod_files
from src.utils import _create_scrollable_frame, _close_popup, _clean_description, \
    _format_timestamp, _load_download_cache, _parse_file_timestamp


def show_file_selection_popup(game, mod_id, on_files_selected):
    """Show a popup menu with file options for the selected mod."""
    popup = Toplevel()
    popup.title("Select Files to Download")
    popup.geometry("400x600")

    # Create a scrollable frame
    scrollable_frame = _create_scrollable_frame(popup)

    # Fetch files for the mod
    files = get_mod_files(game, mod_id)
    if not files:
        messagebox.showinfo("No Files", "No files found for this mod.")
        popup.destroy()
        return

    # Sort files by upload timestamp in descending order
    files = sorted(files, key=lambda x: x.get("uploaded_timestamp", 0), reverse=True)

    # Create checkboxes for each file
    file_vars = _create_file_checkboxes(scrollable_frame, files)

    # Add "Download" button
    download_button = ttk.Button(
        popup,
        text="Download Selected Files",
        command=lambda: _handle_file_selection(file_vars, popup, on_files_selected),
    )
    download_button.pack(pady=10)

    # Handle the case when the popup is closed without selecting files
    popup.protocol("WM_DELETE_WINDOW", lambda: _close_popup(popup, download_button))

    # Make the popup modal
    popup.grab_set()


def _create_file_checkboxes(scrollable_frame, files):
    """Create checkboxes for files, ensuring only one checkbox per base file name can be selected.
       Also indicates which files have already been downloaded using the download cache.
    """
    file_vars = {}
    selected_base_files = set()  # Track selected base file names

    # Load downloaded files cache
    downloaded_cache = _load_download_cache()
    downloaded_files = downloaded_cache.get("files", {})

    def toggle_checkbox(file_id, base_name, var):
        """Callback to enforce unique base file selection."""
        if var.get() == 1:  # Checkbox is being selected
            # Deselect other checkboxes with the same base name
            for other_id, other_var in file_vars.items():
                if other_id != file_id and other_var["base_name"] == base_name:
                    other_var["var"].set(0)
            selected_base_files.add(base_name)
        else:  # Checkbox is being deselected
            selected_base_files.discard(base_name)

    for file in files:
        file_id = file.get("id")
        file_name = file.get("name", "Unknown File")
        size = file.get("size_kb", 0) / 1024  # Convert size to MB
        description = _clean_description(file.get("description", "No Description"))
        upload_time = _format_timestamp(file.get("uploaded_timestamp"))

        if not file_id:
            continue

        # Extract the base file name (before timestamp or version info)
        base_name = file_name.split("_")[0]

        # Convert the mod file's uploaded_timestamp to a full datetime object (UTC)
        mod_uploaded_timestamp = file.get("uploaded_timestamp")
        mod_uploaded_dt = (
            datetime.utcfromtimestamp(mod_uploaded_timestamp) if mod_uploaded_timestamp else None
        )

        # Check if a downloaded file exists that matches both the base name and the full timestamp.
        already_downloaded = False
        for downloaded_file in downloaded_files.keys():
            # Check if the downloaded file has the same base name
            if downloaded_file.startswith(base_name):
                downloaded_dt = _parse_file_timestamp(downloaded_file)
                if downloaded_dt and mod_uploaded_dt and downloaded_dt == mod_uploaded_dt:
                    already_downloaded = True
                    break

        # Update the label to indicate if the file is already downloaded.
        file_label = (
            f"{file_name} (ID: {file_id})\n"
            f"Size: {size:.2f} MB\n"
            f"Uploaded: {upload_time}\n"
            f"Description: {description}"
        )
        if already_downloaded:
            file_label += "\n[Already Downloaded]"

        # Create the IntVar for the checkbox
        var = IntVar()
        file_vars[file_id] = {"var": var, "base_name": base_name}

        # Optionally, disable the checkbox if the file is already downloaded.
        state = DISABLED if already_downloaded else None

        Checkbutton(
            scrollable_frame,
            text=file_label,
            variable=var,
            anchor="w",
            justify="left",
            wraplength=350,
            state=state,  # disable if already downloaded
            command=lambda f_id=file_id, b_name=base_name, v=var: toggle_checkbox(f_id, b_name, v),
        ).pack(fill="x", pady=5)

    return {file_id: data["var"] for file_id, data in file_vars.items()}

def _handle_file_selection(file_vars, popup, on_files_selected):
    """Handle the file selection and trigger the callback."""
    selected_files = [file_id for file_id, var in file_vars.items() if var.get() == 1]
    if not selected_files:
        messagebox.showinfo("No Selection", "No files were selected.")
    else:
        popup.destroy()
        on_files_selected(selected_files)