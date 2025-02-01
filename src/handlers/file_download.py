import logging
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, List

from src.core import download_selected_files
from src.ui import show_file_selection_popup
from src.update import refresh_results, refresh_downloaded_files_ui
from src.utils import _update_progress_bar, _get_selected_mod

logger = logging.getLogger(__name__)


def handle_file_download(results_tree: ttk.Treeview, progress_label: tk.Label, settings: Dict, files_tree: ttk.Treeview):
    """Handle downloading selected mod files with a progress bar."""
    try:
        # Get selected mod
        selected_item = _get_selected_mod(results_tree)
        if not selected_item:
            return

        mod_id, mod_name = selected_item

        def on_files_selected(selected_files: List[int]):
            """Handle file selection from the popup."""
            if not selected_files:
                messagebox.showinfo("No Selection", "No files were selected.")
                return

            # Create a progress bar window
            progress_window = tk.Toplevel()
            progress_window.title("Downloading Files")
            progress_window.geometry("400x150")

            tk.Label(progress_window, text=f"Downloading files for {mod_name}...", font=("Arial", 12)).pack(pady=10)
            progress_bar = ttk.Progressbar(progress_window, length=300, mode="determinate", maximum=100)
            progress_bar.pack(pady=10)
            progress_label = tk.Label(progress_window, text="Initializing download...")
            progress_label.pack(pady=5)

            progress_window.update()

            try:
                total_files = len(selected_files)
                for index, file_id in enumerate(selected_files, start=1):
                    def progress_callback(percent_complete, downloaded_mb, total_mb):
                        """Update the progress bar for the current file."""
                        cumulative_percent = ((index - 1) / total_files * 100) + (percent_complete / total_files)
                        _update_progress_bar(progress_bar, progress_label, cumulative_percent, downloaded_mb, total_mb)

                    success = download_selected_files(
                        "cyberpunk2077", mod_id, [file_id], settings["output_dir"], progress_callback
                    )
                    if not success:
                        messagebox.showerror("Error", f"Failed to download file with ID {file_id}.")
                        progress_window.destroy()
                        return

                refresh_results(results_tree, progress_label)
                refresh_downloaded_files_ui(files_tree)

                messagebox.showinfo("Success", f"Downloaded {total_files} file(s) successfully!")
            except Exception as e:
                logging.error(f"Error during file download: {e}")
                messagebox.showerror("Error", f"Failed to download files: {e}")
            finally:
                progress_window.destroy()

        # Show file selection popup
        show_file_selection_popup("cyberpunk2077", mod_id, on_files_selected)

    except Exception as e:
        logging.error(f"Error in handle_mod_download: {e}")
        messagebox.showerror("Error", f"Failed to download mod: {e}")
