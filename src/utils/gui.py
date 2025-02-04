import re
from datetime import datetime
import logging
from tkinter import ttk, messagebox
import tkinter as tk
from typing import Optional

logger = logging.getLogger(__name__)


def _create_scrollable_frame(popup):
    """Create and return a scrollable frame for the popup."""
    container = ttk.Frame(popup)
    container.pack(fill="both", expand=True)

    canvas = tk.Canvas(container)  # Use tk.Canvas here
    scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
    scrollable_frame = ttk.Frame(canvas)

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    return scrollable_frame

def _close_popup(popup, download_button):
    """Handle closing the popup and re-enabling the download button."""
    download_button.config(state="normal")
    popup.destroy()

def _clean_description(description):
    """
    Clean the description by removing unwanted HTML tags, formatting codes, and markdown-like tags.
    """
    if not description:
        return ""

    # Remove HTML tags (e.g., <br>, <p>, etc.)
    description = re.sub(r"<.*?>", "", description)

    # Remove color tags like [color=#FFFF00], [color=red]
    description = re.sub(r"\[color=.*?\]", "", description)

    # Remove closing color tags like [/color]
    description = re.sub(r"\[/color\]", "", description)

    # Remove generic [tags], e.g., [b], [i], [link=url] and their closing counterparts
    description = re.sub(r"\[.*?\]", "", description)

    # Replace <br/> or variations of <br> with a space
    description = description.replace("<br/>", " ").replace("<br>", " ")

    # Replace encoded backslashes (e.g., &#92;) with forward slashes
    description = description.replace("&#92;", "/")

    # Remove any excessive whitespace
    description = re.sub(r"\s+", " ", description)

    # Strip leading/trailing spaces and newlines
    return description.strip()

def _format_timestamp(timestamp):
    """Convert a timestamp to a human-readable date format."""
    try:
        return datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
    except (ValueError, TypeError):
        return "Unknown Date"

def _install_progress_window():
    """Creates and displays a small progress window for extracting mods."""
    progress_window = tk.Toplevel()
    progress_window.title("Installing Mods")
    progress_window.geometry("300x100")
    progress_window.resizable(False, False)

    label = ttk.Label(progress_window, text="Installing selected mod(s)...", font=("Arial", 11))
    label.pack(pady=20)

    progress_bar = ttk.Progressbar(progress_window, mode="indeterminate")
    progress_bar.pack(fill=tk.X, padx=20, pady=10)
    progress_bar.start(10)  # Simulates loading

    return progress_window, label

def _group_mods_by_category(mods):
    """Group mods by category."""
    categories = {}
    for mod in mods:
        category = mod.get("category", "Uncategorized")
        if category not in categories:
            categories[category] = []
        categories[category].append(mod)
    return categories

def _configure_treeview_tags(results_tree):
    """Configure Treeview tags for different statuses and make separators stand out more."""
    results_tree.tag_configure("update_available", background="yellow", font=("Arial", 9, "bold"))
    results_tree.tag_configure("up_to_date", background="lightgreen")
    results_tree.tag_configure("not_downloaded", background="lightgray")

    # Enhanced separator with bold, italic text and gray background
    results_tree.tag_configure("separator", background="gray", foreground="lightgray", font=("Arial", 11, "bold italic"))

def _compare_mod_status(mod_details, downloaded_files):
    mod_name = mod_details.get("name", "Unknown")

    # Check all files for the mod in `downloaded_files`
    mod_files = [
        file_metadata for file_metadata in downloaded_files.values()
        if file_metadata.get("mod_name") == mod_name
    ]

    if not mod_files:
        # If there are no files for this mod
        return "Not Downloaded"

    # Check if any file under the mod has matching timestamps
    for file in mod_files:
        if file["latest_downloaded_timestamp"] == file["latest_uploaded_timestamp"]:
            return "Up-to-date"

    # If none of the files have matching timestamps, return "Update Available"
    return "Update Available"

def _show_update_popup(root):
    """Show a popup that indicates that mod updates are being checked."""
    popup = tk.Toplevel(root)
    popup.title("Checking for Updates")
    popup.resizable(False, False)
    popup.attributes('-topmost', True)  # Make the popup topmost
    label = tk.Label(popup, text="Checking for mod updates, please wait...", padx=20, pady=20)
    label.pack()
    # Center the popup on the screen (optional)
    popup.update_idletasks()
    x = (popup.winfo_screenwidth() - popup.winfo_reqwidth()) // 2
    y = (popup.winfo_screenheight() - popup.winfo_reqheight()) // 2
    popup.geometry(f"+{x}+{y}")
    return popup

def _update_progress_bar(progress_bar, progress_label, percent_complete, downloaded_mb, total_mb):
    """Update the progress bar and progress label."""
    progress_bar["value"] = percent_complete  # Set progress bar value (0 to 100)
    progress_label.config(
        text=f"Downloaded {downloaded_mb:.2f} MB out of {total_mb:.2f} MB ({percent_complete:.2f}%)"
    )
    progress_label.update_idletasks()

def _get_selected_mod(results_tree: ttk.Treeview) -> Optional[tuple]:
    """Get the selected mod ID and name from the Treeview, ignoring category separators."""
    selected = results_tree.selection()
    if not selected:
        messagebox.showinfo("Info", "Please select a mod to download.")
        return None

    selected_item = results_tree.item(selected[0], "values")[0]

    # Ignore category separators
    if selected_item.startswith("────────────") and selected_item.endswith("────────────"):
        logging.info("Ignoring category separator.")
        return None

    try:
        mod_id = int(selected_item.split("ID:")[-1].strip())
        mod_name = selected_item.split(" - ID:")[0].strip()
        return mod_id, mod_name
    except ValueError:
        messagebox.showerror("Error", "Invalid mod ID. Please select a valid mod.")
        return None

def _sort_treeview(tree, col, reverse):
    """Sort the treeview column when the user clicks the header."""
    data = [(tree.set(k, col), k) for k in tree.get_children("")]

    # Convert to appropriate type
    if col == "Size":
        data.sort(key=lambda t: float(t[0].split()[0]) if t[0] != "Unknown" else 0,
                  reverse=reverse)  # Sort by file size (in MB)
    elif col == "Uploaded by Author":
        data.sort(key=lambda t: t[0] if t[0] != "Unknown" else "", reverse=reverse)  # Sort by timestamp
    else:
        data.sort(reverse=reverse)  # Alphabetical sort

    for index, (_, k) in enumerate(data):
        tree.move(k, "", index)

    tree.heading(col, command=lambda: _sort_treeview(tree, col, not reverse))  # Toggle sort direction

def _initialize_main_window():
    """Creates the main Tkinter window."""
    root = tk.Tk()
    root.title("Cyberpunk Mod Manager")
    root.geometry("1000x800")  # Fixed initial window size
    root.minsize(800, 500)  # Prevent shrinking too much
    root.maxsize(1920, 1080)  # Reasonable max size
    root.resizable(True, True)  # Allow resizing
    return root

def _create_tabs(root):
    """Creates tabbed interface and returns relevant frames."""
    notebook = ttk.Notebook(root)
    mods_frame = ttk.Frame(notebook)
    files_frame = ttk.Frame(notebook)

    notebook.add(mods_frame, text="Tracked Mods")
    notebook.add(files_frame, text="Downloaded Files")
    notebook.pack(expand=True, fill="both")

    return notebook, mods_frame, files_frame
