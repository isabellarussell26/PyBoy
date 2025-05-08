from pathlib import Path

KEYBINDS = {
    "PRESS_ARROW_RIGHT": "Right",
    "PRESS_ARROW_LEFT": "Left",
    "PRESS_ARROW_UP": "Up",
    "PRESS_ARROW_DOWN": "Down",
    "PRESS_BUTTON_a": "a",
    "PRESS_BUTTON_b": "s",
    "PRESS_BUTTON_START": "Return",
    "PRESS_BUTTON_SELECT": "BackSpace",
}

TKINTER_TO_SDL2 = {
    'a': 'SDLK_a', 'b': 'SDLK_b', 'c': 'SDLK_c', 'd': 'SDLK_d',
    'e': 'SDLK_e', 'f': 'SDLK_f', 'g': 'SDLK_g', 'h': 'SDLK_h',
    'i': 'SDLK_i', 'j': 'SDLK_j', 'k': 'SDLK_k', 'l': 'SDLK_l',
    'm': 'SDLK_m', 'n': 'SDLK_n', 'o': 'SDLK_o', 'p': 'SDLK_p',
    'q': 'SDLK_q', 'r': 'SDLK_r', 's': 'SDLK_s', 't': 'SDLK_t',
    'u': 'SDLK_u', 'v': 'SDLK_v', 'w': 'SDLK_w', 'x': 'SDLK_x',
    'y': 'SDLK_y', 'z': 'SDLK_z',
    '0': 'SDLK_0', '1': 'SDLK_1', '2': 'SDLK_2', '3': 'SDLK_3',
    '4': 'SDLK_4', '5': 'SDLK_5', '6': 'SDLK_6', '7': 'SDLK_7',
    '8': 'SDLK_8', '9': 'SDLK_9',
    'space': 'SDLK_SPACE', 'Tab': 'SDLK_TAB', 'Caps_Lock': 'SDLK_CAPSLOCK',
    'Return': 'SDLK_RETURN', 'Shift': 'SDLK_LSHIFT', 'Control': 'SDLK_LCTRL',
    'Alt_L': 'SDLK_LALT', 'Alt_R': 'SDLK_RALT', 'BackSpace': 'SDLK_BACKSPACE',
    'Left': 'SDLK_LEFT', 'Right': 'SDLK_RIGHT', 'Up': 'SDLK_UP', 'Down': 'SDLK_DOWN',
    'Mouse1': 'SDL_BUTTON_LEFT', 'Mouse2': 'SDL_BUTTON_MIDDLE', 'Mouse3': 'SDL_BUTTON_RIGHT',
    'comma': 'SDLK_COMMA', 'minus': 'SDLK_MINUS', 'equal': 'SDLK_EQUALS',
    'bracketleft': 'SDLK_LEFTBRACKET', 'bracketright': 'SDLK_RIGHTBRACKET',
    'backslash': 'SDLK_BACKSLASH', 'semicolon': 'SDLK_SEMICOLON',
    'apostrophe': 'SDLK_QUOTE', 'period': 'SDLK_PERIOD', 'slash': 'SDLK_SLASH',
    'colon': 'SDLK_COLON'
}

COLORS = {
    "gameboy_grey": "#C5C1C2",
    "screen_green": "#596708",
    "highlight_green": "#005500",
    "text_blue": "#21298C",
    "button_grey": "#808080",
    "black": "#000000",
    "button_magenta": "#a61257",
    "green": "#008800",
    "white": "#FFFFFF"
}

BASE_DIR = Path(__file__).resolve().parent  
ROM_PATH = str(BASE_DIR / "roms")
