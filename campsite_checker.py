import time
import openpyxl # Changed from pandas
from playwright.sync_api import sync_playwright
from datetime import date, timedelta, datetime
import tkinter as tk
from tkinter import filedialog # Added for save dialog
import sys
import os
# gui.py will import perform_site_check from this file
# from gui import CampsiteCheckerGUI # This line will be moved to main() to avoid circular import at module level

# --- Configuration ---
URL = "https://nysuffolkctyweb.myvscloud.com/webtrac/web/search.html?Module=RN&Type=FamilySite&webscreendesign=webtrac%20screen%20design&Display=Detail"
TARGET_PARK_VALUE = "Smith Point"
TARGET_SITES = "230, 234, 236, 238, 240, 242, 244, 246, 248, 250, 252, 254, 256, 258, 260, 262, 264, 266, 268, 270"
OUTPUT_FILE = "campsite_availability.xlsx"
DATE_FORMAT = "%m/%d/%Y" # Format expected by the website input
REQUEST_DELAY_SECONDS = 1 # Delay between checking each date

# --- Selectors ---
PARK_LABEL_SELECTOR = "#category_vm_2_label"
PARK_LIST_ITEM_SELECTOR = f"#category_vm_2_wrap li[data-value='{TARGET_PARK_VALUE}']"
NIGHTS_LABEL_SELECTOR = "#nights_vm_1_label"
NIGHTS_BUTTON_SELECTOR = "#nights_vm_1_button"
NIGHTS_OPTION_1_SELECTOR = "#nights_vm_1_wrap li[data-value='1']"
NIGHTS_OPTION_4_SELECTOR = "#nights_vm_1_wrap li[data-value='4']"
KEYWORD_LABEL_SELECTOR = "label[for='keyword']"
KEYWORD_INPUT_SELECTOR = "#keyword"
BEGIN_DATE_LABEL_SELECTOR = "#begindate_vm_6_label"
BEGIN_DATE_INPUT_SELECTOR = "#begindate" # Hidden input
SEARCH_BUTTON_SELECTOR = "#rnwebsearch_buttonsearch"
RESULTS_CONTAINER_SELECTOR = "div.result-content" # To wait for results loading

# --- JavaScript to Extract Data ---
EXTRACT_JS = """
(() => {
    const results = [];
    const resultBlocks = document.querySelectorAll('div.result-content');
    const targetSiteNumbers = TARGET_SITES_STR.split(',').map(s => s.trim());

    resultBlocks.forEach(block => {
        const siteNameElement = block.querySelector('.result-header__info h2 span');
        const siteName = siteNameElement ? siteNameElement.textContent.trim() : null;
        const siteNumberMatch = siteName ? siteName.match(/Site (\\d+)/) : null;
        const siteNumber = siteNumberMatch ? siteNumberMatch[1] : null;

        if (siteNumber) {
            const addButton = block.querySelector('td.button-cell--cart a.button');
            let status = 'Unknown';
            if (addButton) {
                if (addButton.classList.contains('success')) {
                    status = 'Available';
                } else if (addButton.classList.contains('error')) {
                    status = 'Unavailable';
                }
            }
            if (targetSiteNumbers.includes(siteNumber)) {
                 results.push({ site: siteNumber, status: status });
            }
        }
    });
    return results;
})();
""".replace("TARGET_SITES_STR", f'"{TARGET_SITES}"') # Inject target sites into JS

