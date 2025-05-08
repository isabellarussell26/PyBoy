import pytest
from pyboy import PyBoy
from pyboy.bot_support import BotSupport


@pytest.fixture
def pyboy_instance():
    """
    Pytest fixture to initialize and finalize the PyBoy emulator instance.

    Returns:
        PyBoy: A PyBoy instance with headless mode for testing.
    """
    rom_path = "../roms/Street Fighter II (USA) (SGB Enhanced).gb"  # Update with your ROM path
    pyboy = PyBoy(rom_path, window="null", keybinds=None)
    yield pyboy
    pyboy.stop()


@pytest.fixture
def bot_instance(pyboy_instance):
    """
    Pytest fixture to initialize the BotSupport instance.

    Returns:
        BotSupport: An instance of the BotSupport class.
    """
    return BotSupport(pyboy_instance)


def test_press_button(bot_instance, pyboy_instance):
    """
    Tests that the bot can press and release a button.
    """
    bot_instance.press("A")
    pyboy_instance.tick()  # Simulate one frame
    # Assert here if you have output tied to a button press
    bot_instance.release("A")
    pyboy_instance.tick()


def test_memory_read_write(bot_instance):
    """
    Tests reading and writing to memory values.
    """
    address = 0xC000
    initial_value = bot_instance.get_memory_value(address)
    bot_instance.set_memory_value(address, 42)
    updated_value = bot_instance.get_memory_value(address)

    assert initial_value != 42, "Initial memory value should not be 42"
    assert updated_value == 42, "Updated memory value was not correctly set"


def test_cpu_register_read(bot_instance):
    """
    Tests reading from CPU registers.
    """
    # Example: Reading the Program Counter (PC) register
    pc_value = bot_instance.get_register_value("PC")
    assert pc_value is not None, "CPU PC register value should not be None"


def test_cpu_step(bot_instance, pyboy_instance):
    """
    Tests stepping the CPU by a number of cycles.
    """
    # Get initial PC (Program Counter)
    initial_pc = bot_instance.get_register_value("PC")

    # Step the CPU for 10 cycles
    bot_instance.step_cpu(10)

    # Get the PC after stepping
    stepped_pc = bot_instance.get_register_value("PC")

    assert initial_pc != stepped_pc, "CPU PC register value should change after stepping"
