# Game Boy Launcher Test Suite

This project includes a test suite for the **Game Boy Launcher** application, which is built using Tkinter and PyBoy. The tests validate the core functionality of the launcher, including ROM loading and initialization.

## Running Tests from the Command Line

To run the tests in this repository, follow the steps below. **It is necessary to set the `PYTHONPATH` environment variable before running the tests.**

### Command to Run the Tests

In the terminal, run the following command from the **root directory** of the project:

````bash
PYTHONPATH=. pytest pyboy_gui/tests/test_gui.py