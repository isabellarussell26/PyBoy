import tkinter as tk
from functools import partial
from config import KEYBINDS, TKINTER_TO_SDL2, COLORS


class KeybindsConfig:
    def __init__(self, parent, keybinds):
        self.parent = parent
        self.top = tk.Toplevel(parent.root)
        self.top.title("Keybind Settings")

        # Get the position of the parent window
        parent_x = self.parent.root.winfo_x()
        parent_y = self.parent.root.winfo_y()

        # Adjust the window position based on the parent window's position
        offset_x = 60
        offset_y = 60

        self.top.geometry(f"350x550+{parent_x+offset_x}+{parent_y+offset_y}")  # Slightly wider for two buttons
        self.top.configure(bg=COLORS["gameboy_grey"])

        self.keybinds = keybinds
        self.create_widgets()

    def create_widgets(self):
        self.buttons = {}
        self.top.grid_rowconfigure(0, minsize=25)

        row = 1
        for action, key in self.keybinds.items():
            # Label for each action
            label = action.replace("PRESS_ARROW_", "").replace("PRESS_BUTTON_", "").upper()
            tk.Label(self.top,
                     text=label,
                     font=("Courier", 10, "bold"),
                     bg=COLORS["gameboy_grey"],
                     fg=COLORS["text_blue"],
                     anchor="e",
                     width=12).grid(row=row, column=0, padx=10, pady=5, sticky="e")

            # Creating button for each keybind
            btn = tk.Button(self.top,
                            text=key,
                            font=("Courier", 10, "bold"),
                            bg=COLORS["button_grey"],
                            fg=COLORS["black"],
                            width=15,
                            height=2)
            # Using partial to pass both the action and the button
            btn.config(command=partial(self.rebind_key, action, btn))
            btn.grid(row=row, column=1, padx=10, pady=5)

            self.buttons[action] = btn
            row += 1

        button_frame = tk.Frame(self.top, bg=COLORS["gameboy_grey"])
        button_frame.grid(row=row, column=1, pady=10)

        # Save Button
        save_button = tk.Button(button_frame,
                                text="SAVE",
                                font=("Courier", 14, "bold"),
                                bg=COLORS["button_magenta"],
                                fg=COLORS["black"],
                                width=5,
                                height=2,
                                relief=tk.RAISED,
                                bd=5,
                                highlightthickness=0,
                                command=self.save_keybinds)
        save_button.pack(side=tk.LEFT, padx=(0, 5))

        # Reset Button
        reset_button = tk.Button(button_frame,
                                 text="RESET",
                                 font=("Courier", 14, "bold"),
                                 bg=COLORS["button_magenta"],
                                 fg=COLORS["black"],
                                 width=5,
                                 height=2,
                                 relief=tk.RAISED,
                                 bd=5,
                                 highlightthickness=0,
                                 command=self.reset_keybinds)
        reset_button.pack(side=tk.LEFT, padx=(5, 0))

    def save_keybinds(self):
        """ Function to save the keybinds to remapped_keys. """
        has_unbound = False
        for action, binding in self.keybinds.items():
            if binding == "UNBOUND":
                has_unbound = True
                btn = self.buttons.get(action)
                if btn:
                    self.flash_button(btn)

        if has_unbound:
            return  # Prevent saving if any are unbound

        if self.keybinds != KEYBINDS:
            self.convert_keybinds()
            self.parent.update_remapped_keys(self.keybinds)
            self.parent.update_keybinds_led()
        self.top.destroy()

    def reset_keybinds(self):
        self.keybinds = KEYBINDS.copy()
        self.parent.update_remapped_keys(self.keybinds, True)
        for action, key in self.keybinds.items():
            if action in self.buttons:
                self.buttons[action].config(text=key)
        self.parent.update_keybinds_led()

    def flash_button(self, btn, count=6):
        def toggle(i):
            # Toggle the button color based on index i
            current_bg = btn.cget("bg")
            btn.config(bg=COLORS["button_magenta"] if current_bg != COLORS["button_magenta"] else COLORS["button_grey"])

            # If there are more flashes left, schedule the next one
            if i < count - 1:
                self.top.after(200, toggle, i + 1)  # Schedule next toggle after 200ms

        toggle(0)  # Start with 0

    def rebind_key(self, action, btn):
        # Highlight the button by changing its background color
        btn.config(bg=COLORS["button_magenta"])  # Highlight the button
        btn.config(state="disabled")  # Disable the button to prevent further clicks

        self.top.unbind("<KeyPress>")
        self.top.unbind("<Button>")

        def capture_key(event):
            new_key = event.keysym
            if is_valid_key(new_key):
                self.update_binding(action, new_key, btn)

        def capture_mouse(event):
            new_mouse = f"Mouse{event.num}"
            self.update_binding(action, new_mouse, btn)

        self.top.bind("<KeyPress>", capture_key)
        self.top.bind("<Button>", capture_mouse)

        def is_valid_key(key):
            return key in TKINTER_TO_SDL2

    def update_binding(self, action, new_binding, btn):
        # Check if this binding is already used
        for other_action, bound_key in self.keybinds.items():
            if other_action != action and bound_key == new_binding:
                self.keybinds[other_action] = "UNBOUND"
                other_btn = self.buttons.get(other_action)
                if other_btn:
                    other_btn.config(text="UNBOUND")

        self.keybinds[action] = new_binding
        btn.config(text=new_binding)

        btn.config(bg=COLORS["button_grey"], state="normal")  # Reset color and re-enable the button
        self.top.unbind("<KeyPress>")
        self.top.unbind("<Button>")

    def convert_keybinds(self):
        self.keybinds = {
            action: TKINTER_TO_SDL2.get(key, f"UNKNOWN_{key}")
            for action, key, in self.keybinds.items()
        }
        