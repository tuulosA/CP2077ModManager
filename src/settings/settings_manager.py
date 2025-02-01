import os
import json
import logging

from src.config import Config


logger = logging.getLogger(__name__)


def ensure_directories(settings):
    """Ensure output directory exists and validate game installation."""

    game_installation_dir = settings.get("game_installation_dir", "")
    output_dir = settings.get("output_dir", "")

    # Check if the default game installation exists
    if not os.path.exists(game_installation_dir):
        logging.warning(f"Cyberpunk 2077 is not installed at {Config.DEFAULT_GAME_DIR}. Leaving output directory empty.")
        settings["game_installation_dir"] = ""
        settings["output_dir"] = ""
    else:
        logging.debug(f"Cyberpunk 2077 installation detected: {game_installation_dir}")

        # Ensure the Mods folder exists inside the game directory
        mods_dir = os.path.join(game_installation_dir, "Mods")
        if not os.path.exists(mods_dir):
            logging.info(f"Mods directory not found. Creating: {mods_dir}")
            os.makedirs(mods_dir, exist_ok=True)

        settings["output_dir"] = mods_dir  # Set output_dir to Mods folder

    save_settings(settings)


def load_settings():
    """Load settings from the json/settings.json file, or return default settings if it doesn't exist."""
    if os.path.exists(Config.SETTINGS_FILE):
        with open(Config.SETTINGS_FILE, 'r') as f:
            settings = json.load(f)
            logging.debug(f"Loaded settings: {settings}")
            return settings

    logging.debug(f"Settings file not found. Using default settings: {Config.DEFAULT_SETTINGS}")
    return Config.DEFAULT_SETTINGS


def save_settings(settings):
    """Save settings to json/settings.json file."""
    with open(Config.SETTINGS_FILE, 'w') as f:
        json.dump(settings, f, indent=4)
    logging.debug(f"Saved settings: {settings}")
