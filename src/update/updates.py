import logging
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

from src.api import get_mod_files
from src.utils import _save_download_cache

logger = logging.getLogger(__name__)

def check_for_updates(downloaded_files):
    """
    Update latest_uploaded_timestamp for each mod in the downloaded files cache.
    This version uses ThreadPoolExecutor to fetch mod file metadata concurrently,
    making the update process faster by overlapping network I/O.
    """
    logging.info("Starting to check for updates to mods in the cache.")

    files_cache = downloaded_files.get("files", {})
    total_mods = len(files_cache)
    updated_mods = 0

    def process_mod(file_name, metadata):
        mod_name = metadata.get("mod_name")
        mod_id = metadata.get("mod_id")

        if not mod_id:
            logging.warning(f"Mod ID missing for file {file_name}. Skipping update.")
            return file_name, None

        files = get_mod_files("cyberpunk2077", mod_id)
        if not files:
            return file_name, None

        # Determine the latest uploaded timestamp from the returned files.
        try:
            latest_timestamp = max(file.get("uploaded_timestamp", 0) for file in files)
        except ValueError:
            # max() may fail if files is empty
            latest_timestamp = 0

        if latest_timestamp > 0:
            new_timestamp = datetime.utcfromtimestamp(latest_timestamp).strftime("%Y-%m-%d %H:%M:%S")
            old_timestamp = metadata.get("latest_uploaded_timestamp", "Unknown")
            if new_timestamp != old_timestamp:
                logging.info(
                    f"Found an update for {file_name}: "
                    f"Current file date: {old_timestamp} -> Updated to: {new_timestamp}."
                )
                return file_name, new_timestamp
            else:
                return file_name, None
        else:
            logging.warning(f"Could not determine latest uploaded timestamp for {mod_name} (ID: {mod_id}).")
            return file_name, None

    # Use a thread pool to process mods concurrently.
    with ThreadPoolExecutor(max_workers=10) as executor:
        future_to_file = {
            executor.submit(process_mod, file_name, metadata): file_name
            for file_name, metadata in files_cache.items()
        }

        for future in as_completed(future_to_file):
            file_name = future_to_file[future]
            try:
                mod_file, new_timestamp = future.result()
                if new_timestamp is not None:
                    files_cache[mod_file]["latest_uploaded_timestamp"] = new_timestamp
                    updated_mods += 1
            except Exception as e:
                logging.error(f"Error updating mod {file_name}: {e}")

    # Save the updated cache after processing all mods.
    _save_download_cache(downloaded_files)

    logging.info(
        f"Completed update check. {updated_mods} out of {total_mods} mods were updated in the cache."
    )