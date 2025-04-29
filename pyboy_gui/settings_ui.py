import tkinter as tk
from pathlib import Path
from tkinter import filedialog
from config import COLORS

from keybinds_window import KeybindsConfig


class SettingsWindow:
    def __init__(self, launcher, opt_to_func=None):
        self.launcher = launcher
        self.top = tk.Toplevel(launcher.root)
        self.top.title("Settings")
        self.top.configure(bg=COLORS["gameboy_grey"])
        self._screen_record_active = self.launcher.screen_record
        self.screen_record_button = None  # Initialize button variable

        title = tk.Label(self.top,
                         text="Settings",
                         font=("Courier", 16, "bold"),
                         bg=COLORS["gameboy_grey"],
                         fg=COLORS["text_blue"])
        title.pack(pady=20)

        options = [
            "Change Keybindings",
            "Change ROM Directory",
            "Toggle Screen Recording",
        ]

        # Get the position of the parent window
        parent_x = self.launcher.root.winfo_x()
        parent_y = self.launcher.root.winfo_y()

        # Adjust the window position based on the parent window's position
        offset_x = 30  # Offset from the parent window's left edge
        offset_y = 30  # Offset from the parent window's top edge

        # Set the size and position of the SettingsWindow relative to the parent window
        window_height = 100 + len(options) * 50
        self.top.geometry(f"400x{window_height}+{parent_x + offset_x}+{parent_y + offset_y}")

        # Create buttons and pack them
        for opt in options:
            opt_to_func = opt.lower().replace(" ", "_")
            opt_btn = tk.Button(self.top,
                                text=opt,
                                font=("Courier", 10, "bold"),
                                bg=COLORS["button_grey"],
                                fg=COLORS["black"],
                                width=30,
                                height=2,
                                command=lambda opt_to_func=opt_to_func: getattr(self, opt_to_func)())
            opt_btn.pack(pady=5)

            if opt_to_func == "toggle_screen_recording":
                self.screen_record_button = opt_btn
                self._update_screen_record_button_color()  # Set initial color

    def _update_screen_record_button_color(self):
        if self._screen_record_active:
            self.screen_record_button.config(bg=COLORS["button_magenta"])
        else:
            self.screen_record_button.config(bg=COLORS["button_grey"])

    def toggle_screen_recording(self):
        self._screen_record_active = not self._screen_record_active
        self.launcher.screen_record = self._screen_record_active  # Update launcher's screen_record

        if self._screen_record_active:
            directory_path = filedialog.askdirectory(
                title="Choose Save Directory for Recording"
            )
            if directory_path:
                self.launcher.recording_directory = directory_path  # Save to launcher's attribute
                print(f"Screen recording directory set to: {self.launcher.recording_directory}")
            else:
                # User cancelled, revert the state
                self._screen_record_active = False
                self.launcher.screen_record = False
                self.launcher.recording_directory = None  # Clear the directory
        else:
            self.launcher.recording_directory = None  # Clear the directory when disabled
            print("Screen recording disabled.")

        self._update_screen_record_button_color()  # Update button color

    def change_keybindings(self):
        if "keybinds" not in self.launcher.open_windows or not self.launcher.open_windows[
                                                            "keybinds"].top.winfo_exists():
            keybinds_window = KeybindsConfig(self.launcher, self.launcher.keybinds)
            self.launcher.open_windows["keybinds"] = keybinds_window

            def on_close():
                keybinds_window.top.destroy()
                if "keybinds" in self.launcher.open_windows:
                    del self.launcher.open_windows["keybinds"]

            keybinds_window.top.protocol("WM_DELETE_WINDOW", on_close)
        else:
            self.launcher.open_windows["keybinds"].top.lift()

    def change_rom_directory(self):
        directory = filedialog.askdirectory(title="Select a Directory")
        if directory:
            self.launcher.rom_directory = Path(directory)
            self.launcher.load_roms()
