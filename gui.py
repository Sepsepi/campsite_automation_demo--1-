import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from tkcalendar import Calendar
import threading
# Removed: from datetime import datetime (not directly used here anymore for date logic)
# Removed: import openpyxl (handled by perform_site_check)
# Removed: from playwright.sync_api import sync_playwright (handled by perform_site_check)

# Import the function that now contains the scraping logic
from campsite_checker import perform_site_check
# Removed: URL, OUTPUT_FILE, DATE_FORMAT, EXTRACT_JS, resource_path (these are used within perform_site_check)

class CampsiteCheckerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Campsite Checker")
        self.root.geometry("700x550") # Adjusted width and height

        # --- Dark Theme Styling ---
        self.style = ttk.Style(self.root)
        self.root.tk.call('source', 'azure.tcl') # Assuming azure.tcl is in the same directory or accessible
        self.style.theme_use('azure-dark') # Or 'azure-light'

        # Override some specific styles for better dark theme appearance if needed
        self.style.configure("TLabel", foreground="white", background="#333333")
        self.style.configure("TButton", foreground="white", background="#555555", borderwidth=1)
        self.style.map("TButton", background=[("active", "#666666")])
        self.style.configure("TEntry", fieldbackground="#555555", foreground="white", insertcolor="white")
        self.style.configure("TProgressbar", troughcolor="#555555", background="#0078D7") # Example: Blue progress
        
        # For ScrolledText, we need to configure the underlying Text widget
        self.root.configure(bg="#333333") # Set root background

        self.start_date_var = tk.StringVar()
        self.end_date_var = tk.StringVar()

        self.start_date_label = ttk.Label(root, text="Start Date:", style="TLabel")
        self.start_date_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.start_date_entry = ttk.Entry(root, textvariable=self.start_date_var, width=15, style="TEntry")
        self.start_date_entry.grid(row=0, column=1, padx=10, pady=10)
        self.start_date_button = ttk.Button(root, text="Pick Date", command=lambda: self.pick_date(self.start_date_var), style="TButton")
        self.start_date_button.grid(row=0, column=2, padx=10, pady=10)

        self.end_date_label = ttk.Label(root, text="End Date:", style="TLabel")
        self.end_date_label.grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.end_date_entry = ttk.Entry(root, textvariable=self.end_date_var, width=15, style="TEntry")
        self.end_date_entry.grid(row=1, column=1, padx=10, pady=10)
        self.end_date_button = ttk.Button(root, text="Pick Date", command=lambda: self.pick_date(self.end_date_var), style="TButton")
        self.end_date_button.grid(row=1, column=2, padx=10, pady=10)

        self.progress_bar = ttk.Progressbar(root, orient="horizontal", length=560, mode="determinate", style="TProgressbar")
        self.progress_bar.grid(row=2, column=0, columnspan=3, padx=10, pady=10)

        self.log_text = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=70, height=18,
                                                  bg="#404040", fg="white", insertbackground="white",
                                                  relief=tk.FLAT, borderwidth=1)
        self.log_text.grid(row=3, column=0, columnspan=3, padx=10, pady=10)

        self.start_button = ttk.Button(root, text="Start Search", command=self.start_search_thread, style="TButton")
        self.start_button.grid(row=4, column=0, columnspan=3, pady=15)

    def log(self, message):
        # Ensure updates to the GUI are done in the main thread
        self.root.after(0, self._log_message, message)

    def _log_message(self, message):
        self.log_text.insert(tk.END, str(message) + "\n")
        self.log_text.see(tk.END)

    def pick_date(self, string_var):
        def set_date():
            string_var.set(cal.get_date())
            top.destroy()

        top = tk.Toplevel(self.root)
        top.configure(bg="#333333") # Style the Toplevel
        # Calendar styling might be limited without a custom themed Calendar widget
        cal = Calendar(top, selectmode='day', date_pattern='mm/dd/yyyy',
                       background="#555555", foreground="white", headersbackground="#666666",
                       normalbackground="#555555", normalforeground="white",
                       othermonthbackground="#444444", othermonthforeground="#aaaaaa",
                       selectbackground="#0078D7", selectforeground="white",
                       weekendbackground="#555555", weekendforeground="white",
                       font=("Arial", 10))
        cal.pack(pady=20, padx=10)
        select_btn = ttk.Button(top, text="Select", command=set_date, style="TButton")
        select_btn.pack(pady=10)


    def start_search_thread(self): # Renamed to avoid confusion with a potential method named start_search
        start_date_str = self.start_date_var.get()
        end_date_str = self.end_date_var.get()

        if not start_date_str or not end_date_str:
            messagebox.showerror("Error", "Please select both start and end dates.")
            return

        # Disable button to prevent multiple clicks
        self.start_button.config(state=tk.DISABLED)
        self.log(f"GUI: Initiating search from {start_date_str} to {end_date_str}...")
        
        # Run the perform_site_check in a separate thread
        # Pass self.log as the callback, and also self.enable_start_button for re-enabling
        # Also pass a callback for progress updates
        thread = threading.Thread(target=self.run_search_logic, args=(start_date_str, end_date_str), daemon=True)
        thread.start()

    def update_progress(self, value):
        # Ensure updates to the GUI are done in the main thread
        self.root.after(0, self._update_progress_bar, value)

    def _update_progress_bar(self, value):
        self.progress_bar["value"] = value
        self.root.update_idletasks() # Ensure the progress bar updates visually

    def run_search_logic(self, start_date_str, end_date_str):
        self.update_progress(0) # Reset progress bar at the start
        try:
            # Call the imported function from campsite_checker.py
            # It will use the log_callback (self.log) and progress_callback (self.update_progress)
            perform_site_check(start_date_str, end_date_str, self.log, self.update_progress)
            self.update_progress(100) # Mark as complete if no error
        except Exception as e:
            self.log(f"GUI Error: An unexpected error occurred in the search thread: {e}")
            self.update_progress(0) # Reset progress on error
        finally:
            # Re-enable the start button in the main thread
            self.root.after(0, self.enable_start_button)

    def enable_start_button(self):
        self.start_button.config(state=tk.NORMAL)

# Example of how campsite_checker.py would run this:
# if __name__ == '__main__':
#     root = tk.Tk()
#     app = CampsiteCheckerGUI(root)
#     root.mainloop()
