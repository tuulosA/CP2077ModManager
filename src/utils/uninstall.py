import os
import stat
import ctypes
import logging
from tkinter import messagebox

logger = logging.getLogger(__name__)


def _remove_file_safely(file_path):
    """Ensure file is writable before deletion and try removing it."""
    try:
        if os.path.isfile(file_path):  # Only attempt to delete actual files
            os.chmod(file_path, stat.S_IWRITE)  # Remove read-only flag
            os.remove(file_path)  # Delete file
            logging.info(f"Deleted file: {file_path}")
    except PermissionError:
        logging.error(f"Failed to delete {file_path}. Trying as admin...")
        try:
            if ctypes.windll.shell32.IsUserAnAdmin():
                os.system(f'del /F /Q "{file_path}"')
            else:
                messagebox.showerror("Error", f"Could not delete {file_path}. Try running as Administrator.")
        except Exception as e:
            logging.error(f"Could not remove {file_path}: {e}")


def _find_matching_mod(file_name, installed_files):
    """
    Search for a mod in installed_files, ignoring file extensions.
    Example: If tracking says `mod.7z`, it should still find `mod.zip` or `mod.rar`.
    """
    base_name = file_name.rsplit(".", 1)[0]  # Remove extension
    for stored_file in installed_files.keys():
        stored_base = stored_file.rsplit(".", 1)[0]
        if stored_base == base_name:
            return stored_file
    return None
