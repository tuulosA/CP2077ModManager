import os
import re
import logging
from tkinter import messagebox

from src.core import extract_archive
from src.update import refresh_downloaded_files_ui, refresh_archives_ui
from src.utils import (
    _fetch_mod_details,
    _install_progress_window,
    _load_download_cache,
    _save_download_cache,
    _load_installed_files,
    _save_installed_files
)

logger = logging.getLogger(__name__)


def handle_file_install(files_tree, settings, archives_tree):
    """Install selected mods from the Downloaded Files tab and track extracted files."""
    selected_items = files_tree.selection()
    if not selected_items:
        messagebox.showwarning("Warning", "Please select at least one file to install.")
        return

    game_install_dir = settings.get("game_installation_dir", "")
    if not game_install_dir or not os.path.exists(game_install_dir):
        messagebox.showerror("Error", "Game installation folder is not set or does not exist. Please configure it in settings.")
        return

    installed_files = _load_installed_files()
    downloaded_files = _load_download_cache()

    progress_window, progress_label = _install_progress_window()
    progress_window.update()  # Force UI to refresh

    try:
        for item in selected_items:
            file_name = files_tree.item(item, "values")[1]  # Get filename from tree selection
            file_details = downloaded_files.get("files", {}).get(file_name)

            if not file_details:
                logging.warning(f"File '{file_name}' not found in tracking. Skipping.")
                continue

            mod_id = file_details.get("mod_id")
            mod_name = file_details.get("mod_name", "Unknown")

            # Fetch mod category properly
            mod_details = _fetch_mod_details("cyberpunk2077", mod_id) or {}
            mod_category = mod_details.get("category", "Uncategorized").strip()

            # 🔹 Remove timestamp suffix (_YYYYMMDD_HHMMSS.zip) from filename
            subdir_name = re.sub(r"_\d{8}_\d{6}\.[a-zA-Z0-9]+$", "", file_name)

            mod_base_dir = os.path.join(settings["output_dir"], mod_category, mod_name, subdir_name)
            mod_path = os.path.join(mod_base_dir, file_name)

            if not os.path.exists(mod_path):
                logging.warning(f"File '{mod_path}' does not exist. Skipping.")
                continue

            progress_label.config(text=f"Extracting {file_name}...")
            progress_window.update()

            try:
                logging.info(f"Extracting '{file_name}' to {game_install_dir}...")
                extracted_files, detected_format = extract_archive(mod_path, game_install_dir)

                extracted_files = [f for f in extracted_files if os.path.isfile(f)]  # Ensure tracking only extracted files

                if not extracted_files:
                    logging.warning(f"No valid files extracted from '{file_name}'. Skipping tracking.")
                    continue

                tracking_key = file_name if detected_format == "zip" else file_name.replace(".zip", ".rar")
                installed_files[tracking_key] = {
                    "mod_name": mod_name,
                    "author_upload": file_details.get("latest_downloaded_timestamp"),
                    "extracted_files": extracted_files
                }

                logging.info(f"Installed '{tracking_key}' successfully.")

            except ValueError as ve:
                logging.error(f"Unsupported file format: {ve}")
                messagebox.showerror("Error", str(ve))

            except Exception as e:
                logging.error(f"Unexpected error extracting '{file_name}': {e}")
                messagebox.showerror("Error", f"Unexpected error extracting '{file_name}'. Check logs for details.")

    finally:
        _save_installed_files(installed_files)
        _save_download_cache(downloaded_files)

        progress_window.destroy()
        messagebox.showinfo("Success", "Selected mods have been installed.")

        refresh_downloaded_files_ui(files_tree)
        refresh_archives_ui(archives_tree)

