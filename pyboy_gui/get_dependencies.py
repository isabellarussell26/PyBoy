import subprocess
import sys
import importlib.util


def install_or_update_pyboy():
    package_name = "pyboy"

    def is_installed(pkg):
        return importlib.util.find_spec(pkg) is not None

    try:
        if is_installed(package_name):
            print(f"{package_name} is already installed. Updating...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", package_name])
        else:
            print(f"{package_name} is not installed. Installing...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
        print(f"{package_name} is ready!")
    except subprocess.CalledProcessError as e:
        print(f"Failed to install or update {package_name}: {e}")