import logging
import threading
import tkinter as tk
from tkinter import ttk
from typing import Dict

from src.ui import *
from src.handlers import *
from src.update import check_for_updates
from src.utils import _show_update_popup, _sort_treeview, _load_download_cache, _load_tracked_mods_cache

logger = logging.getLogger(__name__)


def run_app(settings: Dict):
    """Create the main UI with three tabs: Tracked Mods, Downloaded Files, and Installed Archives."""
    root = tk.Tk()
    root.title("Cyberpunk Mod Manager")

    notebook = ttk.Notebook(root)  # Create tabbed interface
    mods_frame = ttk.Frame(notebook)
    files_frame = ttk.Frame(notebook)

    notebook.add(mods_frame, text="Tracked Mods")
    notebook.add(files_frame, text="Downloaded Files")  # Second tab for files
    notebook.pack(expand=True, fill="both")

    # ✅ Fix: Let `create_file_list` handle Treeview creation
    files_tree = create_file_list(files_frame)

    # Archive tab (Now receives archives_tree directly from create_archive_tab)
    archives_frame, archives_tree = create_archive_tab(notebook)

    # Install Mods Button (inside Downloaded Files tab)
    install_button = ttk.Button(files_frame, text="Install Mods",
                                command=lambda: handle_file_install(files_tree, settings, archives_tree))
    install_button.pack(pady=5)

    # Uninstall Mods Button (inside Downloaded Files tab)
    uninstall_button = ttk.Button(files_frame, text="Uninstall Mods",
                                  command=lambda: handle_file_uninstall(files_tree, settings, archives_tree))
    uninstall_button.pack(pady=5)

    # Tracked Mods Tab
    create_settings_panel(root, settings, lambda s: logging.info("Settings saved"))
    results_tree = create_results_panel(mods_frame)
    progress_label = tk.Label(mods_frame, text="Loading mods...")
    progress_label.pack(pady=5)
    setup_ui_buttons(mods_frame, results_tree, progress_label, settings, files_tree)

    try:
        tracked_mods = _load_tracked_mods_cache()
        downloaded_files = _load_download_cache()

        # Create and show the "checking for updates" popup.
        update_popup = _show_update_popup(root)

        def run_updates():
            try:
                logging.info("Checking for mod updates...")
                check_for_updates(downloaded_files)
            except Exception as e:
                logging.error(f"Error during update check: {e}")
            finally:
                # Schedule the popup to be destroyed in the main thread.
                root.after(0, update_popup.destroy)

        # Start the update in a background thread.
        update_thread = threading.Thread(target=run_updates, daemon=True)
        update_thread.start()

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

    root.mainloop()


def setup_ui_buttons(root: tk.Tk, results_tree: ttk.Treeview, progress_label: tk.Label, settings: Dict,
                     files_tree: ttk.Treeview):
    """Set up buttons in a horizontal row instead of vertical stacking."""

    # Create a frame for buttons
    buttons_frame = ttk.Frame(root)
    buttons_frame.pack(pady=5)  # Keep some padding for spacing

    # Arrange buttons in a single row using .grid()
    ttk.Button(buttons_frame, text="Fetch Tracked Mods",
               command=lambda: handle_mod_search(None, None, results_tree)).grid(row=0, column=0, padx=5)

    ttk.Button(buttons_frame, text="Download Mod",
               command=lambda: handle_file_download(results_tree, progress_label, settings, files_tree)).grid(row=0, column=2, padx=5)

    ttk.Button(buttons_frame, text="Modify Files",
               command=lambda: handle_modify_files(results_tree, progress_label, settings, files_tree)).grid(row=0, column=3, padx=5)
