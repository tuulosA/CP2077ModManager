import requests
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

from src.config import Config

logger = logging.getLogger(__name__)


def get_mod_files(game, mod_id):
    """Fetch all files for a specified mod and log file IDs."""
    url = f"{Config.BASE_URL}/games/{game}/mods/{mod_id}/files.json"
    try:
        response = requests.get(url, headers=Config.HEADERS)
        response.raise_for_status()
        data = response.json()

        # Extract files and ensure file IDs are integers
        files = data.get("files", [])
        for file in files:
            file_id = file.get("id")
            # Handle cases where file_id is a list
            if isinstance(file_id, list):
                file["id"] = file_id[0]  # Extract the first element

            file_name = file.get("name", "Unknown File")
            logging.debug(f"Mod ID {mod_id}: File ID {file['id']}, Name: {file_name}")
        return files
    except requests.RequestException as e:
        logging.error(f"Failed to fetch mod files for mod ID {mod_id}: {e}")
        return []

def get_download_link(game, mod_id, file_id):
    """Generate a download link for a specific mod file."""
    url = f"{Config.BASE_URL}/games/{game}/mods/{mod_id}/files/{file_id}/download_link.json"
    try:
        response = requests.get(url, headers=Config.HEADERS)
        response.raise_for_status()
        data = response.json()

        # Premium users get a direct download link as a list
        if isinstance(data, list) and data:
            return data[0]['URI']  # Extract the URI field for the first download link

        # For non-premium users, display a message and provide instructions
        if "error" in data and data["error"] == "You don't have permission to get download links":
            logging.warning("Non-premium users cannot download directly via the API.")
            return None
        return None
    except requests.RequestException as e:
        logging.error(f"Failed to get download link for file ID {file_id}: {e}")
        return None

def get_category_name(category_id):
    return Config.CATEGORY_MAPPING.get(category_id, "Unknown Category")

def get_mod_details(game, mod_id):
    url = f"{Config.BASE_URL}/games/{game}/mods/{mod_id}.json"
    try:
        response = requests.get(url, headers=Config.HEADERS)
        response.raise_for_status()
        mod_details = response.json()
        mod_details["category"] = get_category_name(mod_details.get("category_id"))
        return mod_details
    except requests.RequestException as e:
        logging.warning(f"Failed to fetch details for mod ID {mod_id}: {e}")
        return None

def get_file_details(game, mod_id, file_id):
    """Retrieve detailed information about a specific file."""
    url = f"{Config.BASE_URL}/games/{game}/mods/{mod_id}/files/{file_id}.json"
    try:
        response = requests.get(url, headers=Config.HEADERS)
        response.raise_for_status()
        return response.json()  # Returns detailed file information
    except requests.RequestException as e:
        logging.error(f"Failed to fetch details for file ID {file_id}: {e}")
        return None

def get_tracked_mods(game="cyberpunk2077"):
    """Fetch tracked mods and their details concurrently using ThreadPoolExecutor."""
    url = f"{Config.BASE_URL}/user/tracked_mods.json"
    try:
        response = requests.get(url, headers=Config.HEADERS)
        response.raise_for_status()
        tracked_mods = response.json()

        def fetch_mod(mod):
            mod_id = mod.get("mod_id")
            if not mod_id:
                logging.warning("Skipping mod with no ID.")
                return None

            # Fetch mod details; if unavailable, create a default dict.
            detailed_mod = get_mod_details(game, mod_id)
            if not detailed_mod:
                detailed_mod = {
                    "name": "Unknown Name",
                    "mod_id": mod_id,
                    "category": "Uncategorized",
                }

            # Fetch file details (this is optional; adjust based on your needs)
            files = get_mod_files(game, mod_id)
            logging.info(f"Fetched data for mod ID {mod_id}.")
            return detailed_mod

        detailed_mods = []
        # Use ThreadPoolExecutor to fetch each mod's details concurrently.
        with ThreadPoolExecutor() as executor:
            futures = {executor.submit(fetch_mod, mod): mod for mod in tracked_mods}
            for future in as_completed(futures):
                result = future.result()
                if result is not None:
                    detailed_mods.append(result)

        logging.info("Finished fetching tracked mods.")
        return detailed_mods

    except requests.RequestException as e:
        logging.error(f"Failed to fetch tracked mods: {e}")
        raise