import time
import openpyxl
from datetime import date, timedelta
from playwright.sync_api import sync_playwright
import threading
import sys
import os
import tkinter as tk
from gui import CampsiteCheckerGUI

def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# --- Configuration ---
URL = "https://nysuffolkctyweb.myvscloud.com/webtrac/web/search.html?Module=RN&Type=FamilySite&webscreendesign=webtrac%20screen%20design&Display=Detail"
TARGET_PARK_VALUE = "Smith Point"
TARGET_SITES = "230, 234, 236, 238, 240, 242, 244, 246, 248, 250, 252, 254, 256, 258, 260, 262, 264, 266, 268, 270"
OUTPUT_FILE = "campsite_availability.xlsx"
DATE_FORMAT = "%m/%d/%Y"
REQUEST_DELAY_SECONDS = 1

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
BEGIN_DATE_INPUT_SELECTOR = "#begindate"
SEARCH_BUTTON_SELECTOR = "#rnwebsearch_buttonsearch"
RESULTS_CONTAINER_SELECTOR = "div.result-content"

# --- JavaScript to Extract Data ---
EXTRACT_JS = """
(() => {
    const results = [];
    const resultBlocks = document.querySelectorAll('div.result-content');

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
            const targetSiteNumbers = TARGET_SITES.split(',').map(s => s.trim());
            if (targetSiteNumbers.includes(siteNumber)) {
                 results.push({ site: siteNumber, status: status });
            }
        }
    });
    return results;
})();
""".replace("TARGET_SITES", f'"{TARGET_SITES}"')

def main():
    root = tk.Tk()
    app = CampsiteCheckerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
