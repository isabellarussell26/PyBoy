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
        self.keybinds_changed = False  # New variable to track keybind changes

        self.style = ttk.Style()
        self.style.theme_use('clam')

        # GUI CONFIGURE FOR MAC OS
        if sys.platform.startswith('darwin'):
            self.style.configure('MacButton.TButton',
                                 background=COLORS["button_magenta"],
                                 foreground="black",
                                 font=('Courier', 14, 'bold'),
                                 relief='raised',
                                 borderwidth=5,
                                 highlightthickness=0)
            self.style.configure('MacGreyButton.TButton',
                                 background=COLORS["button_grey"],
                                 foreground="text_blue",
                                 font=('Courier', 8, 'bold'),
                                 relief='raised',
                                 borderwidth=2,
                                 highlightthickness=0)

        # CROSS PLATFORM GUI CONFIGURATION
        self.style.configure('Hacker.TFrame', background=COLORS["gameboy_grey"], padding=10)
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
                                      height=40,
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

        center_buttons_frame = tk.Frame(control_frame, bg=COLORS["gameboy_grey"])
        center_buttons_frame.place(relx=0.5, rely=0.2, anchor=tk.CENTER, x=0, y=25)

        settings_frame = tk.Frame(center_buttons_frame, bg=COLORS["gameboy_grey"])
        settings_frame.pack(side=tk.LEFT, padx=(20, 15), pady=(0, 0))

        power_button_frame = tk.Frame(center_buttons_frame, bg=COLORS["gameboy_grey"])
        power_button_frame.pack(side=tk.LEFT, padx=(20, 80), pady=(0, 0))

        # BUTTON CONFIGURE FOR MAC OS
        if sys.platform.startswith('darwin'):

            launch_button = ttk.Button(control_frame, text=f"LAUNCH\n GAME", command=self.launch_game,
                                       style='MacButton.TButton')
            readme_button = ttk.Button(control_frame, text=f"READ\n ME", command=self.open_readme,
                                       style='MacButton.TButton')
            settings_button = ttk.Button(settings_frame, text=" Settings".ljust(10), command=self.open_settings_window,
                                         style='MacGreyButton.TButton', width=10)
            power_button = ttk.Button(power_button_frame, text="   Exit".ljust(10), command=self.close_window,
                                      style='MacGreyButton.TButton', width=10)

            launch_button.pack(side=tk.RIGHT, padx=10)
            readme_button.pack(side=tk.RIGHT, padx=10)
            settings_button.pack(fill=tk.X, expand=True)
            power_button.pack(fill=tk.X, expand=True)

        # CROSS PLATFORM BUTTON CONFIGURATION
        else:
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
            readme_button = tk.Button(control_frame,
                                      text=f"READ\nME",
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
            settings_button = tk.Button(settings_frame,
                                        width=10,
                                        height=1,
                                        font=('Courier', 8, 'bold'),
                                        relief=tk.RAISED,
                                        bg=COLORS["button_grey"],
                                        fg=COLORS["text_blue"],
                                        command=self.open_settings_window)
            power_button = tk.Button(power_button_frame,
                                     width=10,
                                     height=1,
                                     font=('Courier', 8, 'bold'),
                                     relief=tk.RAISED,
                                     bg=COLORS["button_grey"],
                                     fg=COLORS["text_blue"],
                                     command=self.close_window)

            launch_button.pack(side=tk.RIGHT, padx=10)
            readme_button.pack(side=tk.RIGHT, padx=10)
            settings_button.pack()
            power_button.pack()

        # CENTER BUTTONS (SETTINGS & "POWER")
        settings_label = tk.Label(settings_frame,
                                  text=" Settings".ljust(10),
                                  font=('Courier', 8, 'bold'),
                                  bg=COLORS["gameboy_grey"],
                                  fg=COLORS["text_blue"])
        settings_label.pack(pady=(5, 0))

        power_label = tk.Label(power_button_frame,
                               text="   Exit".ljust(10),
                               font=('Courier', 8, 'bold'),
                               bg=COLORS["gameboy_grey"],
                               fg=COLORS["text_blue"])
        power_label.pack(pady=(5, 0))

        # KEYBINDS STATUS LED AND LABEL
        self.keybinds_status_led_canvas = tk.Canvas(self.main_frame, width=17, height=17, bg=COLORS["gameboy_grey"],
                                                    highlightthickness=0)
        self.keybinds_status_led = self.keybinds_status_led_canvas.create_oval(2, 2, 15, 15, fill="red",
                                                                               outline="white", width=1)  # Initial red
        self.keybinds_status_label = ttk.Label(self.main_frame, text="KEYBINDS CHANGED", style='Hacker.TLabel')

        # SCREEN RECORDING STATUS LED AND LABEL
        self.recording_status_text = tk.StringVar()
        self.recording_status_text.set("REC:")
        self.recording_label = ttk.Label(self.main_frame,
                                         textvariable=self.recording_status_text,
                                         style='Hacker.TLabel')
        self.recording_led_canvas = tk.Canvas(self.main_frame, width=17, height=17, bg=COLORS["gameboy_grey"],
                                              highlightthickness=0)
        self.recording_led = self.recording_led_canvas.create_oval(2, 2, 15, 15, fill="red", outline="white",
                                                                   width=1)  # Initial red

        # SYSTEM STATUS WITH LED
        self.status_var = tk.StringVar()
        self.status_var.set("SYSTEM READY")

        self.status_led_canvas = tk.Canvas(self.main_frame, width=17, height=17, bg=COLORS["gameboy_grey"],
                                           highlightthickness=0)
        self.status_led = self.status_led_canvas.create_oval(2, 2, 15, 15, fill="green", outline="white",
                                                             width=1)  # Initial color green

        status_label = ttk.Label(self.main_frame,
                                 textvariable=self.status_var,
                                 style='Hacker.TLabel')

        # UPDATED GRID PLACEMENT
        self.keybinds_status_led_canvas.grid(row=5, column=0, sticky=tk.W, padx=(10, 0), pady=(0, 0))
        self.keybinds_status_label.grid(row=5, column=0, sticky=tk.W, padx=(35, 0), pady=(0, 0))
        self.recording_led_canvas.grid(row=6, column=0, sticky=tk.W, padx=(10, 0), pady=(5, 0))
        self.recording_label.grid(row=6, column=0, sticky=tk.W, padx=(35, 0), pady=(5, 0))
        self.status_led_canvas.grid(row=7, column=0, sticky=tk.W, padx=(10, 0), pady=(0, 0))
        status_label.grid(row=7, column=0, sticky=(tk.W, tk.E), padx=(35, 0), pady=(5, 0))

        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.rowconfigure(3, weight=1)

        self.rom_listbox.bind('<Double-Button-1>', lambda e: self.launch_game())

        self.games = []
        self.load_roms()
        self.update_led_status()
        self.update_recording_led()
        self.update_keybinds_led()

    def update_recording_led(self):
        if self.screen_record and self.recording_directory:
            self.recording_led_canvas.itemconfig(self.recording_led, fill="green")
            self.recording_status_text.set(f"REC: {self.recording_directory}")
        else:
            self.recording_led_canvas.itemconfig(self.recording_led, fill="red")
            self.recording_status_text.set("REC:")

    def update_keybinds_led(self):
        if self.remapped_keys:
            self.keybinds_status_led_canvas.itemconfig(self.keybinds_status_led, fill="green")
        else:
            self.keybinds_status_led_canvas.itemconfig(self.keybinds_status_led, fill="red")

    def update_led_status(self):
        if self.status_var.get() == "SYSTEM READY":
            self.status_led_canvas.itemconfig(self.status_led, fill="green")
        else:
            self.status_led_canvas.itemconfig(self.status_led, fill="red")

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
                self.update_recording_led() # Update REC status when settings close

            settings_window.top.protocol("WM_DELETE_WINDOW", on_close)
        else:
            self.open_windows["settings"].top.lift()

    def load_roms(self):
        self.games.clear()
        roms_dir = self.rom_directory
        if roms_dir is None:
            self.rom_listbox.insert(tk.END, "Please select a ROM directory in Settings.")  # changed
            self.stats_label.configure(text="NO ROM DIRECTORY SELECTED")
            self.status_var.set("NO ROM DIRECTORY")
            self.update_led_status()
        elif roms_dir.exists():
            for file in roms_dir.glob("*.gb"):
                self.games.append(file.name.strip())
            self.games.sort()
            self.update_listbox()
            self.update_stats()
            self.status_var.set("SYSTEM READY")
            self.update_led_status()
        else:
            self.status_var.set("ROM DIRECTORY NOT FOUND")
            self.rom_listbox.insert(tk.END, "ROMs directory not found.")
            self.update_led_status()

    def update_stats(self):
        self.stats_label.configure(text=f"AVAILABLE ROMS: {len(self.games)}")

    def update_listbox(self):
        self.rom_listbox.delete(0, tk.END)
        for game in self.games:
            game = game.replace('.gb', '')
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
        print(self.remapped_keys)
        """Launch the selected game with PyBoy and record screen if enabled."""
        selection = self.rom_listbox.curselection()
        if len(selection) == 0:
            return
        game_name = self.rom_listbox.get(selection[0]).strip()
        game_name = game_name + ".gb"
        rom_path = os.path.abspath(os.path.join(self.rom_directory, game_name))

        if not os.path.exists(rom_path):
            self.status_var.set("ROM NOT FOUND")
            self.update_led_status()
            return

        self.status_var.set(f"LAUNCHING {game_name.upper()}...")
        self.update_led_status()
        self.root.update()

        try:
            if self.remapped_keys:
                keybinds = json.dumps(self.remapped_keys)
                pyboy = PyBoy(rom_path, keybinds=keybinds)
            else:
                pyboy = PyBoy(rom_path)

            if self.screen_record and self.recording_directory:
                output_filename = f"{game_name.replace('.gb', '').replace(' ', '_')}_{time.strftime('%m.%d.%Y_%H.%M.%S')}.mp4"
                output_path = os.path.join(self.recording_directory, output_filename)
                self.video_creator = VideoCreator(pyboy, output_path=output_path)
            elif self.screen_record and not self.recording_directory:
                self.status_var.set("SCREEN RECORDING DIRECTORY NOT SET")
                self.screen_record = False
                self.update_led_status()
            else:
                self.video_creator = None

            while pyboy.tick():
                if self.screen_record and self.video_creator:
                    self.video_creator.video_frames.append(np.array(pyboy.screen.image))
                    self.video_creator.audio_frames.append(pyboy.sound.ndarray.copy())
            pyboy.stop()

            self.status_var.set("SYSTEM READY")  # Reset status after game closes
            self.update_led_status()

            if self.screen_record and self.video_creator:
                self.video_creator.merge_av()

        except Exception as e:
            print(f"Error launching {game_name}: {e}")
            self.status_var.set("LAUNCH FAILURE")

    def open_readme(self):

        readme_window = tk.Toplevel(self.root)
        readme_window.title("README")
        readme_window.geometry("1350x900")

        frame = ttk.Frame(readme_window)
        frame.pack(expand=True, fill=tk.BOTH)

        try:
            if hasattr(sys, '_MEIPASS'):
                readme_path = os.path.join(sys._MEIPASS, "README.md")
            else:
                readme_path = "README.md"

            with open(readme_path, "r", encoding="utf-8") as readme_file:  # Explicitly specify UTF-8
                readme_content = readme_file.read()
                import markdown
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

