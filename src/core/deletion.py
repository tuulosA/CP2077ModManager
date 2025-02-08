import logging
import os
import shutil
import re
from tkinter import messagebox

from src.update import refresh_results, refresh_downloaded_files_ui
from src.utils import _save_download_cache
from src.api import get_mod_details


logger = logging.getLogger(__name__)


def delete_selected_file(listbox, mod_name, mod_files, downloaded_files, popup, results_tree, progress_label, settings, files_tree, game="cyberpunk2077"):
    """Delete the selected file, update tracking, and refresh UI."""
    try:
        selected_index = listbox.curselection()
        if not selected_index:
            messagebox.showwarning("Warning", "Please select a file to delete.")
            return

        selected_file = str(listbox.get(selected_index))
        file_details = mod_files.get(selected_file)
        if not file_details:
            messagebox.showerror("Error", f"Selected file '{selected_file}' not found.")
            return

        mod_id = file_details.get("mod_id")
        if not mod_id:
            messagebox.showerror("Error", f"Missing mod_id for file '{selected_file}'.")
            return

        mod_details = get_mod_details(game, mod_id)
        if not mod_details:
            messagebox.showerror("Error", f"Failed to fetch mod details for mod ID {mod_id}.")
            return

        mod_category = mod_details.get("category", "Uncategorized").strip()
        resolved_mod_name = mod_details.get("name", f"Mod_{mod_id}")

        # Ensure the output directory is retrieved correctly
        output_dir = settings.get("output_dir", "")
        if not output_dir:
            messagebox.showerror("Error", "Output directory is not set. Please configure it in the settings.")
            return

        # 🔹 Remove timestamp suffix (_YYYYMMDD_HHMMSS.zip) from filename
        subdir_name = re.sub(r"_\d{8}_\d{6}\.zip$", "", selected_file)

        # Construct the correct mod file path
        mod_base_dir = os.path.join(output_dir, mod_category, resolved_mod_name, subdir_name)
        file_path = os.path.join(mod_base_dir, selected_file)

        logging.debug(f"🛠️ Constructed file path for deletion: {file_path}")

        _delete_file_from_disk(file_path)
        _delete_empty_directory(os.path.dirname(file_path))
        _remove_file_from_tracking(selected_file, downloaded_files)
        refresh_results(results_tree, progress_label)
        refresh_downloaded_files_ui(files_tree)  # Refresh the Downloaded Files tab

        listbox.delete(selected_index)
        messagebox.showinfo("Success", f"Deleted '{selected_file}' successfully.")
    except Exception as e:
        logging.error(f"Error deleting file or directory: {e}")
        messagebox.showerror("Error", f"Failed to delete file or its directory: {e}")

def _delete_file_from_disk(file_path):
    """Delete a file from the disk."""
    if os.path.exists(file_path):
        os.remove(file_path)
        logging.info(f"Deleted file: {file_path}")
    else:
        logging.warning(f"File not found: {file_path}")

def _delete_empty_directory(directory_path):
    """Delete a directory if it is empty."""
    if os.path.exists(directory_path) and not os.listdir(directory_path):
        shutil.rmtree(directory_path)
        logging.info(f"Deleted empty directory: {directory_path}")
    else:
        logging.info(f"Directory '{directory_path}' is not empty and was not deleted.")

def _remove_file_from_tracking(selected_file, downloaded_files):
    """Remove a file from JSON tracking."""
    if selected_file in downloaded_files["files"]:
        del downloaded_files["files"][selected_file]
        _save_download_cache(downloaded_files)
        logging.info(f"Removed '{selected_file}' from tracking.")