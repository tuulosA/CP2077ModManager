import logging
import tkinter as tk
from tkinter import ttk

from src.ui import create_results_panel, populate_results_list
from src.handlers import handle_file_install, handle_file_uninstall, handle_mod_search, handle_file_download, \
    handle_modify_files
from src.update.updates import start_update_thread
from src.utils import _load_download_cache, _load_tracked_mods_cache, _show_update_popup

logger = logging.getLogger(__name__)


def initialize_mod_data(root, results_tree, progress_label):
    """Loads cached mods and starts update checks."""
    try:
        tracked_mods = _load_tracked_mods_cache()
        downloaded_files = _load_download_cache()

        update_popup = _show_update_popup(root)
        start_update_thread(root, downloaded_files, update_popup)

        if tracked_mods:
            logging.info("Populating results with cached mods.")

            populate_results_list(results_tree, tracked_mods, downloaded_files)
            progress_label.config(text="Mods loaded successfully.")
        else:
            logging.info("No cached mods found.")
            progress_label.config(text="No mods found in cache.")
    except Exception as e:
        logging.error(f"Failed to load mods on startup: {e}")
        progress_label.config(text="Error loading mods. Check logs for details.")


def setup_file_buttons(files_frame, files_tree, settings, archives_tree):
    """Adds buttons for installing and uninstalling mods."""
    ttk.Button(files_frame, text="Install Mods",
               command=lambda: handle_file_install(files_tree, settings, archives_tree)).pack(pady=5)
    ttk.Button(files_frame, text="Uninstall Mods",
               command=lambda: handle_file_uninstall(files_tree, settings, archives_tree)).pack(pady=5)


def setup_tracked_mods_tab(mods_frame, settings, files_tree):
    """Sets up the tracked mods UI elements and returns results_tree and progress_label."""
    results_tree = create_results_panel(mods_frame)
    progress_label = tk.Label(mods_frame, text="Loading mods...")
    progress_label.pack(pady=5)

    setup_ui_buttons(mods_frame, results_tree, progress_label, settings, files_tree)

    return results_tree, progress_label


def setup_ui_buttons(root, results_tree, progress_label, settings, files_tree):
    """Creates a row of buttons for the UI."""
    buttons_frame = ttk.Frame(root)
    buttons_frame.pack(pady=5)

    ttk.Button(buttons_frame, text="Fetch Tracked Mods",
               command=lambda: handle_mod_search(None, None, results_tree)).grid(row=0, column=0, padx=5)

    ttk.Button(buttons_frame, text="Download Mod",
               command=lambda: handle_file_download(results_tree, progress_label, settings, files_tree)).grid(row=0, column=2, padx=5)

    ttk.Button(buttons_frame, text="Modify Files",
               command=lambda: handle_modify_files(results_tree, progress_label, settings, files_tree)).grid(row=0, column=3, padx=5)

