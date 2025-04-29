import sys
import time

from settings_ui import SettingsWindow
import tkinter as tk
from tkinter import ttk
from tkinter import font
import os
import json
from config import KEYBINDS, COLORS
from tkhtmlview import HTMLLabel
from pyboy.pyboy import PyBoy
from screen_recording import VideoCreator
import numpy as np
import markdown


class GameBoyLauncher:
    def __init__(self, root):
        self.root = root
        self.root.title("Game Boy ROM Launcher")
        self.root.geometry("1000x700")
        self.root.configure(bg=COLORS["gameboy_grey"])
        self.rom_directory = None
        self.keybinds = KEYBINDS.copy()
        self.screen_record = False
        self.remapped_keys = None
        self.open_windows = {}
        self.video_creator = None
        self.recording_directory = None

        self.style = ttk.Style()
        self.style.configure('Hacker.TFrame', background=COLORS["gameboy_grey"])
        self.style.configure('Hacker.TButton',
                             background=COLORS["button_grey"],
                             foreground=COLORS["gameboy_grey"],
                             font=('Courier', 12, 'bold'),
                             padding=10)
        self.style.configure('Hacker.TLabel',
                             background=COLORS["gameboy_grey"],
                             foreground=COLORS["text_blue"],
                             font=('Courier', 12))

        self.main_frame = ttk.Frame(root, padding="20", style='Hacker.TFrame')
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        title_font = font.Font(family='Courier', size=24, weight='bold')
        self.title_label = tk.Label(self.main_frame,
                         text="GAME BOY LAUNCHER v1.0",
                         font=title_font,
                         fg=COLORS["text_blue"],
                         bg=COLORS["gameboy_grey"])
        self.title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))

        search_frame = ttk.Frame(self.main_frame, style='Hacker.TFrame')
        search_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))

        search_label = ttk.Label(search_frame, text="SEARCH:", style='Hacker.TLabel')
        search_label.pack(side=tk.LEFT, padx=(0, 10))

        self.search_var = tk.StringVar()
        self.search_var.trace_add('write', self.filter_games)
        search_entry = tk.Entry(search_frame,
                                textvariable=self.search_var,
                                font=('Courier', 12),
                                bg=COLORS["button_grey"],
                                fg=COLORS["gameboy_grey"],
                                insertbackground=COLORS["text_blue"],
                                relief=tk.FLAT,
                                width=50)
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.stats_frame = ttk.Frame(self.main_frame, style='Hacker.TFrame')
        self.stats_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        self.stats_label = ttk.Label(self.stats_frame,
                                     text="LOADING ROMS...",
                                     style='Hacker.TLabel')
        self.stats_label.pack(side=tk.LEFT)

        self.rom_listbox = tk.Listbox(self.main_frame,
                                      width=70,
                                      height=20,
                                      font=('Courier', 14, 'bold'),
                                      bg=COLORS["screen_green"],
                                      fg=COLORS["text_blue"],
                                      selectmode=tk.SINGLE,
                                      selectbackground=COLORS["highlight_green"],
                                      selectforeground=COLORS["screen_green"],
                                      relief=tk.FLAT)

        self.rom_listbox.grid(row=3, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))

        control_frame = ttk.Frame(self.main_frame, style='Hacker.TFrame')
        control_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=20)

        launch_button = tk.Button(control_frame,
                                  text=f"LAUNCH\nGAME",
                                  command=self.launch_game,
                                  font=('Courier', 14, 'bold'),
                                  bg=COLORS["button_magenta"],
                                  fg=COLORS["black"],
                                  activebackground=COLORS["green"],
                                  activeforeground=COLORS["white"],
                                  relief=tk.RAISED,
                                  width=6,
                                  height=3,
                                  bd=5,
                                  highlightthickness=0)
        launch_button.pack(side=tk.RIGHT, padx=10)

        # Add this just before the 'Launch Game' button in the control_frame

        readme_button = tk.Button(control_frame,
                                  text=f"README",
                                  command=self.open_readme,
                                  font=('Courier', 14, 'bold'),
                                  bg=COLORS["button_magenta"],
                                  fg=COLORS["black"],
                                  activebackground=COLORS["green"],
                                  activeforeground=COLORS["white"],
                                  relief=tk.RAISED,
                                  width=6,
                                  height=3,
                                  bd=5,
                                  highlightthickness=0)
        readme_button.pack(side=tk.RIGHT, padx=10)  # Place the button to the left of the 'Launch Game' button

        center_buttons_frame = tk.Frame(control_frame, bg=COLORS["gameboy_grey"])
        center_buttons_frame.pack(expand=True, padx=(80, 0))

        settings_frame = tk.Frame(center_buttons_frame, bg=COLORS["gameboy_grey"])
        settings_frame.pack(side=tk.LEFT, padx=10)

        power_button_frame = tk.Frame(center_buttons_frame, bg=COLORS["gameboy_grey"])
        power_button_frame.pack(side=tk.LEFT, padx=10)

        settings_button = tk.Button(settings_frame,
                                    width=10,
                                    height=1,
                                    font=('Courier', 8, 'bold'),
                                    relief=tk.RAISED,
                                    bg=COLORS["button_grey"],
                                    fg=COLORS["text_blue"],
                                    command=self.open_settings_window)
        settings_button.pack()

        settings_label = tk.Label(settings_frame,
                                  text="Settings",
                                  font=('Courier', 8, 'bold'),
                                  bg=COLORS["gameboy_grey"],
                                  fg=COLORS["text_blue"])
        settings_label.pack(pady=(5, 0))

        power_button = tk.Button(power_button_frame,
                                 width=10,
                                 height=1,
                                 font=('Courier', 8, 'bold'),
                                 relief=tk.RAISED,
                                 bg=COLORS["button_grey"],
                                 fg=COLORS["text_blue"],
                                 command=self.close_window)
        power_button.pack()

        power_label = tk.Label(power_button_frame,
                               text="Exit",
                               font=('Courier', 8, 'bold'),
                               bg=COLORS["gameboy_grey"],
                               fg=COLORS["text_blue"])
        power_label.pack(pady=(5, 0))

        self.status_var = tk.StringVar()
        self.status_var.set("SYSTEM READY")
        status_label = ttk.Label(self.main_frame,
                                 textvariable=self.status_var,
                                 style='Hacker.TLabel')
        status_label.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))

        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.rowconfigure(3, weight=1)

        self.rom_listbox.bind('<Double-Button-1>', lambda e: self.launch_game())

        self.games = []
        self.load_roms() # changed

    def close_window(self):
        self.root.destroy()

    def open_settings_window(self):
        # Check if the settings window is already open
        if "settings" not in self.open_windows or not self.open_windows["settings"].top.winfo_exists():
            settings_window = SettingsWindow(self)
            self.open_windows["settings"] = settings_window  # Store the window

            # When the window is closed, remove it from open_windows
            def on_close():
                settings_window.top.destroy()
                if "settings" in self.open_windows:
                    del self.open_windows["settings"]

            settings_window.top.protocol("WM_DELETE_WINDOW", on_close)
        else:
            # Focus the existing window
            self.open_windows["settings"].top.lift()

    def load_roms(self):
        self.games.clear()
        self.rom_listbox.delete(0, tk.END)
        
        if self.rom_directory is None:
            self.rom_listbox.insert(tk.END, "Please select a ROM directory in Settings.")
            self.stats_label.configure(text="NO ROM DIRECTORY SELECTED")
            self.status_var.set("NO ROM DIRECTORY SELECTED")
            return
            
        try:
            if not self.rom_directory.exists():
                self.rom_listbox.insert(tk.END, "ROM directory not found. Please select a valid directory.")
                self.stats_label.configure(text="ROM DIRECTORY NOT FOUND")
                self.status_var.set("ROM DIRECTORY NOT FOUND")
                return
                
            # Find all .gb files in the directory
            rom_files = list(self.rom_directory.glob("*.gb"))
            if not rom_files:
                self.rom_listbox.insert(tk.END, "No ROM files found in the selected directory.")
                self.stats_label.configure(text="NO ROMS FOUND")
                self.status_var.set("NO ROMS FOUND")
                return
                
            # Add found ROMs to the list
            for file in rom_files:
                self.games.append(file.name)
            self.games.sort()
            
            # Update the UI
            self.update_listbox()
            self.update_stats()
            self.status_var.set("ROMS LOADED SUCCESSFULLY")
            
        except Exception as e:
            self.rom_listbox.insert(tk.END, f"Error loading ROMs: {str(e)}")
            self.stats_label.configure(text="ERROR LOADING ROMS")
            self.status_var.set("ERROR LOADING ROMS")

    def update_stats(self):
        self.stats_label.configure(text=f"AVAILABLE ROMS: {len(self.games)}")

    def update_listbox(self):
        self.rom_listbox.delete(0, tk.END)
        for game in self.games:
            self.rom_listbox.insert(tk.END, f" {game}")
        self.update_stats()

    def filter_games(self, *args):
        search_term = self.search_var.get().lower()
        self.rom_listbox.delete(0, tk.END)
        for game in self.games:
            if search_term in game.lower():
                self.rom_listbox.insert(tk.END, f" {game}")
        self.update_stats()

    def update_remapped_keys(self, new_keys, reset=False):
        if reset:
            self.remapped_keys = None
        else:
            self.remapped_keys = new_keys

    def launch_game(self):
        """Launch the selected game with PyBoy and record screen if enabled."""
        selection = self.rom_listbox.curselection()
        if len(selection) == 0:
            self.status_var.set("NO GAME SELECTED")
            return
            
        try:
            # Get the selected game name from the listbox
            selected_game = self.rom_listbox.get(selection[0]).strip()
            
            # Find the matching game in our games list
            matching_game = None
            for game in self.games:
                if game == selected_game:
                    matching_game = game
                    break
            
            if not matching_game:
                self.status_var.set(f"GAME NOT FOUND: {selected_game}")
                return
                
            if not self.rom_directory:
                self.status_var.set("NO ROM DIRECTORY SET")
                return
                
            rom_path = self.rom_directory / matching_game
            
            if not rom_path.exists():
                self.status_var.set(f"ROM NOT FOUND: {matching_game}")
                return

            self.status_var.set(f"LAUNCHING {matching_game.upper()}...")
            self.root.update()

            try:
                if self.remapped_keys:
                    keybinds = json.dumps(self.remapped_keys)
                    pyboy = PyBoy(str(rom_path), keybinds=keybinds)
                else:
                    pyboy = PyBoy(str(rom_path))

                if self.screen_record and self.recording_directory:
                    output_filename = f"{matching_game.replace('.gb', '').replace(' ', '_')}_{time.strftime('%m.%d.%Y_%H.%M.%S')}.mp4"
                    output_path = os.path.join(self.recording_directory, output_filename)
                    self.video_creator = VideoCreator(pyboy, output_path=output_path)
                elif self.screen_record and not self.recording_directory:
                    self.status_var.set("SCREEN RECORDING DIRECTORY NOT SET")
                    self.screen_record = False
                else:
                    self.video_creator = None

                while pyboy.tick():
                    if self.screen_record and self.video_creator:
                        self.video_creator.video_frames.append(np.array(pyboy.screen.image))
                        self.video_creator.audio_frames.append(pyboy.sound.ndarray.copy())
                pyboy.stop()

                if self.screen_record and self.video_creator:
                    self.video_creator.merge_av()
                    
                self.status_var.set("GAME CLOSED")

            except Exception as e:
                self.status_var.set(f"LAUNCH FAILURE: {str(e)}")
                
        except Exception as e:
            self.status_var.set("ERROR LAUNCHING GAME")

    def open_readme(self):
        # Create a new top-level window for the README
        readme_window = tk.Toplevel(self.root)
        readme_window.title("README")
        readme_window.geometry("1350x900")

        # Create a frame for holding the HTMLLabel
        frame = ttk.Frame(readme_window)
        frame.pack(expand=True, fill=tk.BOTH)

        # Read the README file and convert it to HTML using markdown library
        try:
            if hasattr(sys, '_MEIPASS'):
                # Running as bundled executable
                readme_path = os.path.join(sys._MEIPASS, "README.md")
            else:
                # Running as script
                readme_path = "README.md"

            with open(readme_path, "r", encoding="utf-8") as readme_file:  # Explicitly specify UTF-8
                readme_content = readme_file.read()
                html_content = markdown.markdown(readme_content)
                html_label = HTMLLabel(frame, html=html_content)
                html_label.pack(expand=True, fill=tk.BOTH)

        except FileNotFoundError:
            error_label = tk.Label(frame, text="README file not found.", fg="red")
            error_label.pack(expand=True)
        except Exception as e:
            print(f"Error in open_readme: {e}")
            error_label = tk.Label(frame, text=f"Error displaying README: {e}", fg="red")
            error_label.pack(expand=True)


if __name__ == "__main__":
    root = tk.Tk()
    app = GameBoyLauncher(root)
    root.mainloop()

# some code snippets added by ai
