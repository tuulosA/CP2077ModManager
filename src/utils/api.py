import logging
import os
import re
from pathlib import Path
from typing import Optional, Tuple

from src.api import get_mod_files, get_mod_details

logger = logging.getLogger(__name__)

def _fetch_mod_details(game: str, mod_id: int) -> dict:
    """Fetch mod details for given mod ID."""
    mod_details = get_mod_details(game, mod_id)
    if not mod_details:
        logging.error(f"Failed to fetch mod details for mod ID {mod_id}. Cannot proceed with download.")
    return mod_details

def _fetch_all_mod_files(game: str, mod_id: int) -> list:
    """Fetch all files for the mod to determine their latest timestamps."""
    files = get_mod_files(game, mod_id)
    if not files:
        logging.error(f"No files available for mod ID {mod_id}. Cannot proceed with download.")
    return files

def _get_file_details(file_name: str, file_details: dict, settings: dict) -> Tuple[Optional[str], str, str]:
    """Fetches mod details and determines the correct mod path."""
    mod_id = file_details.get("mod_id")
    mod_name = file_details.get("mod_name", "Unknown")

    mod_details = _fetch_mod_details("cyberpunk2077", mod_id) or {}
    mod_category = mod_details.get("category", "Uncategorized").strip()

    # 🔹 Remove timestamp suffix (_YYYYMMDD_HHMMSS.zip) from filename
    subdir_name = re.sub(r"_\d{8}_\d{6}\.[a-zA-Z0-9]+$", "", str(file_name))  # Ensure file_name is str

    mod_base_dir = Path(settings["output_dir"]) / mod_category / mod_name / subdir_name
    mod_path = mod_base_dir / file_name  # Use `/` operator for paths

    # Ensure file_name is str before using string methods
    file_name_str = str(file_name)
    tracking_key = file_name_str if file_name_str.endswith(".zip") else file_name_str.replace(".zip", ".rar")

    return str(mod_path) if mod_path.exists() else None, mod_name, tracking_key