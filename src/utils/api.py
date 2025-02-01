import logging

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