import sys
import os
from cx_Freeze import setup, Executable
import subprocess
import shutil
from pathlib import Path


sys.setrecursionlimit(sys.getrecursionlimit() * 10)

# --- Determine Playwright browser path ---
# IMPORTANT: This assumes 'playwright install chromium' has been run and 'chromium-1097' is the correct version.
# The user's home directory is C:/Users/The Effrontery
# The path is C:\Users\The Effrontery\AppData\Local\ms-playwright\chromium-1097\chrome-win
# For cx_Freeze, we need to provide an absolute path or one relative to setup.py.
sys.setrecursionlimit(sys.getrecursionlimit() * 10)

# --- Determine Playwright browser source path ---
# This path points to where 'playwright install chromium' downloaded the browser.
# IMPORTANT: Ensure this path is correct for your system and 'chromium-1097' is the version.
user_profile = os.environ.get("USERPROFILE") or os.path.expanduser("~")  # More robust fallback for user profile
# Updated to use chromium-1005 path
chromium_src_path_str = str(Path(user_profile) / "AppData" / "Local" / "ms-playwright" / "chromium-1005" / "chrome-win")

# Check if the source path exists
if not os.path.exists(chromium_src_path_str):
    print(f"ERROR: Chromium source path for bundling not found: {chromium_src_path_str}")
    print("Please ensure Playwright's Chromium browser (version 1097) is installed by running 'playwright install chromium'")
    # Consider sys.exit(1) here if you want the build to fail if browsers aren't pre-installed.

# --- Determine Python installation path for Tcl/Tk ---
# This is based on the traceback provided in the error.
python_install_dir_str = r"C:\Users\my notebook\AppData\Local\Programs\Python\Python39" # From error traceback
tcl_lib_path_str = str(Path(python_install_dir_str) / "tcl" / "tcl8.6")
tk_lib_path_str = str(Path(python_install_dir_str) / "tcl" / "tk8.6")

# Check if Tcl/Tk paths exist
if not os.path.exists(tcl_lib_path_str):
    print(f"ERROR: Tcl library path not found: {tcl_lib_path_str}")
    # sys.exit(1) # Optionally fail build
if not os.path.exists(tk_lib_path_str):
    print(f"ERROR: Tk library path not found: {tk_lib_path_str}")
    # sys.exit(1) # Optionally fail build

# Dependencies
build_exe_options = {
    "packages": [
        "tkinter",
        "tkcalendar",
        "playwright",
        "openpyxl",
        "asyncio" # Playwright often needs this
    ],
    "excludes": [],
    "include_files": [
        # Copy the entire 'chrome-win' directory to the specific path Playwright expects within the bundle.
        (chromium_src_path_str, "lib/playwright/driver/package/.local-browsers/chromium-1005/chrome-win"),
        (tcl_lib_path_str, "lib/tcl8.6"), # Added for Tcl
        (tk_lib_path_str, "lib/tk8.6")    # Added for Tk
    ],
}

# Base name for the executable
# Set base to None for console window (useful for debugging bundled app)
base = None
if sys.platform == "win32":
    base = "Win32GUI"  # Hide console window for GUI app

setup(
    name="CampsiteChecker",
    version="1.0",
    description="Campsite Availability Checker",
    options={"build_exe": build_exe_options},
    executables=[
        Executable(
            "campsite_checker.py",
            base=base, 
            target_name="CampsiteChecker.exe",
            icon=None
        )
    ]
)

# Post-build script is not needed if we are bundling the browser.
# def install_playwright_browsers():
#     print("Installing Playwright browsers...")
#     try:
#         subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"], check=True)
#         print("Playwright browsers installed successfully.")
#     except Exception as e:
#         print(f"Error installing Playwright browsers: {e}")

# if __name__ == "__main__":
#     print("Running post-build script...")
#     install_playwright_browsers()
