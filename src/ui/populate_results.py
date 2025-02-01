from src.utils import _group_mods_by_category, _configure_treeview_tags, _compare_mod_status


def populate_results_list(results_tree, mods, downloaded_files):
    """Populate the Treeview with mod details, including their statuses."""
    results_tree.delete(*results_tree.get_children())  # Clear the Treeview

    if not mods:
        results_tree.insert("", "end", values=("No mods found.", ""))
        return

    # Configure tags for different statuses
    _configure_treeview_tags(results_tree)

    # Group mods by category
    categories = _group_mods_by_category(mods)

    for category, mods_in_category in categories.items():
        # Add category separator
        results_tree.insert("", "end", values=(f"────────────{category}────────────", ""), tags=("separator",))

        for mod in mods_in_category:
            mod_name = mod.get("name", "Unknown")
            mod_id = mod.get("mod_id", "Unknown ID")

            # Calculate mod status
            status = _compare_mod_status(mod, downloaded_files.get("files", {}))

            # Determine the tag based on status
            tag = {
                "Update Available": "update_available",
                "Up-to-date": "up_to_date",
                "Not Downloaded": "not_downloaded",
            }.get(status, "not_downloaded")

            # Insert the mod into the Treeview with the appropriate tag
            results_tree.insert("", "end", values=(f"{mod_name} - ID: {mod_id}", status), tags=(tag,))
