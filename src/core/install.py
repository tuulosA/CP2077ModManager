import zipfile
from tkinter import messagebox

from src.utils import _list_files_recursive, _extract_zip, _extract_rar


def extract_archive(file_path, extract_to):
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
            messagebox.showerror("Error", f"Failed to extract '{file_path}': Unsupported or corrupted file.")
            return [], None

    # Get list of files **after extraction** and track only newly created files
    after_extraction = set(_list_files_recursive(extract_to))
    extracted_files = list(after_extraction - before_extraction)

    return extracted_files, detected_format

