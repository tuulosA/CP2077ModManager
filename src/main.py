import logging
from typing import Dict

from src.app import setup_file_buttons, setup_tracked_mods_tab, initialize_mod_data
from src.ui import create_file_list, create_archive_tab, create_settings_panel
from src.utils import _initialize_main_window, _create_tabs, configure_logging
from src.settings import load_settings, ensure_directories

def main(settings: Dict):
    """Initialize and run the main UI for Cyberpunk Mod Manager."""
    root = _initialize_main_window()
    notebook, mods_frame, files_frame = _create_tabs(root)

    files_tree = create_file_list(files_frame)
    archives_frame, archives_tree = create_archive_tab(notebook)

    setup_file_buttons(files_frame, files_tree, settings, archives_tree)
    create_settings_panel(root, settings, lambda s: logging.info("Settings saved"))
    results_tree, progress_label = setup_tracked_mods_tab(mods_frame, settings, files_tree)

    initialize_mod_data(root, results_tree, progress_label)

    root.mainloop()

def run():
    """Load settings, ensure directories, and start the main application."""
    configure_logging()
    settings = load_settings()
    ensure_directories(settings)
    main(settings)

if __name__ == "__main__":
    run()