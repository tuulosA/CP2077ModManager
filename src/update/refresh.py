import logging
import tkinter as tk
from tkinter import ttk
from typing import Optional

from src.ui import populate_results_list, create_file_list
from src.utils import _load_tracked_mods_cache, _load_download_cache, _list_installed_archives

logger = logging.getLogger(__name__)


def refresh_results(results_tree: ttk.Treeview, progress_label: Optional[tk.Label] = None):
    """Reload the cache and refresh the results tree."""
    if progress_label:
        progress_label.config(text="Refreshing tracked mods...")
        progress_label.update_idletasks()

    try:
        # Reload the caches
        tracked_mods = _load_tracked_mods_cache()
        downloaded_files = _load_download_cache()

        if not tracked_mods:
            logging.info("No tracked mods found in cache.")
            if progress_label:
                progress_label.config(text="No tracked mods found in cache.")
            return

        # Repopulate the results tree
        populate_results_list(results_tree, tracked_mods, downloaded_files)

        if progress_label:
            progress_label.config(text="Refresh complete.")
    except Exception as e:
        logging.error(f"Error refreshing results: {e}")
        if progress_label:
            progress_label.config(text="Error refreshing results. Check logs for details.")

def refresh_downloaded_files_ui(files_tree):
    """Trigger UI refresh for Downloaded Files tab."""
    create_file_list(files_tree)
    files_tree.update_idletasks()

def refresh_archives_ui(archives_tree: ttk.Treeview):
    """Refresh the Installed Archives list, ensuring proper alphabetical order."""
    logging.info("Refreshing Installed Archives list...")

    # Clear existing items
    archives_tree.delete(*archives_tree.get_children())

    # Use the fixed sorting function
    archives = _list_installed_archives()

    for archive in archives:
        archives_tree.insert("", "end", text=archive)

    archives_tree.update_idletasks()
