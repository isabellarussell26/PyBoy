from pyboy import PyBoy


class BotSupport:
    """
    A utility class to provide interaction and automation for the PyBoy emulator.
    """

    def __init__(self, rom_path: str, window: str = "null"):
        """
        Initialize the PyBoy emulator with the specified ROM.

        :param rom_path: Path to the ROM file to load into the emulator.
        :param window: Window display mode ('null' for headless, or others for visual output).
        """
        self.pyboy = PyBoy(rom_path, window=window)  # Updated for new API
        self.memory = self.pyboy.memory  # Access the memory attribute for read/write operations

    def press_button(self, button: str):
        """
        Press a button on the emulator.

        :param button: The name of the button (e.g., "A", "B", "UP", "DOWN", "START").
        """
        button_code = self._get_button_code(button)
        if button_code is None:
            raise ValueError(f"Invalid button name: {button}")
        self.pyboy.send_input(button_code)

    def release_button(self, button: str):
        """
        Release a button on the emulator.

        :param button: The name of the button to release.
        """
        button_code = self._get_button_code(button)
        if button_code is None:
            raise ValueError(f"Invalid button name: {button}")
        self.pyboy.send_input(~button_code)

    def write_memory(self, address: int, value: int):
        """
        Write a value to an address in the emulator's memory.

        :param address: Address in memory to write to.
        :param value: Value to write (0-255).
        """
        self.memory[address] = value  # Direct memory access via self.pyboy.memory

    def read_memory(self, address: int) -> int:
        """
        Read a value from an address in the emulator's memory.

        :param address: Address in memory to read from.
        :return: Value stored at the memory address.
        """
        return self.memory[address]  # Read memory directly

    def step_cpu(self, steps: int = 1):
        """
        Move the emulator forward by a specific number of CPU steps.

        :param steps: The number of CPU steps to perform.
        """
        for _ in range(steps):
            self.pyboy.tick()

    def stop(self):
        """
        Stop the emulator and perform cleanup.
        """
        self.pyboy.stop()

    @staticmethod
    def _get_button_code(button: str):
        """
        Map button names to numeric button codes.

        :param button: Button name (e.g., "A", "B", etc.).
        :return: Corresponding numeric code for the button, or None if invalid.
        """
        # These button codes come from older versions of PyBoy
        mapping = {
            "A": 0x01,  # Button A
            "B": 0x02,  # Button B
            "UP": 0x40,  # D-Pad Up
            "DOWN": 0x80,  # D-Pad Down
            "LEFT": 0x20,  # D-Pad Left
            "RIGHT": 0x10,  # D-Pad Right
            "START": 0x08,  # Start Button
            "SELECT": 0x04,  # Select Button
        }
        return mapping.get(button.upper())
