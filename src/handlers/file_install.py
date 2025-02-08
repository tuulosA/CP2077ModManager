import logging
from tkinter import messagebox
from src.core.install import extract_and_track_files
from src.update import refresh_downloaded_files_ui, refresh_archives_ui
from src.utils import (
    _install_progress_window,
    _load_download_cache,
    _save_download_cache,
    _load_installed_files,
    _save_installed_files, _get_file_details, _validate_installation_settings
)

logger = logging.getLogger(__name__)


def handle_file_install(files_tree, settings, archives_tree):
    """Install selected mods from the Downloaded Files tab and track extracted files."""
    selected_items = files_tree.selection()
    if not selected_items:
        messagebox.showwarning("Warning", "Please select at least one file to install.")
        return

    game_install_dir = _validate_installation_settings(settings)
    if not game_install_dir:
        return  # Error message already shown inside `_validate_installation_settings`

    installed_files = _load_installed_files()
    downloaded_files = _load_download_cache()

    progress_window, progress_label = _install_progress_window()
    progress_window.update()  # Force UI to refresh

    try:
        for item in selected_items:
            file_name = files_tree.item(item, "values")[1]  # Get filename from tree selection
            file_details = downloaded_files.get("files", {}).get(file_name)

            if not file_details:
                logging.warning(f"⚠️ File '{file_name}' not found in tracking. Skipping.")
                continue

            mod_path, mod_name, tracking_key = _get_file_details(file_name, file_details, settings)
            if not mod_path:
                logging.warning(f"⚠️ File '{file_name}' does not exist. Skipping.")
                continue

            progress_label.config(text=f"Extracting {file_name}...")
            progress_window.update()

            try:
                extracted_files, detected_format = extract_and_track_files(file_name, mod_path, game_install_dir)

                if not extracted_files:
                    logging.warning(f"⚠️ No valid files extracted from '{file_name}'. Skipping tracking.")
                    continue

                installed_files[tracking_key] = {
                    "mod_name": mod_name,
                    "author_upload": file_details.get("latest_downloaded_timestamp"),
                    "extracted_files": extracted_files
                }

                logging.info(f"✅ Installed '{tracking_key}' successfully.")

            except ValueError as ve:
                logging.error(f"❌ Unsupported file format: {ve}")
                messagebox.showerror("Error", str(ve))

            except Exception as e:
                logging.error(f"❌ Unexpected error extracting '{file_name}': {e}")
                messagebox.showerror("Error", f"Unexpected error extracting '{file_name}'. Check logs for details.")

    finally:
        _save_installed_files(installed_files)
        _save_download_cache(downloaded_files)

        progress_window.destroy()
        messagebox.showinfo("Success", "Selected mods have been installed.")

        refresh_downloaded_files_ui(files_tree)
        refresh_archives_ui(archives_tree)
