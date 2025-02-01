import logging
import re
from datetime import datetime

from src.utils import _save_download_cache, _parse_file_timestamp, _format_timestamp

logger = logging.getLogger(__name__)

def track_download_metadata(file_name, file_details, downloaded_files, files, mod_name, mod_id, file_size):
    """Update metadata for downloaded files, ensuring only exact base name matches are replaced."""
    logging.info(f"🔍 Processing metadata update for file: {file_name}")

    base_file_name = re.sub(r'\_\d{8}_\d{6}', '', file_name).rsplit(".", 1)[0]  # Remove _YYYYMMDD_HHMMSS
    logging.info(f"Base file name: {base_file_name}")

    existing_files = downloaded_files.get("files", {})

    existing_files = {
        key: value for key, value in existing_files.items()
        if key.split("_")[0] != base_file_name
    }

    parsed_timestamp = _parse_file_timestamp(file_name)
    latest_timestamp = max(
        (file.get("uploaded_timestamp", 0) for file in files),
        default=0,
    )

    is_outdated = parsed_timestamp and latest_timestamp and parsed_timestamp < datetime.utcfromtimestamp(latest_timestamp)

    existing_files[file_name] = {
        "mod_name": mod_name,
        "mod_id": mod_id,
        "file_size": file_size,
        "latest_downloaded_timestamp": datetime.strftime(parsed_timestamp, "%Y-%m-%d %H:%M:%S") if parsed_timestamp else "Unknown",
        "latest_uploaded_timestamp": _format_timestamp(latest_timestamp) if latest_timestamp > 0 else "Unknown",
    }

    logging.info(f"Updated metadata entry for file: {base_file_name}")

    downloaded_files["files"] = existing_files
    _save_download_cache(downloaded_files)

    return is_outdated

