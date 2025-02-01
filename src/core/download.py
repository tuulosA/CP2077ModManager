import logging
import os

from src.metadata import track_download_metadata
from src.api import get_file_details, get_download_link
from src.utils import (
    _fetch_all_mod_files,
    _fetch_mod_details,
    _clean_directory,
    _save_download_cache,
    _setup_mod_directory,
    _load_download_cache,
    _download_file,
    _prepare_file_for_download,
)

logger = logging.getLogger(__name__)

def download_selected_files(game, mod_id, selected_files, output_dir, progress_callback=None):
    """Download selected files for a mod."""
    logging.info(f"Downloading files for mod ID: {mod_id}, file ID: {selected_files}")

    mod_details = _fetch_mod_details(game, mod_id)
    if not mod_details:
        logging.error(f"Mod details could not be retrieved for ID {mod_id}.")
        return False

    mod_name = mod_details.get("name", f"Mod_{mod_id}")
    mod_base_dir = _setup_mod_directory(mod_details, output_dir)
    files = _fetch_all_mod_files(game, mod_id)

    if not files:
        logging.error(f"No files found for mod ID {mod_id}.")
        return False

    downloaded_files = _load_download_cache()

    for file_id in selected_files:
        success = _process_and_download_file(
            game, mod_id, file_id, files, mod_base_dir, downloaded_files, mod_name, progress_callback
        )
        if not success:
            return False

    _save_download_cache(downloaded_files)

    logging.info("Download completed successfully.")
    return True

def _process_and_download_file(game, mod_id, file_id, files, mod_base_dir, downloaded_files, mod_name, progress_callback=None):
    """Process and download a single file."""
    logging.info(f"Processing file ID: {file_id} for mod: {mod_name}")

    file_details = get_file_details(game, mod_id, file_id)
    if not file_details:
        logging.warning(f"Details for file ID {file_id} could not be retrieved. Skipping.")
        return False

    file_name, file_path, mod_specific_dir = _prepare_file_for_download(file_details, mod_base_dir)
    logging.info(f"Prepared file for download: {file_name}")

    _clean_directory(mod_specific_dir)

    try:
        logging.info(f"Downloading file: {file_name}")
        _download_file(get_download_link(game, mod_id, file_id), file_path, progress_callback)
        file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0  # Get file size after download
    except Exception as e:
        logging.error(f"Download failed for file {file_name}: {e}")
        return False

    logging.info(f"Updating metadata for file: {file_name}")
    updated = track_download_metadata(file_name, file_details, downloaded_files, files, mod_name, mod_id, file_size)
    logging.info(f"File status: {'Outdated' if updated else 'Up-to-date'}")

    return True
