import os
import logging
from tkinter import messagebox

from src.update import refresh_downloaded_files_ui, refresh_archives_ui
from src.utils import _load_installed_files, _save_installed_files, _find_matching_mod, _remove_file_safely

logger = logging.getLogger(__name__)


def handle_file_uninstall(files_tree, settings, archives_tree):
    """Uninstall selected mods by deleting only the extracted files, leaving folders intact."""
    selected_items = files_tree.selection()
    if not selected_items:
        messagebox.showwarning("Warning", "Please select at least one installed mod to uninstall.")
        return

    game_install_dir = settings.get("game_installation_dir", "")
    if not game_install_dir or not os.path.exists(game_install_dir):
        messagebox.showerror("Error", "Game installation folder is not set or does not exist. Please configure it in settings.")
        return

    installed_files = _load_installed_files()

    for item in selected_items:
        file_name = files_tree.item(item, "values")[1]  # Get filename from tree selection

        # Find matching mod, ignoring file extensions
        tracked_file_name = _find_matching_mod(file_name, installed_files)
        if not tracked_file_name:
            logging.warning(f"Mod '{file_name}' is not tracked as installed. Skipping.")
            continue

        logging.info(f"Uninstalling '{tracked_file_name}'...")

        mod_data = installed_files[tracked_file_name]
        extracted_files = mod_data.get("extracted_files", [])

        # Delete only files, skip directories
        for file_path in extracted_files:
            if os.path.isfile(file_path):  # Only removes files, never folders
                _remove_file_safely(file_path)
            else:
                logging.info(f"Skipping directory: {file_path}")

        # Remove from installed tracking
        del installed_files[tracked_file_name]

    _save_installed_files(installed_files)
    messagebox.showinfo("Success", "Selected mods have been uninstalled.")
    refresh_downloaded_files_ui(files_tree)  # Refresh UI properly
    refresh_archives_ui(archives_tree)  # Refresh Installed Archives
