import os
import json
import re
from typing import Dict, List
import logging
from datetime import datetime
from tkinter import messagebox, simpledialog

from src.config import Config

logger = logging.getLogger(__name__)


def _load_download_cache() -> dict:
    """Load the downloaded files JSON cache."""
    if os.path.exists(Config.DOWNLOADED_FILES_CACHE):
        with open(Config.DOWNLOADED_FILES_CACHE, "r") as cache_file:
            return json.load(cache_file)
    return {}

def _save_download_cache(downloaded_files: dict):
    """Save the updated cache data."""
    try:
        with open(Config.DOWNLOADED_FILES_CACHE, "w") as cache_file:
            json.dump(downloaded_files, cache_file, indent=4)
        logging.info(f"Cache successfully saved.")
    except Exception as e:
        logging.error(f"Error saving download cache: {e}")

def _load_installed_files():
    """Load the installed files tracking JSON."""
    if os.path.exists(Config.INSTALLED_FILES_PATH):
        with open(Config.INSTALLED_FILES_PATH, "r") as f:
            return json.load(f)
    return {}

def _save_installed_files(installed_files):
    """Save the installed files tracking JSON."""
    with open(Config.INSTALLED_FILES_PATH, "w") as f:
        json.dump(installed_files, f, indent=4)

def _load_tracked_mods_cache() -> List[Dict]:
    """Load the tracked mods from the cache."""
    if os.path.exists(Config.CACHE_FILE):
        try:
            with open(Config.CACHE_FILE, "r") as cache_file:
                return json.load(cache_file)
        except Exception as e:
            logging.error(f"Error loading tracked mods cache: {e}")
    return []

def _setup_mod_directory(mod_details: dict, output_dir: str) -> str:
    """Create and prepare the base directory structure for the mod."""
    mod_name = mod_details.get("name", f"Mod_{mod_details.get('id', 'unknown')}")
    mod_category = mod_details.get("category", "Uncategorized")

    # Base directory
    mod_base_dir = os.path.join(output_dir, mod_category, mod_name)
    os.makedirs(mod_base_dir, exist_ok=True)

    return mod_base_dir

def _clean_directory(directory: str):
    """Ensure the directory contains only the latest downloaded file."""
    for existing_file in os.listdir(directory):
        path = os.path.join(directory, existing_file)
        try:
            if os.path.isfile(path):
                os.remove(path)
                logging.info(f"Removed old file: {path}")
        except Exception as e:
            logging.error(f"Error deleting file '{path}': {e}")

def _find_matching_installed_file(file_name, installed_files):
    """
    Search for a mod in installed_files, ignoring file extensions.
    Example: If tracking says `mod.7z`, it should still find `mod.zip` or `mod.rar`.
    """
    base_name = file_name.rsplit(".", 1)[0]  # Remove extension
    for stored_file in installed_files.keys():
        stored_base = stored_file.rsplit(".", 1)[0]
        if stored_base == base_name:
            return True
    return False

def _move_item(tree, direction):
    """Move selected archive file up or down in the list."""
    selected_item = tree.selection()
    if not selected_item:
        return

    index = tree.index(selected_item)
    if (direction == "up" and index > 0) or (direction == "down" and index < len(tree.get_children()) - 1):
        swap_index = index - 1 if direction == "up" else index + 1
        tree.move(selected_item, "", swap_index)

def _list_installed_archives():
    """
    Load the JSON file and return a sorted list of installed .archive files.
    This function iterates over each mod's "extracted_files" and includes only those
    whose filename ends with '.archive'. (Optionally, you can filter to ensure the file
    is in the expected mod folder.)
    """
    json_path = Config.INSTALLED_FILES_PATH
    if not os.path.exists(json_path):
        return []

    with open(json_path, "r") as f:
        data = json.load(f)

    archive_files = []
    # Each key in the JSON represents an archive (zip/rar) upload,
    # and the associated "extracted_files" list contains the installed file paths.
    for mod_entry in data.values():
        extracted_files = mod_entry.get("extracted_files", [])
        for file_path in extracted_files:
            # Only include files ending with ".archive"
            if file_path.lower().endswith(".archive"):
                # Optionally, check if the file is in the mod folder.
                # For example, uncomment the following lines to filter by folder:
                #
                # if os.path.dirname(file_path).lower() != Config.ARCHIVE_FOLDER.lower():
                #     continue
                #
                # We extract only the file name.
                archive_files.append(os.path.basename(file_path))

    # Remove duplicates (if any) and sort case-insensitively.
    return sorted(set(archive_files), key=lambda x: x.lower())

def _rename_archive(tree):
    """
    Allow the user to rename a selected .archive file.
    This renames the file on disk (using Config.ARCHIVE_FOLDER) and updates the JSON
    file so that the new file name replaces the old one in the corresponding extracted_files.
    """
    selected_item = tree.selection()
    if not selected_item:
        messagebox.showwarning("Warning", "Please select a file to rename.")
        return

    old_name = tree.item(selected_item, "text")
    new_name = simpledialog.askstring("Rename Archive", "Enter new file name:",
                                      initialvalue=old_name)

    if not new_name:
        return  # User cancelled

    if not new_name.lower().endswith(".archive"):
        messagebox.showerror("Error", "Invalid file name. Must end with .archive")
        return

    old_path = os.path.join(Config.ARCHIVE_FOLDER, old_name)
    new_path = os.path.join(Config.ARCHIVE_FOLDER, new_name)

    # Rename the file on disk.
    try:
        os.rename(old_path, new_path)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to rename file on disk: {e}")
        return

    # Now update the JSON file.
    json_path = Config.INSTALLED_FILES_PATH
    try:
        with open(json_path, "r") as f:
            data = json.load(f)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to load JSON file: {e}")
        return

    updated = False
    # Search through each mod's extracted_files and update the matching entry.
    for mod_entry in data.values():
        updated_files = []
        for file_path in mod_entry.get("extracted_files", []):
            if os.path.basename(file_path) == old_name:
                # Replace the file name with the new name but preserve the directory.
                updated_files.append(os.path.join(Config.ARCHIVE_FOLDER, new_name))
                updated = True
            else:
                updated_files.append(file_path)
        mod_entry["extracted_files"] = updated_files

    if updated:
        try:
            with open(json_path, "w") as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update JSON file: {e}")
            return

    # Update the treeview to display the new file name.
    tree.item(selected_item, text=new_name)
    messagebox.showinfo("Success", "File renamed successfully.")

def _parse_file_timestamp(file_name):
    """
    Extract and parse the timestamp from a file name.
    Format expected: {mod_name}_{YYYYMMDD_HHMMSS}.zip
    """
    logging.debug(f"Attempting to parse timestamp from file: {file_name}")

    timestamp_pattern = r"_(\d{8}_\d{6})\.zip"  # Regex to capture the timestamp
    match = re.search(timestamp_pattern, file_name)  # Search for the pattern
    if match:
        try:
            parsed_time = datetime.strptime(match.group(1), "%Y%m%d_%H%M%S")  # Parse to datetime
            logging.debug(f"Parsed timestamp: {parsed_time} from file: {file_name}")
            return parsed_time
        except ValueError as e:
            logging.error(f"Failed to parse timestamp from file: {file_name}. Error: {e}")
    else:
        logging.warning(f"No valid timestamp found in file name: {file_name}")

    return None  # Return None if no valid timestamp is found