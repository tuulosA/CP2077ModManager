from tkinter import ttk

from src.utils import _load_download_cache, _load_installed_files, _find_matching_installed_file, _sort_treeview


def create_file_list(files_frame):
    """Populate the Downloaded Files tab with a scrollable list of sorted data."""
    # Create a frame to hold the Treeview and scrollbar
    container = ttk.Frame(files_frame)
    container.pack(expand=True, fill="both", padx=10, pady=10)

    # Create the Treeview widget
    files_tree = ttk.Treeview(container, columns=("Mod Name", "File Name", "Size", "Uploaded by Author", "Status"),
                              show="headings")

    # Create vertical scrollbar and attach to the Treeview
    vsb = ttk.Scrollbar(container, orient="vertical", command=files_tree.yview)
    files_tree.configure(yscrollcommand=vsb.set)

    # Place the Treeview and scrollbar in the container using grid layout
    files_tree.grid(row=0, column=0, sticky="nsew")
    vsb.grid(row=0, column=1, sticky="ns")  # Scrollbar next to Treeview

    # Configure grid expansion
    container.columnconfigure(0, weight=1)
    container.rowconfigure(0, weight=1)

    # Define column headers
    for col in ("Mod Name", "File Name", "Size", "Uploaded by Author", "Status"):
        files_tree.heading(col, text=col, command=lambda c=col: _sort_treeview(files_tree, c, False))
        files_tree.column(col, width=200 if col != "Size" else 100, anchor="w")

    # Load downloaded files
    populate_file_list(files_tree)

    return files_tree

def populate_file_list(files_tree):
    """Populate the Treeview with sorted downloaded file data."""
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

    # Sort files alphabetically by mod name
    files_data.sort(key=lambda x: x[0].lower())

    # Insert data into Treeview
    for row in files_data:
        files_tree.insert("", "end", values=row)
