import tkinter as tk
from tkinter import ttk, Toplevel

from src.core import delete_selected_file


def show_modify_files_popup(mod_name, mod_files, downloaded_files, results_tree, progress_label, settings, files_tree):
    """Show a popup window allowing users to delete downloaded files."""
    popup = Toplevel()
    popup.title(f"Modify Files - {mod_name}")
    popup.geometry("450x400")

    tk.Label(popup, text=f"Modify Files for '{mod_name}'", font=("Arial", 12, "bold")).pack(pady=10)

    listbox = tk.Listbox(popup, selectmode=tk.SINGLE, width=50, height=10)
    for file_name in mod_files.keys():
        listbox.insert(tk.END, file_name)
    listbox.pack(pady=10)

    delete_button = ttk.Button(popup, text="Delete Selected File", command=lambda: delete_selected_file(
        listbox, mod_name, mod_files, downloaded_files, popup, results_tree, progress_label, settings, files_tree
    ))
    delete_button.pack(pady=10)

    ttk.Button(popup, text="Close", command=popup.destroy).pack(pady=5)
    popup.grab_set()