def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def perform_site_check(start_date_str, end_date_str, log_callback, progress_callback=None): # Add progress_callback
    log_callback(f"Starting site check from {start_date_str} to {end_date_str}...")
    all_results = []
    
    try:
        start_date_obj = datetime.strptime(start_date_str, DATE_FORMAT).date()
        end_date_obj = datetime.strptime(end_date_str, DATE_FORMAT).date()
    except ValueError:
        log_callback(f"Error: Invalid date format. Please use {DATE_FORMAT.replace('%m','MM').replace('%d','DD').replace('%Y','YYYY')}.")
        return

    current_date = start_date_obj
    today = date.today()

    total_days = (end_date_obj - start_date_obj).days + 1
    processed_days = 0

    if progress_callback:
        progress_callback(0) # Initial progress

    with sync_playwright() as p:
        try:
            # For development, ensure Playwright browsers are installed: playwright install
            # For cx_Freeze, if bundling, executablePath might be needed.
            # For now, assume browsers are available in the environment.
            browser = p.chromium.launch(headless=False) 
            page = browser.new_page()
            log_callback(f"Navigating to {URL}...")
            page.goto(URL, wait_until='networkidle')
            log_callback("Page loaded.")

            log_callback("Performing initial setup clicks...")
            page.locator(PARK_LABEL_SELECTOR).click()
            page.locator(PARK_LIST_ITEM_SELECTOR).click()
            log_callback(f"- Selected Park: {TARGET_PARK_VALUE}")
            page.locator(KEYWORD_LABEL_SELECTOR).click()
            page.locator(KEYWORD_INPUT_SELECTOR).fill(TARGET_SITES)
            log_callback(f"- Entered Site Keywords: {TARGET_SITES}")
            log_callback("Initial setup complete.")

            while current_date <= end_date_obj:
                loop_date_str = current_date.strftime(DATE_FORMAT)
                log_callback(f"Checking date: {loop_date_str}...")

                try:
                    days_diff = (current_date - today).days
                    nights_to_select = 4 if days_diff > 30 else 1
                    log_callback(f"- Setting Nights to {nights_to_select} (Date is {days_diff} days from today)")

                    page.locator(NIGHTS_LABEL_SELECTOR).click()
                    page.locator(NIGHTS_BUTTON_SELECTOR).click() # Assuming this reveals the options
                    if nights_to_select == 4:
                        page.locator(NIGHTS_OPTION_4_SELECTOR).click()
                    else:
                        page.locator(NIGHTS_OPTION_1_SELECTOR).click()

                    page.locator(BEGIN_DATE_LABEL_SELECTOR).click()
                    page.evaluate(f"""
                        const dateInput = document.querySelector('{BEGIN_DATE_INPUT_SELECTOR}');
                        if (dateInput) {{
                            dateInput.value = '{loop_date_str}';
                            dateInput.dispatchEvent(new Event('change', {{ bubbles: true }}));
                        }} else {{
                            console.error('Date input not found for {loop_date_str}!');
                        }}
                    """)
                    log_callback(f"- Set Begin Date to {loop_date_str} via JS")

                    page.locator(SEARCH_BUTTON_SELECTOR).click()
                    log_callback("- Clicked Search")

                    page.wait_for_load_state('networkidle', timeout=15000)
                    log_callback("- Results loaded (network idle)")

                    daily_results = page.evaluate(EXTRACT_JS)
                    log_callback(f"- Extracted {len(daily_results)} results for {loop_date_str}")

                    for result in daily_results:
                        result['date'] = loop_date_str
                        result['nights_searched'] = nights_to_select
                        all_results.append(result)

                except Exception as e:
                    log_callback(f"!! Error processing date {loop_date_str}: {e}")
                    error_screenshot_path = f"error_{current_date.strftime('%Y%m%d')}.png"
                    page.screenshot(path=error_screenshot_path)
                    log_callback(f"Screenshot saved to {error_screenshot_path}")

                current_date += timedelta(days=1)
                processed_days += 1
                if progress_callback:
                    progress_percentage = (processed_days / total_days) * 100
                    progress_callback(progress_percentage)

                if current_date <= end_date_obj: # Only sleep if there are more dates
                    log_callback(f"Waiting {REQUEST_DELAY_SECONDS}s before next request...")
                    time.sleep(REQUEST_DELAY_SECONDS)
            
            log_callback("All dates processed.")
            if progress_callback:
                progress_callback(100) # Ensure it hits 100% at the end of loop

        except Exception as e:
            log_callback(f"An error occurred during the Playwright process: {e}")
            if 'page' in locals(): # Check if page object exists
                 page.screenshot(path="error_screenshot_main_playwright.png")
                 log_callback("Main Playwright process error screenshot saved.")
        finally:
            if 'browser' in locals() and browser.is_connected():
                log_callback("Closing browser...")
                browser.close()

    if all_results:
        log_callback(f"\nCollected {len(all_results)} total availability records.")
        log_callback("Processing data and saving to Excel using openpyxl...")
        
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Availability"
        
        # Write header
        header = ['date', 'site', 'status', 'nights_searched']
        ws.append(header)
        
        # Write data rows
        for result_item in all_results:
            # Ensure order matches header
            row_data = [
                result_item.get('date'),
                result_item.get('site'),
                result_item.get('status'),
                result_item.get('nights_searched')
            ]
            ws.append(row_data)
        
        # Ask user for save location
        # Reformat dates for filename to avoid slashes
        try:
            s_date_obj = datetime.strptime(start_date_str, DATE_FORMAT)
            e_date_obj = datetime.strptime(end_date_str, DATE_FORMAT)
            formatted_start_date = s_date_obj.strftime("%m-%d-%Y")
            formatted_end_date = e_date_obj.strftime("%m-%d-%Y")
            default_filename = f"Campsite_Availability_{formatted_start_date}_to_{formatted_end_date}.xlsx"
        except ValueError: # Fallback if date parsing fails for some reason
            default_filename = "Campsite_Availability.xlsx"

        output_path = filedialog.asksaveasfilename(
            initialfile=default_filename, # Set the default filename
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
            title="Save Campsite Availability As..."
        )

        if output_path: # If the user selected a path (didn't cancel)
            try:
                wb.save(output_path)
                log_callback(f"Data successfully saved to {output_path}")
            except Exception as e:
                log_callback(f"Error saving Excel file to {output_path}: {e}")
        else:
            log_callback("Save operation cancelled by user.")
            
    else:
        log_callback("No data collected. Check logs or error screenshots for issues.")
    
    log_callback("Site check script finished.")
    # Ensure progress is 100 if everything completes, even if no results
    if progress_callback:
        progress_callback(100)


def main():
    # Import gui here to avoid circular import at module level
    from gui import CampsiteCheckerGUI 
    root = tk.Tk()
    app = CampsiteCheckerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    # This is the main entry point when running the script directly
    # For cx_Freeze, it will also be the entry point of the executable
    main()
