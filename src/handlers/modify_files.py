import logging
import tkinter as tk
from tkinter import messagebox, ttk
from typing import Dict

from src.ui import show_modify_files_popup
from src.utils import _get_selected_mod, _load_download_cache

logger = logging.getLogger(__name__)


def handle_modify_files(results_tree: ttk.Treeview, progress_label: tk.Label, settings: Dict, files_tree: ttk.Treeview):
    """Handle modifying files for a selected mod (deleting files)."""
    try:
        selected_item = _get_selected_mod(results_tree)
        if not selected_item:
            return

        mod_id, mod_name = selected_item
        downloaded_files = _load_download_cache()

        mod_files = {file_name: details for file_name, details in downloaded_files.get("files", {}).items()
                     if details.get("mod_name") == mod_name}

        if not mod_files:
            messagebox.showinfo("Info", f"No downloaded files found for '{mod_name}'.")
            return

        show_modify_files_popup(mod_name, mod_files, downloaded_files, results_tree, progress_label, settings, files_tree)
    except Exception as e:
        logging.error(f"Error in handle_modify_files: {e}")
        messagebox.showerror("Error", f"Failed to modify files: {e}")

