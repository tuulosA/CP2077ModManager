from src.utils import _group_mods_by_category, _configure_treeview_tags, _compare_mod_status


def populate_results_list(results_tree, mods, downloaded_files):
    """Populate the Treeview with mod details, keeping categories sorted alphabetically and mods sorted within categories."""
    results_tree.delete(*results_tree.get_children())  # Clear the Treeview

    if not mods:
        results_tree.insert("", "end", values=("No mods found.", ""))
        return

    # Configure tags for different statuses
    _configure_treeview_tags(results_tree)

    # Group mods by category
    categories = _group_mods_by_category(mods)

    # Sort categories alphabetically
    sorted_categories = sorted(categories.keys(), key=lambda c: c.lower())

    for category in sorted_categories:
        mods_in_category = categories[category]

        # Sort mods alphabetically within each category
        sorted_mods = sorted(mods_in_category, key=lambda m: m.get("name", "").lower())

        # Create a centered category separator
        category_text = f"────────────{category.upper()}────────────"
        results_tree.insert("", "end", values=(category_text.center(50), ""), tags=("separator",))

        for mod in sorted_mods:
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
