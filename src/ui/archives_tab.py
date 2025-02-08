from tkinter import ttk

from src.utils import _list_installed_archives, _rename_archive


def create_archive_tab(notebook):
    """
    Create the Installed Archives tab in the UI.
    This tab is populated solely from the JSON file's list of installed .archive files.
    """
    frame = ttk.Frame(notebook)
    notebook.add(frame, text="Installed Archives")

    # Use a simple Treeview that displays one column (the file name).
    archives_tree = ttk.Treeview(frame, columns=("File Name",), show="tree")
    archives_tree.pack(expand=True, fill="both", padx=10, pady=10)

    # Get the list of .archive files from the JSON.
    archives = _list_installed_archives()
    for archive in archives:
        archives_tree.insert("", "end", text=archive)

    button_frame = ttk.Frame(frame)
    button_frame.pack(fill="x", pady=5)

    btn_rename = ttk.Button(button_frame, text="Rename File",
                            command=lambda: _rename_archive(archives_tree))
    btn_rename.pack(side="left", padx=5)

    return frame, archives_tree
