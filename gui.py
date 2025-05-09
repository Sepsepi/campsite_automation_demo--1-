import tkinter as tk
from tkinter import scrolledtext, messagebox
from tkinter import ttk
from tkcalendar import Calendar
import threading
from campsite_checker import perform_site_check

class CampsiteCheckerGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Campsite Checker")
        self.geometry("900x600")
        self.resizable(True, True)
        self.minsize(600, 400)
        self.is_dark = False
        self.configure_theme()
        self.create_widgets()

    def configure_theme(self):
        if self.is_dark:
            self.bg_color = "#1e1e1e"
            self.fg_color = "#ffffff"
            self.entry_bg = "#2c2c2c"
            self.btn_bg = "#3a3a3a"
            self.btn_fg = "#ffffff"
            self.text_bg = "#23272e"
            self.text_fg = "#e0e0e0"
            self.border_color = "#444444"
            self.terminal_border = "#444444"
        else:
            self.bg_color = "#ffffff"
            self.fg_color = "#000000"
            self.entry_bg = "#f7f7f7"
            self.btn_bg = "#e0e0e0"
            self.btn_fg = "#000000"
            self.text_bg = "#f9f9fb"  # subtle tint for terminal
            self.text_fg = "#222222"
            self.border_color = "#b0b0b0"  # darker border for entries/buttons
            self.terminal_border = "#888888"  # more obvious terminal border
        self.configure(bg=self.bg_color)

    def create_widgets(self):
        # Top Frame
        top_frame = tk.Frame(self, bg=self.bg_color)
        top_frame.pack(padx=20, pady=10, fill="x")
        title = tk.Label(top_frame, text="Campsite Checker", bg=self.bg_color, fg=self.fg_color, font=("Segoe UI", 14, "bold"))
        title.pack(side="left")
        self.theme_btn = tk.Button(top_frame, text=("Switch to Light Mode" if self.is_dark else "Switch to Dark Mode"), command=self.toggle_theme, bg=self.btn_bg, fg=self.btn_fg, relief=tk.FLAT, padx=10, pady=2, highlightbackground=self.border_color, highlightcolor=self.border_color, highlightthickness=1, bd=0)
        self.theme_btn.pack(side="right")

        # --- Unified Form Frame for Alignment ---
        form_frame = tk.Frame(self, bg=self.bg_color)
        form_frame.pack(padx=20, pady=(0, 10), fill="x")

        label_font = ("Segoe UI", 10)
        entry_font = ("Segoe UI", 10)
        label_width = 12
        entry_width = 20  # Make entry boxes compact

        # Select a Park
        tk.Label(form_frame, text="Select a Park", bg=self.bg_color, fg=self.fg_color, font=label_font, width=label_width, anchor="w").grid(row=0, column=0, sticky="w", pady=2)
        self.park_var = tk.StringVar(value="Smith Point")
        self.park_entry = tk.Entry(form_frame, textvariable=self.park_var, bg=self.entry_bg, fg=self.fg_color, relief=tk.FLAT, highlightbackground=self.border_color, highlightcolor=self.border_color, highlightthickness=1, bd=0, width=entry_width, font=entry_font)
        self.park_entry.grid(row=0, column=1, sticky="w", pady=2, ipady=2, ipadx=6)

        # Site Search
        tk.Label(form_frame, text="Site Search", bg=self.bg_color, fg=self.fg_color, font=label_font, width=label_width, anchor="w").grid(row=1, column=0, sticky="nw", pady=2)
        self.sites_text = tk.Text(form_frame, bg=self.entry_bg, fg=self.fg_color, relief=tk.FLAT, highlightbackground=self.border_color, highlightcolor=self.border_color, highlightthickness=1, bd=0, width=70, height=2, font=entry_font)
        default_sites = "230, 234, 236, 238, 240, 242, 244, 246, 248, 250, 252, 254, 256, 258, 260, 262, 264, 266, 268, 270"
        self.sites_text.insert("1.0", default_sites)
        self.sites_text.grid(row=1, column=1, sticky="ew", pady=2, ipady=2, ipadx=8)

        # Start Date
        tk.Label(form_frame, text="Start Date", bg=self.bg_color, fg=self.fg_color, font=label_font, width=label_width, anchor="w").grid(row=2, column=0, sticky="w", pady=2)
        start_date_frame = tk.Frame(form_frame, bg=self.bg_color)
        self.start_date = tk.Entry(start_date_frame, bg=self.entry_bg, fg=self.fg_color, relief=tk.FLAT, highlightbackground=self.border_color, highlightcolor=self.border_color, highlightthickness=1, bd=0, width=12, font=entry_font)
        self.start_date.pack(side="left", ipady=2, ipadx=6)
        tk.Button(start_date_frame, text="Pick Date", bg=self.btn_bg, fg=self.btn_fg, relief=tk.FLAT, command=lambda: self.pick_date(self.start_date), highlightbackground=self.border_color, highlightcolor=self.border_color, highlightthickness=1, bd=0, font=entry_font, padx=6, pady=1).pack(side="left", padx=(4, 0))
        start_date_frame.grid(row=2, column=1, sticky="w", pady=2)

        # End Date
        tk.Label(form_frame, text="End Date", bg=self.bg_color, fg=self.fg_color, font=label_font, width=label_width, anchor="w").grid(row=3, column=0, sticky="w", pady=2)
        end_date_frame = tk.Frame(form_frame, bg=self.bg_color)
        self.end_date = tk.Entry(end_date_frame, bg=self.entry_bg, fg=self.fg_color, relief=tk.FLAT, highlightbackground=self.border_color, highlightcolor=self.border_color, highlightthickness=1, bd=0, width=12, font=entry_font)
        self.end_date.pack(side="left", ipady=2, ipadx=6)
        tk.Button(end_date_frame, text="Pick Date", bg=self.btn_bg, fg=self.btn_fg, relief=tk.FLAT, command=lambda: self.pick_date(self.end_date), highlightbackground=self.border_color, highlightcolor=self.border_color, highlightthickness=1, bd=0, font=entry_font, padx=6, pady=1).pack(side="left", padx=(4, 0))
        self.headless_var = tk.BooleanVar()
        tk.Checkbutton(end_date_frame, text="Run in Headless Mode", bg=self.bg_color, fg=self.fg_color, variable=self.headless_var, selectcolor=self.bg_color, activebackground=self.bg_color, activeforeground=self.fg_color, highlightbackground=self.border_color, highlightcolor=self.border_color, highlightthickness=1, bd=0, font=entry_font, padx=6).pack(side="left", padx=(8, 0))
        end_date_frame.grid(row=3, column=1, sticky="w", pady=2)

        # Progress Bar (Blue)
        style = ttk.Style()
        style.theme_use('default')
        style.configure("blue.Horizontal.TProgressbar", troughcolor=self.bg_color, bordercolor=self.bg_color, background="#0078FF", lightcolor="#0078FF", darkcolor="#0078FF")
        self.progress_bar = ttk.Progressbar(self, orient="horizontal", mode="determinate", style="blue.Horizontal.TProgressbar")
        self.progress_bar.pack(padx=20, fill="x")

        # Output Area with Scrollbar
        output_frame = tk.Frame(self, bg=self.bg_color)
        output_frame.pack(padx=20, pady=10, fill="both", expand=True)
        self.output_box = scrolledtext.ScrolledText(output_frame, height=10, bg=self.text_bg, fg=self.text_fg, insertbackground=self.fg_color, relief=tk.FLAT, font=("Consolas", 11), highlightbackground=self.terminal_border, highlightcolor=self.terminal_border, highlightthickness=2, bd=0)
        self.output_box.pack(side="left", fill="both", expand=True)
        # Start Search Button
        def on_start_search():
            start_date_str = self.start_date.get()
            end_date_str = self.end_date.get()
            headless = self.headless_var.get()
            park = self.park_var.get()
            sites = self.sites_text.get("1.0", tk.END).replace("\n", " ").replace("\r", " ").strip()
            if not start_date_str or not end_date_str:
                messagebox.showerror("Error", "Please select both start and end dates.")
                return
            self.start_btn.config(state=tk.DISABLED)
            self.log(f"GUI: Initiating search from {start_date_str} to {end_date_str} (headless={headless}, park={park}, sites={sites})...")
            thread = threading.Thread(target=self.run_search_logic, args=(start_date_str, end_date_str, headless, park, sites), daemon=True)
            thread.start()
        self.start_btn = tk.Button(self, text="Start Search", bg="#0078FF", fg="white", padx=10, pady=5, font=("Segoe UI", 11), relief=tk.FLAT, command=on_start_search, highlightbackground=self.border_color, highlightcolor=self.border_color, highlightthickness=1, bd=0)
        self.start_btn.pack(pady=10, anchor="e", padx=30)

    def toggle_theme(self):
        self.is_dark = not self.is_dark
        self.configure_theme()
        for widget in self.winfo_children():
            widget.destroy()
        self.create_widgets()

    def pick_date(self, entry_widget):
        def set_date():
            entry_widget.delete(0, tk.END)
            entry_widget.insert(0, cal.get_date())
            top.destroy()
        top = tk.Toplevel(self)
        top.configure(bg=self.bg_color)
        cal = Calendar(top, selectmode='day', date_pattern='mm/dd/yyyy')
        cal.pack(pady=16, padx=10)
        select_btn = tk.Button(top, text="Select", command=set_date, bg="#0078FF", fg="white", relief=tk.FLAT)
        select_btn.pack(pady=8)

    def log(self, message):
        self.output_box.insert(tk.END, str(message) + "\n")
        self.output_box.see(tk.END)

    def update_progress(self, value):
        self.progress_bar["value"] = value
        self.update_idletasks()

    def run_search_logic(self, start_date_str, end_date_str, headless, park, sites):
        try:
            perform_site_check(start_date_str, end_date_str, self.log, self.update_progress, headless, park, sites)
        except Exception as e:
            self.log(f"GUI Error: An unexpected error occurred in the search thread: {e}")
        finally:
            self.start_btn.config(state=tk.NORMAL)

if __name__ == "__main__":
    app = CampsiteCheckerGUI()
    app.mainloop()
