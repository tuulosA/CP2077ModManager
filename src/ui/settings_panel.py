from tkinter import ttk, filedialog


def create_settings_panel(root, settings, save_settings_callback):
    """Create the settings panel for selecting directories."""

    def select_output_folder():
        folder = filedialog.askdirectory()
        if folder:
            settings["output_dir"] = folder
            save_settings_callback(settings)
            output_label.config(text=f"Output Folder: {folder}")

    def select_game_installation_folder():
        folder = filedialog.askdirectory()
        if folder:
            settings["game_installation_dir"] = folder
            save_settings_callback(settings)
            game_install_label.config(text=f"Game Installation: {folder}")

    settings_frame = ttk.LabelFrame(root, text="Settings")
    settings_frame.pack(fill="x", padx=10, pady=5)

    # Output Folder Selection
    output_label = ttk.Label(settings_frame, text=f"Output Folder: {settings.get('output_dir', 'Not Set')}")
    output_label.pack(side="top", padx=5, pady=5)
    ttk.Button(settings_frame, text="Change Output Folder", command=select_output_folder).pack(side="top", padx=5, pady=5)

    # Game Installation Folder Selection
    game_install_label = ttk.Label(settings_frame, text=f"Game Installation: {settings.get('game_installation_dir', 'Not Set')}")
    game_install_label.pack(side="top", padx=5, pady=5)
    ttk.Button(settings_frame, text="Change Game Installation Folder", command=select_game_installation_folder).pack(side="top", padx=5, pady=5)