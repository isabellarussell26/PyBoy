# -*- mode: python ; coding: utf-8 -*-
import sys
import os

sys.setrecursionlimit(sys.getrecursionlimit() * 5)


block_cipher = None


a = Analysis(
    ['pyboy_gui\\main.py'],
    pathex=[],
    binaries=[('C:\\Users\\andyj\\Desktop\\PyBoy\\pyboy_gui\\venv\\Lib\\site-packages\\sdl2dll\\dll\\SDL2.dll', '.')],
    datas=[
        ('pyboy_gui\\README.md', '.'),
        ('pyboy_gui\\config.py', 'pyboy_gui'),
        ('pyboy_gui\\keybinds_window.py', 'pyboy_gui'),
        ('pyboy_gui\\settings_ui.py', 'pyboy_gui'),
        ('pyboy_gui\\screen_recording.py', '.'),
        ('pyboy', 'pyboy'),
    ],
    hiddenimports=['pyboy', 'pyboy.plugins', 'tkinter.filedialog', 'pyboy_gui.screen_recording',],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
print(f"A.BINARIES: {a.binaries}") # Keep this for debugging
pyz = PYZ(a.pure)
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='PyBoy',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='pyboy_gui/images/pyboy_logo.ico',
)
