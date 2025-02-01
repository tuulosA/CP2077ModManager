import logging
import threading
from tkinter import Toplevel, Label, messagebox
import json
import os

from src.api import get_tracked_mods
from src.ui import populate_results_list

from src.config import Config

logger = logging.getLogger(__name__)


def handle_mod_search(progress_label, progress_bar, results_tree):
    """Fetch and display tracked mods with a loading popup using threading and a ThreadPoolExecutor."""
    def worker():
        loading_popup = None
        try:
            # Create a loading popup
            loading_popup = Toplevel()
            loading_popup.title("Loading")
            loading_popup.geometry("300x100")
            loading_label = Label(loading_popup, text="Fetching tracked mods...", font=("Arial", 12))
            loading_label.pack(pady=20)
            loading_popup.update()

            if progress_label:
                progress_label.config(text="Fetching tracked mods...")
            if progress_bar:
                progress_bar.start()

            # Fetch tracked mods (this call internally uses ThreadPoolExecutor)
            mods = get_tracked_mods()

            # Load downloaded file metadata
            downloaded_files = {}
            if os.path.exists(Config.DOWNLOADED_FILES_CACHE):
                with open(Config.DOWNLOADED_FILES_CACHE, "r") as cache_file:
                    downloaded_files = json.load(cache_file)

            # Display mods in the results tree
            logging.info("Displaying fetched mods and calculating their statuses...")
            populate_results_list(results_tree, mods, downloaded_files)

            # Save mods to cache
            with open(Config.CACHE_FILE, "w") as cache_file:
                json.dump(mods, cache_file)
                logging.info("Saved tracked mods to cache.")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to fetch tracked mods: {e}")
            logging.error(f"Error displaying tracked mods: {e}")
        finally:
            if progress_bar:
                progress_bar.stop()
            if progress_label:
                progress_label.config(text="")
            if loading_popup:
                loading_popup.destroy()

    # Run the worker in a separate thread so that the UI doesn't freeze.
    threading.Thread(target=worker, daemon=True).start()