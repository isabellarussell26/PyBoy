# PyBoy_GUI
April 2025

## Authors:
- Andrew Janedy
- Isabella Russell
- Jordan DeAndrade
- Justice Russell

## Overview:
- PyBoy_GUI is a graphical user interface for the [PyBoy emulator](https://github.com/Baekalfen/PyBoy), designed to 
  provide an easy and seamless way to play Game Boy ROMs on your computer.
- The program allows users to load ROM files, configure controls, and manage 
  gameplay all within an intuitive interface.
- You can explore the full original PyBoy documentation here: [PyBoy README](https://github.com/Baekalfen/PyBoy/blob/master/README.md)


## Requirements:
Before running the PyBoy_GUI program, ensure you have the following:

- **Python**: The program requires Python to run. You can download and install Python from the 
  official [Python website](https://www.python.org/downloads/).
- **pip**: You must have pip installed to manage the program’s dependencies. You can install it following 
  [these instructions](https://pip.pypa.io/en/stable/installation/).

### Steps to Run:

1. Install Python from the official [Python website](https://www.python.org/downloads/).
2. Ensure pip is installed. If pip is not installed, follow the [installation guide](https://pip.pypa.io/en/stable/installation/).
3. Clone or download this repository.
4. Navigate to the root directory in command line
5. Install the necessary dependencies using pip by running the following command in your terminal/command prompt: pip install -r requirements.txt
6. Run Cython build by running: python setup.py build_ext --inplace
7. After installing the dependencies and compiling, you can launch the PyBoy_GUI program by running: python pyboy_gui/main.py

### Steps to Compile (Currently only tested on Windows):

1. Create and activate a virtual environment.
2. Install the necessary dependencies using pip
3. Run Cython build by running: python setup.py build_ext --inplace
4. Install PyInstaller by running: pip install pyinstaller
5. From the root directory, run: pyinstaller main.spec
6. PyBoy.exe will be located in PyBoy/dist

## License:
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

