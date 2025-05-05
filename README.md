# Campsite Availability Checker

## Goal
The goal of this project is to automate the process of checking availability for specific campsites at Smith Point campground on the Suffolk County Parks website. The user requested a script that can report the availability data in an Excel sheet for the campsites 230, 234, 236, 238, 240, 242, 244, 246, 248, 250, 252, 254, 256, 258, 260, 262, 264, 266, 268, and 270 at Smith Point Park. The availability should be checked for each date from May 1st, 2025, to December 31st, 2025.

## Solution
To accomplish this task, a Python script named `campsite_checker.py` was created. This script utilizes the Playwright library to automate interactions with the website's search interface. It performs the following steps:

1. Launches a browser instance using Playwright.
2. Navigates to the campsite search page.
3. Selects the "Smith Point" park, sets the number of nights to 1, and enters the target campsite numbers in the search field.
4. Iterates through each date from May 1st, 2025, to December 31st, 2025.
5. For each date:
   - Updates the "Begin Date" field with the current date.
   - Clicks the "Search" button to initiate the search.
   - Waits for the results to load.
   - Extracts the availability status (Available or Unavailable) for each of the target campsites using JavaScript evaluation.
   - Stores the date, campsite number, and availability status in a list.
6. After checking all dates, the collected data is compiled into a Pandas DataFrame.
7. The DataFrame is saved as an Excel file named `campsite_availability.xlsx`.

## Prerequisites
Before running the script, ensure you have the following prerequisites installed:

- Python 3.x
- Required Python packages: `playwright`, `pandas`, `openpyxl`

You can install the required packages by running:

```
pip install -r requirements.txt
```

Additionally, the Playwright browsers need to be installed. This can be done by running the provided `install_playwright.py` script:

```
python install_playwright.py
```

## Usage
To run the script and generate the Excel report, execute the following command:

```
python campsite_checker.py
```

The script will launch a visible browser window (you can set `headless=True` in the script to run in headless mode) and perform the necessary interactions on the website. It will provide console output indicating the progress and any issues encountered.

Once the script completes successfully, the `campsite_availability.xlsx` file will be created in the same directory, containing the availability data for the specified campsites and date range.

## Notes
- The script includes a delay of 1 second between checking each date to avoid overwhelming the server with requests.
- Error handling and logging mechanisms are implemented to capture and report any issues that may occur during the execution.
- The script can be further enhanced or customized based on additional requirements or changes to the website's structure.

Please refer to the `campsite_checker.py` file for the complete source code and comments.
