import os
import shutil
import zipfile
import logging
from tkinter import messagebox

import patoolib  # For handling .rar

from src.config import Config

logger = logging.getLogger(__name__)


def _extract_zip(file_path, extract_to):
    """Extracts a ZIP archive, ensuring the topmost folder is valid and handling `.archive` files correctly."""
    temp_extraction_dir = os.path.join(extract_to, "_temp_extracted")
    os.makedirs(temp_extraction_dir, exist_ok=True)

    with zipfile.ZipFile(file_path, "r") as zip_ref:
        zip_ref.extractall(temp_extraction_dir)

    _extract_common(temp_extraction_dir, extract_to, file_path)

def _extract_rar(file_path, extract_to):
    """Extracts a RAR archive while ensuring proper mod installation structure."""
    temp_extraction_dir = os.path.join(extract_to, "_temp_extracted")
    os.makedirs(temp_extraction_dir, exist_ok=True)

    patoolib.extract_archive(file_path, outdir=temp_extraction_dir)

    _extract_common(temp_extraction_dir, extract_to, file_path)

def _extract_common(temp_extraction_dir, extract_to, file_path):
    """Handles the extraction logic for both ZIP and RAR archives."""
    extracted_files = _list_files_recursive(temp_extraction_dir)

    if _handle_only_archive_files(temp_extraction_dir, extracted_files, file_path):
        _cleanup_temp_extraction(temp_extraction_dir)
        return

    temp_extraction_dir = _find_deepest_valid_folder(temp_extraction_dir)
    folder_structure, mod_folders_present = _get_folder_structure_and_mod_presence(extracted_files)

    if not folder_structure:
        _log_and_cleanup(f"No valid root folders found in '{file_path}'. Skipping extraction.", temp_extraction_dir)
        _cleanup_temp_extraction(temp_extraction_dir)
        return

    _process_extracted_structure(temp_extraction_dir, extract_to, file_path, folder_structure, mod_folders_present)
    _cleanup_temp_extraction(temp_extraction_dir)

def _cleanup_temp_extraction(temp_extraction_dir):
    """Ensures the temporary extraction directory is removed after processing."""
    if os.path.exists(temp_extraction_dir):
        shutil.rmtree(temp_extraction_dir)
        logging.info(f"✅ Cleaned up temporary extraction directory: {temp_extraction_dir}")

def _handle_only_archive_files(temp_extraction_dir, extracted_files, file_path):
    """Handles cases where only .archive files are extracted."""
    if all(f.endswith(".archive") for f in extracted_files):
        logging.info(f"📂 Only .archive files detected in '{file_path}'. Extracting to {Config.ARCHIVE_FOLDER}...")

        if not os.path.exists(Config.ARCHIVE_FOLDER):
            os.makedirs(Config.ARCHIVE_FOLDER, exist_ok=True)

        for file in extracted_files:
            shutil.move(os.path.join(temp_extraction_dir, file), Config.ARCHIVE_FOLDER)

        shutil.rmtree(temp_extraction_dir)
        logging.info(f"Extracted .archive files to {Config.ARCHIVE_FOLDER}")
        return True
    return False

def _get_folder_structure_and_mod_presence(extracted_files):
    """Determines the folder structure and checks for mod folders."""
    folder_structure = {os.path.normpath(f).split(os.sep)[0] for f in extracted_files if os.sep in f}
    mod_folders_present = Config.MOD_FOLDERS.intersection(folder_structure)
    return folder_structure, mod_folders_present

def _process_extracted_structure(temp_extraction_dir, extract_to, file_path, folder_structure, mod_folders_present):
    """Processes the extracted folder structure and moves files accordingly."""
    topmost_root_folder = sorted(folder_structure)[0]

    if topmost_root_folder not in Config.MOD_FOLDERS:
        extracted_mod_dir = os.path.join(temp_extraction_dir, topmost_root_folder)
        if os.path.exists(extracted_mod_dir):
            _move_relevant_folders(extracted_mod_dir, extract_to)
            shutil.rmtree(temp_extraction_dir)  # Cleanup temp extraction
        else:
            logging.warning(f"Unexpected structure in {file_path}. Extracting normally.")
            shutil.move(temp_extraction_dir, extract_to)
    elif mod_folders_present:
        _move_relevant_folders(temp_extraction_dir, extract_to)
        shutil.rmtree(temp_extraction_dir)  # Cleanup temp extraction
    else:
        logging.warning(f"Unrecognized folder structure in '{file_path}'. Extracting normally.")
        shutil.move(temp_extraction_dir, extract_to)

def _log_and_cleanup(message, temp_extraction_dir):
    """Logs a warning message and removes the temporary extraction directory."""
    logging.warning(message)
    shutil.rmtree(temp_extraction_dir)

def _find_deepest_valid_folder(temp_extraction_dir):
    """Finds the deepest folder containing mod files inside the extracted directory."""
    current_dir = temp_extraction_dir
    while True:
        subdirs = [d for d in os.listdir(current_dir) if os.path.isdir(os.path.join(current_dir, d))]

        # If we found standard mod folders, return the current directory
        if any(folder in subdirs for folder in Config.MOD_FOLDERS):
            return current_dir

        # If there's only one folder inside, go deeper
        if len(subdirs) == 1:
            current_dir = os.path.join(current_dir, subdirs[0])
        else:
            break  # Stop if we can't drill down further

    return temp_extraction_dir  # Return the best guess if nothing valid is found

def _move_relevant_folders(src_dir, dest_dir):
    """Moves only the relevant mod folders (e.g., `archive`, `bin`) from a nested extraction to the correct location."""
    for folder in os.listdir(src_dir):
        folder_path = os.path.join(src_dir, folder)

        if folder in Config.MOD_FOLDERS and os.path.isdir(folder_path):
            dest_path = os.path.join(dest_dir, folder)

            if not os.path.exists(dest_path):
                os.makedirs(dest_path)  # Create destination if it doesn't exist

            for root, _, files in os.walk(folder_path):
                relative_path = os.path.relpath(root, folder_path)
                target_dir = os.path.join(dest_path, relative_path)

                if not os.path.exists(target_dir):
                    os.makedirs(target_dir)

                for file in files:
                    src_file = os.path.join(root, file)
                    dest_file = os.path.join(target_dir, file)

                    shutil.move(src_file, dest_file)

            shutil.rmtree(folder_path)

        elif os.path.isdir(folder_path):
            logging.info(f"Skipping non-mod folder '{folder}'")

def _list_files_recursive(directory):
    """Recursively list all files inside a directory, ignoring folders."""
    all_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            full_path = os.path.join(root, file)
            if not full_path.endswith((".zip", ".rar")):  # Ignore archive files themselves
                all_files.append(full_path)
    return all_files

def _validate_installation_settings(settings):
    """Validates game installation directory settings."""
    game_install_dir = settings.get("game_installation_dir", "")
    if not game_install_dir or not os.path.exists(game_install_dir):
        messagebox.showerror("Error", "Game installation folder is not set or does not exist. Please configure it in settings.")
        return None
    return game_install_dir
