import os
from datetime import datetime

import requests


def _download_file(url, file_path, progress_callback=None):
    """Download a file from the given URL to the specified file path."""
    response = requests.get(url, stream=True)
    total_size = int(response.headers.get('Content-Length', 0))  # Total size in bytes
    downloaded_size = 0

    with open(file_path, "wb") as file:
        for chunk in response.iter_content(chunk_size=1024 * 1024):  # 1 MB chunks
            if chunk:
                file.write(chunk)
                downloaded_size += len(chunk)

                if progress_callback and total_size > 0:
                    percent_complete = (downloaded_size / total_size) * 100
                    progress_callback(percent_complete, downloaded_size / (1024 * 1024), total_size / (1024 * 1024))


def _prepare_file_for_download(file_details: dict, mod_base_dir: str) -> tuple:
    """Prepare filename, download path, and directory for a single file."""
    file_name_base = file_details.get("name", f"file_{file_details.get('id', 'unknown')}")
    uploaded_time = file_details.get("uploaded_timestamp", None)

    if uploaded_time:
        formatted_time = datetime.utcfromtimestamp(uploaded_time).strftime("%Y%m%d_%H%M%S")
        file_name = f"{file_name_base}_{formatted_time}.zip"
    else:
        file_name = f"{file_name_base}.zip"

    mod_specific_dir = os.path.join(mod_base_dir, file_name_base)
    os.makedirs(mod_specific_dir, exist_ok=True)

    file_path = os.path.join(mod_specific_dir, file_name)
    return file_name, file_path, mod_specific_dir