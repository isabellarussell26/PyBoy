from unittest.mock import MagicMock
from pyboy_gui.main import GameBoyLauncher
from pathlib import Path
import unittest


class TestGameBoyLauncher(unittest.TestCase):

    def setUp(self):

        dummy_roms_path = Path(__file__).resolve().parent / "dummy_roms"

        self.mock_root = MagicMock()  # Mock tkinter root window

        self.launcher = GameBoyLauncher(self.mock_root)
        self.launcher.rom_directory = dummy_roms_path
        self.launcher.rom_listbox = MagicMock()

    def test_load_roms(self):

        self.launcher.load_roms()

        self.assertIn("mario.gb", self.launcher.games)
        self.assertIn("wario.gb", self.launcher.games)
        self.assertNotIn("mario.gb.ram", self.launcher.games)


if __name__ == "__main__":
    unittest.main()

