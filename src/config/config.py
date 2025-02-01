import os
from src.api_key import load_api_key

class Config:
    """Configuration settings for the Nexus Mods application."""

    # Standard Cyberpunk mod folder names
    MOD_FOLDERS = {"archive", "bin", "engine", "r6", "red4ext"}

    # Get the absolute path of the main project directory (going up one level from src/)
    PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

    # Define the path for the JSON directory inside the main project directory
    JSON_DIR = os.path.join(PROJECT_ROOT, "json")

    # Define file paths for JSON caches inside the json/ subdirectory
    CACHE_FILE = os.path.join(JSON_DIR, "cached_tracked_mods.json")
    DOWNLOADED_FILES_CACHE = os.path.join(JSON_DIR, "downloaded_files.json")
    INSTALLED_FILES_PATH = os.path.join(JSON_DIR, "installed_files.json")

    # Define the settings file path inside the json/ directory
    SETTINGS_FILE = os.path.join(JSON_DIR, "settings.json")

    # Ensure the JSON directory exists
    os.makedirs(JSON_DIR, exist_ok=True)

    # Default Game Directories
    DEFAULT_GAME_DIR = "C:\\Program Files (x86)\\Steam\\steamapps\\common\\Cyberpunk 2077"
    DEFAULT_MODS_DIR = os.path.join(DEFAULT_GAME_DIR, "Mods")
    ARCHIVE_FOLDER = os.path.join(DEFAULT_GAME_DIR, "archive", "pc", "mod")

    # Valid mod folders
    VALID_MOD_FOLDERS = {"bin", "r6", "archive", "red4ext", "engine"}

    # Default settings
    DEFAULT_SETTINGS = {
        "output_dir": DEFAULT_MODS_DIR,  # Set Mods folder as the default output
        "game_installation_dir": DEFAULT_GAME_DIR
    }

    # API base URL
    BASE_URL = "https://api.nexusmods.com/v1"

    # Load API Key from external manager
    API_KEY = load_api_key()
    HEADERS = {"apikey": API_KEY}

    # Category mapping
    CATEGORY_MAPPING = {
        2: "Miscellaneous",
        3: "Armour and Clothing",
        4: "Audio",
        5: "Characters",
        6: "Crafting",
        7: "Gameplay",
        8: "User Interface",
        9: "Utilities",
        10: "Visuals and Graphics",
        11: "Weapons",
        12: "Modders Resources",
        13: "Appearance",
        14: "Vehicles",
        15: "Animations",
        16: "Locations",
        17: "Scripts"
    }
