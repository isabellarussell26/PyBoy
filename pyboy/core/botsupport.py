"""Code written by Justice Russell"""

class BotSupport:
    """
    Provides interfaces for automation and benchmarking using PyBoy's internal state.
    Can be used for headless testing, AI input, frame stepping, etc.
    """

    def __init__(self, motherboard):
        self.motherboard = motherboard
        self.frame_count = 0

    def step_frame(self):
        """
        Steps the emulator by one frame and increments frame count.
        """
        self.motherboard.tick()
        self.frame_count += 1

    def get_registers(self):
        """
        Returns a dictionary of current CPU register values.
        """
        cpu = self.motherboard.cpu
        return {
            "A": cpu.a,
            "B": cpu.b,
            "C": cpu.c,
            "D": cpu.d,
            "E": cpu.e,
            "F": cpu.f,
            "H": cpu.h,
            "L": cpu.l,
            "PC": cpu.pc,
            "SP": cpu.sp,
        }

    def read_memory(self, address, length=1):
        """
        Reads `length` bytes from memory starting at `address`.
        """
        return [self.motherboard.memory.read8(address + i) for i in range(length)]

    def write_memory(self, address, values):
        """
        Writes bytes to memory at the specified address.
        """
        if isinstance(values, int):
            values = [values]
        for i, val in enumerate(values):
            self.motherboard.memory.write8(address + i, val)

    def reset(self):
        """
        Resets frame count or any additional state as needed.
        """
        self.frame_count = 0
