import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from tkcalendar import Calendar
import threading
from datetime import datetime
import openpyxl
from playwright.sync_api import sync_playwright
from campsite_checker import URL, OUTPUT_FILE, DATE_FORMAT, EXTRACT_JS, resource_path

class CampsiteCheckerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Campsite Checker")
        self.root.geometry("600x400")

        self.start_date_var = tk.StringVar()
        self.end_date_var = tk.StringVar()

        self.start_date_label = ttk.Label(root, text="Start Date:")
        self.start_date_label.grid(row=0, column=0, padx=10, pady=10)
        self.start_date_entry = ttk.Entry(root, textvariable=self.start_date_var)
        self.start_date_entry.grid(row=0, column=1, padx=10, pady=10)
        self.start_date_button = ttk.Button(root, text="Pick Date", command=lambda: self.pick_date(self.start_date_var))
        self.start_date_button.grid(row=0, column=2, padx=10, pady=10)

        self.end_date_label = ttk.Label(root, text="End Date:")
        self.end_date_label.grid(row=1, column=0, padx=10, pady=10)
        self.end_date_entry = ttk.Entry(root, textvariable=self.end_date_var)
        self.end_date_entry.grid(row=1, column=1, padx=10, pady=10)
        self.end_date_button = ttk.Button(root, text="Pick Date", command=lambda: self.pick_date(self.end_date_var))
        self.end_date_button.grid(row=1, column=2, padx=10, pady=10)

        self.log_text = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=70, height=15)
        self.log_text.grid(row=2, column=0, columnspan=3, padx=10, pady=10)

        self.start_button = ttk.Button(root, text="Start Search", command=self.start_search)
        self.start_button.grid(row=3, column=0, columnspan=3, pady=10)

    def log(self, message):
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)

    def pick_date(self, string_var):
        def set_date():
            string_var.set(cal.get_date())
            top.destroy()

        top = tk.Toplevel(self.root)
        cal = Calendar(top, selectmode='day')
        cal.pack(pady=20)
        ttk.Button(top, text="Select", command=set_date).pack(pady=10)

    def start_search(self):
        start_date = self.start_date_var.get()
        end_date = self.end_date_var.get()

        if not start_date or not end_date:
            messagebox.showerror("Error", "Please select both start and end dates.")
            return

        self.log(f"Starting search from {start_date} to {end_date}...")
        threading.Thread(target=self.run_search, args=(start_date, end_date), daemon=True).start()

    def run_search(self, start_date, end_date):
        self.log(f"Searching for campsites from {start_date} to {end_date}...")
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(
                    headless=False,
                    executablePath=resource_path("chromium/chrome.exe") if hasattr(sys, '_MEIPASS') else None
                )
                page = browser.new_page()
                page.goto(URL, wait_until='networkidle')
                self.log("Page loaded.")
                results = []
                current_date = datetime.strptime(start_date, DATE_FORMAT)
                end_date_obj = datetime.strptime(end_date, DATE_FORMAT)
                while current_date <= end_date_obj:
                    date_str = current_date.strftime(DATE_FORMAT)
                    self.log(f"Checking date: {date_str}...")
                    # Fill in the date field and trigger search (update selectors as needed)
                    page.fill('#begindate', date_str)
                    page.click('#rnwebsearch_buttonsearch')
                    page.wait_for_selector('div.result-content', timeout=10000)
                    data = page.evaluate(EXTRACT_JS)
                    for row in data:
                        results.append({"date": date_str, "site": row["site"], "status": row["status"]})
                    current_date += timedelta(days=1)
                # Save results to Excel
                wb = openpyxl.Workbook()
                ws = wb.active
                ws.title = "Availability"
                ws.append(["Date", "Site", "Status"])
                for row in results:
                    ws.append([row["date"], row["site"], row["status"]])
                wb.save(OUTPUT_FILE)
                self.log(f"Results saved to {OUTPUT_FILE}")
                browser.close()
        except Exception as e:
            self.log(f"An error occurred: {str(e)}")
        self.log("Search completed.")