import tkinter as tk
from tkinter import ttk


def create_results_panel(root):
    """Create the results panel for displaying search or tracked mods using a Treeview."""
    results_frame = tk.Frame(root)
    results_frame.pack(fill="both", padx=10, pady=5, expand=True)

    # Create a Treeview widget
    columns = ("name", "status")
    results_tree = ttk.Treeview(
        results_frame,
        columns=columns,
        show="headings",
        selectmode="browse"
    )
    results_tree.heading("name", text="Mod Name")
    results_tree.heading("status", text="Status")
    results_tree.column("name", width=300, anchor="w")
    results_tree.column("status", width=150, anchor="w")

    # Add a scrollbar
    scrollbar = ttk.Scrollbar(results_frame, orient="vertical", command=results_tree.yview)
    results_tree.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side="right", fill="y")

    results_tree.pack(fill="both", expand=True, padx=5, pady=5)

    return results_tree