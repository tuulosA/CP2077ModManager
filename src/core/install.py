import logging
import zipfile

from src.utils import _list_files_recursive, _extract_zip, _extract_rar

logger = logging.getLogger(__name__)


def extract_and_track_files(file_name, mod_path, game_install_dir):
    """Extracts and tracks newly created files after extraction."""
    logging.info(f"📂 Extracting '{file_name}' to {game_install_dir}...")

    before_extraction = set(_list_files_recursive(game_install_dir))  # ✅ Track correct folder

    extracted_files, detected_format = _extract_archive(mod_path, game_install_dir)

    after_extraction = set(_list_files_recursive(game_install_dir))  # ✅ Track correct folder
    extracted_files = list(after_extraction - before_extraction)  # ✅ Only track new files

    logging.info(f"✅ Tracked extracted files: {extracted_files}")

    return extracted_files if extracted_files else [], detected_format

def _extract_archive(file_path, extract_to):
    extracted_files = []
    detected_format = None

    # Get list of files **before extraction** to track only new files
    before_extraction = set(_list_files_recursive(extract_to))

    try:
        # Always try ZIP first, even if it might be a RAR file
        extracted_files = _extract_zip(file_path, extract_to)
        detected_format = "zip"

    except zipfile.BadZipFile:
        try:
            extracted_files = _extract_rar(file_path, extract_to)
            detected_format = "rar"
        except Exception as e:
            return [], None

    # Get list of files **after extraction** and track only newly created files
    after_extraction = set(_list_files_recursive(extract_to))
    extracted_files = list(after_extraction - before_extraction)

    return extracted_files, detected_format
