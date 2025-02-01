from src.utils import _load_download_cache, _load_installed_files, _find_matching_installed_file


def create_file_list(files_tree):
    """Populate the Downloaded Files tab with sorted data."""
    files_tree.delete(*files_tree.get_children())  # Clear previous entries

    downloaded_files = _load_download_cache()
    installed_files = _load_installed_files()  # Load installed mods tracking
    files_data = []

    for file_name, metadata in downloaded_files.get("files", {}).items():
        mod_name = metadata.get("mod_name", "Unknown")
        file_size = metadata.get("file_size", 0) / (1024 * 1024)  # Convert to MB
        uploaded_time = metadata.get("latest_uploaded_timestamp", "Unknown")

        # Determine installation status, ignoring file extensions
        install_status = "Installed" if _find_matching_installed_file(file_name, installed_files) else "Not Installed"

        files_data.append((mod_name, file_name, f"{file_size:.2f} MB", uploaded_time, install_status))

    files_data.sort(key=lambda x: x[0].lower())

    for row in files_data:
        files_tree.insert("", "end", values=row)
