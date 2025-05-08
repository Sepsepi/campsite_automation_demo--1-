# Campsite Availability Checker

## Description

This application checks for campsite availability for specified dates at Smith Point County Park (Suffolk County, NY) by scraping the official booking website. It provides a graphical user interface (GUI) to select date ranges and view logs of the checking process. Results are saved to an Excel file (`campsite_availability.xlsx`).

## Features

*   GUI for easy date selection.
*   Automated web scraping using Playwright.
*   Checks availability for a predefined list of sites at Smith Point.
*   Logs progress and any errors encountered.
*   Saves availability data to an Excel spreadsheet.
*   Dynamically adjusts the number of nights searched based on how far in the future the date is.

## Requirements

*   Python 3.x
*   Required Python packages (see `requirements.txt`)
*   Playwright browsers (specifically Chromium)

## Setup and Usage

There are two main ways to run this application: from source or as a bundled executable.

### 1. Running from Source (for Developers)

**a. Clone the Repository (if applicable)**
   ```bash
   # git clone <repository_url>
   # cd <repository_directory>
   ```

**b. Create a Virtual Environment**
   It's highly recommended to use a virtual environment:
   ```bash
   python -m venv .venv
   ```
   Activate the virtual environment:
   *   Windows:
       ```bash
       .venv\Scripts\activate
       ```
   *   macOS/Linux:
       ```bash
       source .venv/bin/activate
       ```

**c. Install Dependencies**
   Install the required Python packages:
   ```bash
   pip install -r requirements.txt
   ```

**d. Install Playwright Browsers**
   Playwright needs browser binaries to operate. Install Chromium:
   ```bash
   playwright install chromium
   ```
   *(This step downloads the Chromium browser. If you encounter issues, you might need to run `playwright install` which installs default browsers.)*

**e. Run the Application**
   ```bash
   python campsite_checker.py
   ```
   This will launch the GUI. Select your start and end dates and click "Start Search".

### 2. Running the Bundled Executable (`CampsiteChecker.exe`)

*(This section assumes a bundled version of the application exists, typically created using `cx_Freeze` with `python setup.py build`)*

**a. Locate the Executable**
   The executable (`CampsiteChecker.exe`) will be in a subdirectory within the `build` folder (e.g., `build/exe.win-amd64-3.12/`).

**b. Running the Application**
   Simply double-click `CampsiteChecker.exe` to run it.

**c. Browser Requirement for Bundled App:**
   *   **If the browser is bundled with the application:** It should run without further setup.
   *   **If the browser is NOT bundled (to keep application size small):** You may need to install the Playwright browsers manually before running the executable for the first time. Open a command prompt or terminal and run:
       ```bash
       playwright install chromium
       ```
       If you see a message from the application prompting you to do this, please follow that instruction.

## Configuration

The following configurations are currently hardcoded in `campsite_checker.py`:
*   `URL`: The booking website URL.
*   `TARGET_PARK_VALUE`: The park name to search for (currently "Smith Point").
*   `TARGET_SITES`: A comma-separated string of site numbers to check.
*   `OUTPUT_FILE`: Name of the Excel file for results (default: `campsite_availability.xlsx`).
*   `REQUEST_DELAY_SECONDS`: Delay between checking each date.

## Building the Executable (Optional)

If you have the source code and want to build the executable yourself:
1.  Ensure all development dependencies, including `cx_Freeze`, are installed (see `requirements.txt`).
2.  Ensure Playwright's Chromium browser is installed locally (`playwright install chromium`), as `setup.py` may try to bundle it.
3.  Run the build command from the project root directory:
    ```bash
    python setup.py build
    ```
    This will create a `build` directory containing the executable and its dependencies.

## Troubleshooting

*   **"Executable doesn't exist" / "playwright install" message:** This means Playwright cannot find the required browser.
    *   If running from source, ensure you've run `playwright install chromium`.
    *   If running a bundled version that doesn't include the browser, run `playwright install chromium`.
*   **Errors during scraping:** The website structure might have changed. Selectors in `campsite_checker.py` may need updating.
*   **Permissions:** Ensure the application has rights to write the output Excel file in its directory.
