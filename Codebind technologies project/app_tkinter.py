import tkinter as tk
from tkinter import ttk, messagebox
import os
import pickle
import pandas as pd
import numpy as np
import datetime
import threading
import requests

# Try imports for optional/ML libraries to ensure graceful behavior
try:
    import pyttsx3
    TTS_AVAILABLE = True
except ImportError:
    TTS_AVAILABLE = False

try:
    import matplotlib
    matplotlib.use("TkAgg")
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    import matplotlib.pyplot as plt
    import seaborn as sns
    PLOT_AVAILABLE = True
except ImportError:
    PLOT_AVAILABLE = False

# Import model training and prediction functions
from model import CropPredictionModel, CROP_INFO, get_fertilizer_recommendation, calculate_yield

class CropPredictionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Crop Prediction System Using Machine Learning")
        self.root.geometry("1100x750")
        self.root.minsize(1050, 700)
        
        # Load ML model
        self.model = CropPredictionModel()
        try:
            self.model.load_model()
        except Exception as e:
            # Train model if not already saved
            self.model.train_models()
            
        # Theme configuration
        self.current_theme = "dark" # default theme
        self.colors = {
            "dark": {
                "bg_main": "#0f172a",       # Slate 900
                "bg_sidebar": "#1e293b",    # Slate 800
                "bg_card": "#1e293b",       # Slate 800
                "bg_card_inner": "#0f172a", # Slate 900
                "fg_title": "#f8fafc",      # Slate 50
                "fg_body": "#cbd5e1",       # Slate 300
                "fg_muted": "#64748b",      # Slate 500
                "primary": "#10b981",       # Emerald 500
                "primary_hover": "#34d399", # Emerald 400
                "danger": "#ef4444",        # Red 500
                "danger_hover": "#f87171",  # Red 400
                "entry_bg": "#334155",      # Slate 700
                "entry_fg": "#ffffff",
                "border": "#475569"         # Slate 600
            },
            "light": {
                "bg_main": "#f8fafc",       # Slate 50
                "bg_sidebar": "#f1f5f9",    # Slate 100
                "bg_card": "#ffffff",       # White
                "bg_card_inner": "#f8fafc", # Slate 50
                "fg_title": "#0f172a",      # Slate 900
                "fg_body": "#334155",       # Slate 700
                "fg_muted": "#64748b",      # Slate 500
                "primary": "#059669",       # Emerald 600
                "primary_hover": "#10b981", # Emerald 500
                "danger": "#dc2626",        # Red 600
                "danger_hover": "#ef4444",  # Red 500
                "entry_bg": "#f1f5f9",      # Slate 100
                "entry_fg": "#0f172a",
                "border": "#cbd5e1"         # Slate 300
            }
        }
        
        # History storage in memory (and backup to file)
        self.history_file = "prediction_history.csv"
        self.history_data = self.load_history_from_csv()
        
        # Initialize TTS Engine in background thread
        self.tts_engine = None
        if TTS_AVAILABLE:
            try:
                self.tts_engine = pyttsx3.init()
                # Set lower speech rate
                self.tts_engine.setProperty('rate', 145)
            except Exception:
                self.tts_engine = None
                
        # Setup GUI Elements
        self.setup_styles()
        self.build_layout()
        
        # Show default Prediction tab
        self.switch_tab("predict")
        
    def setup_styles(self):
        self.style = ttk.Style()
        self.style.theme_use("clam")
        
        # Remove default focus borders
        self.style.configure(".", highlightthickness=0)
        
    def build_layout(self):
        # Master Frame
        self.main_container = tk.Frame(self.root)
        self.main_container.pack(fill=tk.BOTH, expand=True)
        
        # Sidebar Frame
        self.sidebar = tk.Frame(self.main_container, width=240)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)
        self.sidebar.pack_propagate(False) # Keep sidebar width constant
        
        # Content Display Area
        self.content_area = tk.Frame(self.main_container)
        self.content_area.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        self.build_sidebar()
        self.build_prediction_tab()
        self.build_visualization_tab()
        self.build_history_tab()
        self.build_about_tab()
        
    def build_sidebar(self):
        # 1. Logo & App Title Section
        self.sidebar_logo_canvas = tk.Canvas(self.sidebar, width=200, height=80, highlightthickness=0)
        self.sidebar_logo_canvas.pack(pady=(20, 5))
        self.draw_logo()
        
        self.sidebar_title = tk.Label(
            self.sidebar, 
            text="Crop Prediction\nSystem", 
            font=("Segoe UI", 16, "bold"),
            justify=tk.CENTER
        )
        self.sidebar_title.pack(pady=(0, 25))
        
        # 2. Navigation Menu Buttons
        self.nav_buttons = {}
        menu_items = [
            ("predict", "📝 Prediction Form"),
            ("visualize", "📊 Data Analysis"),
            ("history", "📜 History Logs"),
            ("about", "ℹ️ About Project")
        ]
        
        for tab_id, label in menu_items:
            btn = tk.Button(
                self.sidebar,
                text=f"  {label}",
                font=("Segoe UI", 11),
                anchor="w",
                bd=0,
                cursor="hand2",
                relief=tk.FLAT,
                padx=15,
                pady=10,
                command=lambda tid=tab_id: self.switch_tab(tid)
            )
            btn.pack(fill=tk.X, padx=15, pady=5)
            # Bind hover events
            btn.bind("<Enter>", lambda e, b=btn: self.on_button_hover(b, True))
            btn.bind("<Leave>", lambda e, b=btn: self.on_button_hover(b, False))
            self.nav_buttons[tab_id] = btn
            
        # Divider/Space filler
        spacer = tk.Label(self.sidebar)
        spacer.pack(fill=tk.BOTH, expand=True)
        
        # 3. Theme Toggle at bottom
        self.theme_btn = tk.Button(
            self.sidebar,
            text="🌓 Toggle Theme (Dark)",
            font=("Segoe UI", 10, "bold"),
            bd=0,
            cursor="hand2",
            relief=tk.FLAT,
            pady=8,
            command=self.toggle_theme
        )
        self.theme_btn.pack(fill=tk.X, padx=15, pady=15)
        
    def draw_logo(self):
        # Draw a custom glowing leaf icon
        self.sidebar_logo_canvas.delete("all")
        theme_colors = self.colors[self.current_theme]
        
        bg_color = theme_colors["bg_sidebar"]
        self.sidebar_logo_canvas.configure(bg=bg_color)
        
        # Draw leaf on canvas
        # Stem
        self.sidebar_logo_canvas.create_line(100, 70, 100, 20, fill=theme_colors["fg_muted"], width=3, smooth=True)
        # Leaf outline and fill
        leaf_pts = [100, 20, 130, 40, 100, 65, 70, 40]
        self.sidebar_logo_canvas.create_polygon(
            leaf_pts, 
            fill=theme_colors["primary"], 
            outline=theme_colors["primary_hover"], 
            width=2, 
            smooth=True
        )
        # Leaf veins
        self.sidebar_logo_canvas.create_line(100, 65, 100, 25, fill="#ffffff", width=2)
        self.sidebar_logo_canvas.create_line(100, 50, 115, 40, fill="#ffffff", width=1.5)
        self.sidebar_logo_canvas.create_line(100, 40, 85, 30, fill="#ffffff", width=1.5)
        self.sidebar_logo_canvas.create_line(100, 35, 110, 28, fill="#ffffff", width=1.5)

    def on_button_hover(self, button, is_hover):
        theme_colors = self.colors[self.current_theme]
        if is_hover:
            # Don't change selected button styling on hover
            if getattr(button, 'is_selected', False):
                return
            button.configure(bg=theme_colors["bg_main"], fg=theme_colors["primary"])
        else:
            if getattr(button, 'is_selected', False):
                return
            button.configure(bg=theme_colors["bg_sidebar"], fg=theme_colors["fg_body"])

    def switch_tab(self, target_tab):
        # Hide all tabs
        self.predict_frame.pack_forget()
        self.visualize_frame.pack_forget()
        self.history_frame.pack_forget()
        self.about_frame.pack_forget()
        
        # Show selected tab
        if target_tab == "predict":
            self.predict_frame.pack(fill=tk.BOTH, expand=True)
        elif target_tab == "visualize":
            self.visualize_frame.pack(fill=tk.BOTH, expand=True)
            self.draw_selected_visualization()
        elif target_tab == "history":
            self.history_frame.pack(fill=tk.BOTH, expand=True)
            self.refresh_history_table()
        elif target_tab == "about":
            self.about_frame.pack(fill=tk.BOTH, expand=True)
            
        # Update sidebar active state
        theme_colors = self.colors[self.current_theme]
        for tid, btn in self.nav_buttons.items():
            if tid == target_tab:
                btn.is_selected = True
                btn.configure(bg=theme_colors["primary"], fg="#ffffff")
            else:
                btn.is_selected = False
                btn.configure(bg=theme_colors["bg_sidebar"], fg=theme_colors["fg_body"])

    # ==========================================
    # PREDICTION TAB
    # ==========================================
    def build_prediction_tab(self):
        self.predict_frame = tk.Frame(self.content_area)
        
        # Title Header
        self.header_panel = tk.Frame(self.predict_frame, pady=15)
        self.header_panel.pack(fill=tk.X, padx=25)
        
        self.header_title = tk.Label(
            self.header_panel, 
            text="Crop Prediction System Using Machine Learning", 
            font=("Segoe UI", 18, "bold")
        )
        self.header_title.pack(anchor="w")
        
        self.header_sub = tk.Label(
            self.header_panel, 
            text="Input soil metrics and environment parameters to generate a recommendation card.", 
            font=("Segoe UI", 10)
        )
        self.header_sub.pack(anchor="w", pady=(2, 0))
        
        # Two-column container
        self.pred_columns = tk.Frame(self.predict_frame)
        self.pred_columns.pack(fill=tk.BOTH, expand=True, padx=25, pady=(0, 20))
        
        # Column 1: Inputs Panel
        self.inputs_card = tk.Frame(self.pred_columns, relief=tk.FLAT, bd=0)
        self.inputs_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 12))
        
        # Column 2: Results & Details Panel
        self.results_card = tk.Frame(self.pred_columns, relief=tk.FLAT, bd=0)
        self.results_card.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(12, 0))
        
        # Fill inputs panel
        self.build_inputs_form()
        
        # Fill results panel
        self.build_results_panel()

    def build_inputs_form(self):
        # Title of card
        self.form_title = tk.Label(self.inputs_card, text="Agricultural Parameters", font=("Segoe UI", 13, "bold"))
        self.form_title.pack(anchor="w", padx=20, pady=(15, 10))

        # Quick Crop Preset selection
        self.preset_frame = tk.Frame(self.inputs_card)
        self.preset_frame.pack(fill=tk.X, padx=20, pady=(0, 10))
        
        self.preset_lbl = tk.Label(self.preset_frame, text="Load Sample Region Preset:", font=("Segoe UI", 10, "bold"))
        self.preset_lbl.pack(side=tk.LEFT)
        
        self.preset_combobox = ttk.Combobox(
            self.preset_frame, 
            values=["Select Crop Area Preset", "Rice Area", "Maize Area", "Chickpea Area", "Cotton Area", "Coffee Area", "Mango Area", "Banana Area", "Grapes Area", "Watermelon Area", "Coconut Area"],
            state="readonly",
            width=23,
            font=("Segoe UI", 10)
        )
        self.preset_combobox.set("Select Crop Area Preset")
        self.preset_combobox.pack(side=tk.LEFT, padx=10)
        self.preset_combobox.bind("<<ComboboxSelected>>", self.load_crop_preset)
        
        # Quick Weather Autofill Frame
        self.weather_frame = tk.LabelFrame(self.inputs_card, text=" Weather Autofill (Optional) ", font=("Segoe UI", 9, "bold"), padx=10, pady=10)
        self.weather_frame.pack(fill=tk.X, padx=20, pady=(5, 15))
        
        self.weather_city_lbl = tk.Label(self.weather_frame, text="City Name:", font=("Segoe UI", 10))
        self.weather_city_lbl.pack(side=tk.LEFT)
        
        self.weather_city_entry = tk.Entry(self.weather_frame, font=("Segoe UI", 10), width=15)
        self.weather_city_entry.insert(0, "Mumbai")
        self.weather_city_entry.pack(side=tk.LEFT, padx=10)
        
        self.weather_btn = tk.Button(
            self.weather_frame, 
            text="Fetch Weather Data", 
            font=("Segoe UI", 9, "bold"),
            cursor="hand2",
            padx=10,
            command=self.fetch_weather
        )
        self.weather_btn.pack(side=tk.LEFT)
        
        # Input grid frame
        self.grid_frame = tk.Frame(self.inputs_card)
        self.grid_frame.pack(fill=tk.BOTH, expand=True, padx=20)
        self.grid_frame.columnconfigure(0, weight=1)
        self.grid_frame.columnconfigure(1, weight=2)
        
        # Field declarations: (Variable Name, Display Name, Unit, Default Value, Tooltip/Range)
        fields = [
            ("N", "Nitrogen (N)", "mg/kg", "90", "Range: 0 - 140"),
            ("P", "Phosphorus (P)", "mg/kg", "42", "Range: 5 - 145"),
            ("K", "Potassium (K)", "mg/kg", "43", "Range: 5 - 205"),
            ("temp", "Temperature", "°C", "20.8", "Range: 10 - 45"),
            ("humid", "Humidity", "%", "82.0", "Range: 15 - 100"),
            ("ph", "Soil pH Value", "", "6.5", "Range: 4.0 - 9.5"),
            ("rain", "Rainfall Amount", "mm", "202.0", "Range: 20 - 300")
        ]
        
        self.entries = {}
        vcmd = (self.root.register(self.validate_numeric), '%P')
        
        for idx, (var, name, unit, default, tooltip) in enumerate(fields):
            lbl = tk.Label(self.grid_frame, text=f"{name} {f'({unit})' if unit else ''}:", font=("Segoe UI", 10, "bold"), anchor="w")
            lbl.grid(row=idx, column=0, sticky="w", pady=6)
            
            entry_frame = tk.Frame(self.grid_frame)
            entry_frame.grid(row=idx, column=1, sticky="ew", pady=6)
            entry_frame.columnconfigure(0, weight=1)
            
            entry = tk.Entry(entry_frame, font=("Segoe UI", 11), validate="key", validatecommand=vcmd)
            entry.insert(0, default)
            entry.grid(row=0, column=0, sticky="ew")
            self.entries[var] = entry
            
            hint = tk.Label(entry_frame, text=tooltip, font=("Segoe UI", 8), fg="#94a3b8")
            hint.grid(row=0, column=1, padx=(10, 0))
            
        # Action Buttons frame at bottom
        self.btn_frame = tk.Frame(self.inputs_card, pady=15)
        self.btn_frame.pack(fill=tk.X, padx=20, side=tk.BOTTOM)
        
        self.predict_btn = tk.Button(
            self.btn_frame,
            text="🌱 Predict Suitable Crop",
            font=("Segoe UI", 11, "bold"),
            cursor="hand2",
            relief=tk.FLAT,
            pady=10,
            command=self.run_prediction
        )
        self.predict_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8))
        
        self.clear_btn = tk.Button(
            self.btn_frame,
            text="🧹 Clear",
            font=("Segoe UI", 11),
            cursor="hand2",
            relief=tk.FLAT,
            pady=10,
            command=self.clear_inputs
        )
        self.clear_btn.pack(side=tk.LEFT, padx=4)
        
        self.exit_btn = tk.Button(
            self.btn_frame,
            text="🚪 Exit",
            font=("Segoe UI", 11),
            cursor="hand2",
            relief=tk.FLAT,
            pady=10,
            command=self.root.quit
        )
        self.exit_btn.pack(side=tk.RIGHT, padx=(8, 0))

    def build_results_panel(self):
        # Result Header Card
        self.result_header_lbl = tk.Label(self.results_card, text="Prediction Summary", font=("Segoe UI", 13, "bold"))
        self.result_header_lbl.pack(anchor="w", padx=20, pady=(15, 10))
        
        # Main Display Result Frame (Emerald accent)
        self.result_display_frame = tk.Frame(self.results_card, borderwidth=1, relief=tk.SOLID, padx=15, pady=15)
        self.result_display_frame.pack(fill=tk.X, padx=20, pady=5)
        
        self.result_crop_lbl = tk.Label(
            self.result_display_frame, 
            text="Click 'Predict Suitable Crop'\nto generate recommendation", 
            font=("Segoe UI", 13, "bold"),
            justify=tk.CENTER
        )
        self.result_crop_lbl.pack(pady=10)
        
        self.result_stats_lbl = tk.Label(
            self.result_display_frame, 
            text="Algorithm: - | Accuracy: -", 
            font=("Segoe UI", 9),
            fg="#94a3b8"
        )
        self.result_stats_lbl.pack()
        
        # Details Tabs/Cards container
        self.detail_notebook = ttk.Notebook(self.results_card)
        self.detail_notebook.pack(fill=tk.BOTH, expand=True, padx=20, pady=(10, 15))
        
        # 1. Info Tab
        self.tab_info = tk.Frame(self.detail_notebook)
        self.detail_notebook.add(self.tab_info, text=" Crop Details ")
        
        self.crop_title_lbl = tk.Label(self.tab_info, text="Crop Name: -", font=("Segoe UI", 11, "bold"))
        self.crop_title_lbl.pack(anchor="w", padx=15, pady=(12, 5))
        
        self.crop_detail_grid = tk.Frame(self.tab_info)
        self.crop_detail_grid.pack(fill=tk.X, padx=15, pady=5)
        self.crop_detail_grid.columnconfigure(0, weight=1)
        self.crop_detail_grid.columnconfigure(1, weight=2)
        
        details_rows = [
            ("Temp. Range:", "temp_val"),
            ("Growing Season:", "season_val"),
            ("Soil Preference:", "soil_val"),
            ("Expected Yield:", "yield_val")
        ]
        self.crop_detail_lbls = {}
        for idx, (label, key) in enumerate(details_rows):
            lbl_name = tk.Label(self.crop_detail_grid, text=label, font=("Segoe UI", 9, "bold"), anchor="w")
            lbl_name.grid(row=idx, column=0, sticky="w", pady=4)
            
            lbl_val = tk.Label(self.crop_detail_grid, text="-", font=("Segoe UI", 9), anchor="w", wraplength=200)
            lbl_val.grid(row=idx, column=1, sticky="w", pady=4)
            self.crop_detail_lbls[key] = lbl_val
            
        self.crop_desc_lbl = tk.Label(self.tab_info, text="Select parameters and run a prediction to view more details on the crop's growing cycle.", font=("Segoe UI", 10), justify=tk.LEFT, wraplength=350, fg="#64748b")
        self.crop_desc_lbl.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)
        
        # 2. Fertilizers Tab
        self.tab_ferts = tk.Frame(self.detail_notebook)
        self.detail_notebook.add(self.tab_ferts, text=" Fertilizers ")
        
        self.ferts_title = tk.Label(self.tab_ferts, text="Soil Nutrient Action Plan", font=("Segoe UI", 11, "bold"))
        self.ferts_title.pack(anchor="w", padx=15, pady=(12, 5))
        
        # Custom Scrollable Text or Label for fertilizer
        self.ferts_scroll_frame = tk.Frame(self.tab_ferts)
        self.ferts_scroll_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=8)
        
        self.ferts_text = tk.Text(self.ferts_scroll_frame, font=("Segoe UI", 10), wrap=tk.WORD, bd=0, relief=tk.FLAT)
        self.ferts_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.ferts_text.insert(tk.END, "Enter soil NPK levels and run prediction to generate custom chemical application advice.")
        self.ferts_text.configure(state=tk.DISABLED)
        
        self.ferts_scroll = ttk.Scrollbar(self.ferts_scroll_frame, command=self.ferts_text.yview)
        self.ferts_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.ferts_text.configure(yscrollcommand=self.ferts_scroll.set)

    def validate_numeric(self, val):
        if val == "":
            return True
        try:
            float(val)
            return True
        except ValueError:
            return False

    def load_crop_preset(self, event):
        preset_name = self.preset_combobox.get()
        if preset_name == "Select Crop Area Preset":
            return
            
        crop = preset_name.replace(" Area", "")
            
        presets = {
            "Rice": {"N": "90", "P": "42", "K": "43", "temp": "20.8", "humid": "82.0", "ph": "6.5", "rain": "202.0"},
            "Maize": {"N": "70", "P": "40", "K": "20", "temp": "22.0", "humid": "62.0", "ph": "6.5", "rain": "85.0"},
            "Chickpea": {"N": "30", "P": "65", "K": "80", "temp": "20.0", "humid": "18.0", "ph": "7.0", "rain": "75.0"},
            "Cotton": {"N": "110", "P": "42", "K": "20", "temp": "25.0", "humid": "80.0", "ph": "6.8", "rain": "75.0"},
            "Coffee": {"N": "100", "P": "22", "K": "30", "temp": "25.0", "humid": "55.0", "ph": "6.5", "rain": "165.0"},
            "Mango": {"N": "30", "P": "27", "K": "30", "temp": "31.0", "humid": "50.0", "ph": "6.0", "rain": "95.0"},
            "Banana": {"N": "100", "P": "80", "K": "50", "temp": "27.0", "humid": "80.0", "ph": "6.0", "rain": "100.0"},
            "Grapes": {"N": "30", "P": "132", "K": "197", "temp": "24.0", "humid": "82.0", "ph": "5.8", "rain": "70.0"},
            "Watermelon": {"N": "90", "P": "15", "K": "50", "temp": "25.0", "humid": "85.0", "ph": "6.5", "rain": "50.0"},
            "Coconut": {"N": "10", "P": "12", "K": "30", "temp": "27.0", "humid": "95.0", "ph": "6.0", "rain": "185.0"}
        }
        
        if crop in presets:
            values = presets[crop]
            for var, val in values.items():
                self.entries[var].delete(0, tk.END)
                self.entries[var].insert(0, val)

    def clear_inputs(self):
        for entry in self.entries.values():
            entry.delete(0, tk.END)
        self.weather_city_entry.delete(0, tk.END)
        self.weather_city_entry.insert(0, "Mumbai")
        
        # Clear result fields
        self.result_crop_lbl.configure(text="Click 'Predict Suitable Crop'\nto generate recommendation")
        self.result_stats_lbl.configure(text="Algorithm: - | Accuracy: -")
        self.crop_title_lbl.configure(text="Crop Name: -")
        for lbl in self.crop_detail_lbls.values():
            lbl.configure(text="-")
        self.crop_desc_lbl.configure(text="Select parameters and run a prediction to view more details on the crop's growing cycle.", fg="#64748b")
        
        self.ferts_text.configure(state=tk.NORMAL)
        self.ferts_text.delete(1.0, tk.END)
        self.ferts_text.insert(tk.END, "Enter soil NPK levels and run prediction to generate custom chemical application advice.")
        self.ferts_text.configure(state=tk.DISABLED)

    def fetch_weather(self):
        city = self.weather_city_entry.get().strip()
        if not city:
            messagebox.showwarning("Input Error", "Please enter a valid city name first.")
            return
            
        self.weather_btn.configure(text="Fetching...", state=tk.DISABLED)
        
        # Run HTTP request in a thread so Tkinter window doesn't freeze
        def run_api():
            try:
                # 1. Geo-code city to lat/lon
                geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1&language=en&format=json"
                geo_res = requests.get(geo_url, timeout=6).json()
                
                if "results" not in geo_res or not geo_res["results"]:
                    self.root.after(0, lambda: messagebox.showerror("Weather Error", f"Could not find coordinates for city: '{city}'"))
                    return
                    
                lat = geo_res["results"][0]["latitude"]
                lon = geo_res["results"][0]["longitude"]
                
                # 2. Fetch current weather and historical rainfall estimate
                weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true&daily=precipitation_sum&timezone=auto"
                w_res = requests.get(weather_url, timeout=6).json()
                
                curr = w_res["current_weather"]
                temp = curr["temperature"]
                # Open-Meteo doesn't give real-time humidity directly in forecast unless asked
                # Let's request it:
                detailed_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,precipitation&timezone=auto"
                det_res = requests.get(detailed_url, timeout=6).json()
                
                curr_det = det_res["current"]
                humidity = curr_det["relative_humidity_2m"]
                
                # Rainfall estimate: typical daily precipitation * 30 (monthly)
                daily_rain = curr_det.get("precipitation", 0.0)
                # Fallback to daily sum list if 0
                if daily_rain <= 0:
                    # Let's check daily sum
                    daily_sum = w_res.get("daily", {}).get("precipitation_sum", [0.0])
                    daily_rain = sum(daily_sum) / len(daily_sum) if daily_sum else 1.0
                
                rainfall = round(daily_rain * 30 + 35, 1) # simple monthly rainfall approximation
                if rainfall < 20: rainfall = 50.0 # clip to realistic crop minimums
                
                # Update UI elements in main thread
                def update_ui():
                    self.entries["temp"].delete(0, tk.END)
                    self.entries["temp"].insert(0, str(temp))
                    self.entries["humid"].delete(0, tk.END)
                    self.entries["humid"].insert(0, str(humidity))
                    self.entries["rain"].delete(0, tk.END)
                    self.entries["rain"].insert(0, str(rainfall))
                    messagebox.showinfo("Weather Success", f"Successfully loaded weather for {city}!\nTemp: {temp}°C, Humidity: {humidity}%, Rainfall: {rainfall}mm")
                    
                self.root.after(0, update_ui)
                
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Network Error", f"Unable to fetch weather data.\nDetail: {str(e)}"))
            finally:
                self.root.after(0, lambda: self.weather_btn.configure(text="Fetch Weather Data", state=tk.NORMAL))
                
        threading.Thread(target=run_api, daemon=True).start()

    def run_prediction(self):
        # Read inputs
        try:
            N = float(self.entries["N"].get())
            P = float(self.entries["P"].get())
            K = float(self.entries["K"].get())
            temp = float(self.entries["temp"].get())
            humid = float(self.entries["humid"].get())
            ph = float(self.entries["ph"].get())
            rain = float(self.entries["rain"].get())
        except ValueError:
            messagebox.showerror("Validation Error", "All agricultural fields must be filled with numeric values.")
            return
            
        # Validation bounds
        if not (0 <= N <= 250 and 0 <= P <= 250 and 0 <= K <= 300):
            messagebox.showwarning("Warning", "Nutrient levels (N, P, K) look unusually high or negative. Double check values!")
        if not (0 <= temp <= 60 and 0 <= humid <= 100 and 0 <= ph <= 14 and 0 <= rain <= 1000):
            messagebox.showerror("Input Bounds Error", "Environmental inputs are outside realistic bounds:\nTemp: 0-60°C\nHumidity: 0-100%\npH: 0-14\nRainfall: 0-1000mm")
            return
            
        # Call model prediction
        crop = self.model.predict(N, P, K, temp, humid, ph, rain)
        accs = self.model.get_accuracies()
        rf_acc = accs.get("Random Forest", 0.986)
        
        # Calculate yield and fertilizer recommendation
        y_val, y_eff = calculate_yield(crop, N, P, K, temp, humid, ph, rain)
        fert_rec = get_fertilizer_recommendation(crop, N, P, K)
        
        # Update results cards
        self.result_crop_lbl.configure(text=f"🌱 Recommended Crop: {crop}")
        self.result_stats_lbl.configure(text=f"Algorithm: Random Forest | Accuracy: {rf_acc*100:.1f}%")
        
        # Crop Details tab
        info = CROP_INFO.get(crop, {})
        self.crop_title_lbl.configure(text=f"Crop Name: {crop}")
        self.crop_detail_lbls["temp_val"].configure(text=info.get("temp_range", "-"))
        self.crop_detail_lbls["season_val"].configure(text=info.get("season", "-"))
        self.crop_detail_lbls["soil_val"].configure(text=info.get("soil_type", "-"))
        self.crop_detail_lbls["yield_val"].configure(text=f"{y_val} t/ha ({y_eff}% efficiency)")
        
        self.crop_desc_lbl.configure(text=info.get("desc", ""), fg=self.colors[self.current_theme]["fg_body"])
        
        # Fertilizer recommendations tab
        self.ferts_text.configure(state=tk.NORMAL)
        self.ferts_text.delete(1.0, tk.END)
        self.ferts_text.insert(tk.END, f"Selected crop requirements:\nOptimal N: {info.get('target_n')}, P: {info.get('target_p')}, K: {info.get('target_k')} (mg/kg)\n\nRecommended Adjustments:\n{fert_rec}")
        self.ferts_text.configure(state=tk.DISABLED)
        
        # Save to history
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        new_row = {
            'N': int(N), 'P': int(P), 'K': int(K),
            'temperature': temp, 'humidity': humid, 'ph': ph, 'rainfall': rain,
            'predicted_crop': crop, 'yield': y_val, 'timestamp': timestamp
        }
        self.history_data = pd.concat([self.history_data, pd.DataFrame([new_row])], ignore_index=True)
        self.save_history_to_csv()
        
        # Voice announcement
        self.speak_prediction(crop, y_val)

    def speak_prediction(self, crop, yield_val):
        if not TTS_AVAILABLE or not self.tts_engine:
            return
            
        def announce():
            try:
                msg = f"The recommended crop is {crop}, with an estimated yield of {yield_val} tons per hectare."
                self.tts_engine.say(msg)
                self.tts_engine.runAndWait()
            except Exception:
                pass # suppress speech exceptions if audio device is locked or unavailable
                
        threading.Thread(target=announce, daemon=True).start()

    # ==========================================
    # VISUALIZATION TAB
    # ==========================================
    def build_visualization_tab(self):
        self.visualize_frame = tk.Frame(self.content_area)
        
        # Header
        self.vis_header = tk.Frame(self.visualize_frame, pady=15)
        self.vis_header.pack(fill=tk.X, padx=25)
        
        self.vis_title = tk.Label(self.vis_header, text="Agricultural Data Analysis", font=("Segoe UI", 18, "bold"))
        self.vis_title.pack(anchor="w")
        
        self.vis_sub = tk.Label(self.vis_header, text="Visualize features and relationships of the model training dataset.", font=("Segoe UI", 10))
        self.vis_sub.pack(anchor="w", pady=(2, 0))
        
        # Button bar for selecting chart
        self.chart_select_frame = tk.Frame(self.visualize_frame)
        self.chart_select_frame.pack(fill=tk.X, padx=25, pady=(5, 10))
        
        self.selected_vis_type = tk.StringVar(value="importance")
        
        chart_buttons = [
            ("importance", "⚡ Feature Importance"),
            ("heatmap", "🔥 Correlation Heatmap"),
            ("distribution", "📊 Crop Distribution")
        ]
        
        self.vis_btns = []
        for vtype, label in chart_buttons:
            btn = tk.Radiobutton(
                self.chart_select_frame,
                text=label,
                variable=self.selected_vis_type,
                value=vtype,
                font=("Segoe UI", 10, "bold"),
                indicatoron=0,
                padx=15,
                pady=8,
                bd=1,
                cursor="hand2",
                selectcolor=self.colors[self.current_theme]["primary"],
                command=self.draw_selected_visualization
            )
            btn.pack(side=tk.LEFT, padx=(0, 10))
            self.vis_btns.append(btn)
            
        # Canvas display container for plot
        self.plot_container = tk.Frame(self.visualize_frame, bd=1, relief=tk.SOLID)
        self.plot_container.pack(fill=tk.BOTH, expand=True, padx=25, pady=(0, 20))
        
        self.plot_canvas = None

    def draw_selected_visualization(self):
        # Clear existing plot
        if self.plot_canvas:
            self.plot_canvas.get_tk_widget().destroy()
            self.plot_canvas = None
            
        # Check if plot is available
        if not PLOT_AVAILABLE:
            err_lbl = tk.Label(self.plot_container, text="Matplotlib and Seaborn are required for graphing visualizations.", font=("Segoe UI", 12))
            err_lbl.pack(expand=True)
            return
            
        # Read dataset
        if not os.path.exists(self.model.csv_path):
            err_lbl = tk.Label(self.plot_container, text="No dataset found to visualize.", font=("Segoe UI", 12))
            err_lbl.pack(expand=True)
            return
            
        df = pd.read_csv(self.model.csv_path)
        vtype = self.selected_vis_type.get()
        
        # Set dark/light style for matplotlib
        is_dark = (self.current_theme == "dark")
        bg_col = self.colors[self.current_theme]["bg_card"]
        fg_col = self.colors[self.current_theme]["fg_title"]
        
        plt.clf()
        fig, ax = plt.subplots(figsize=(7, 4.2), facecolor=bg_col)
        ax.set_facecolor(bg_col)
        
        # Adjust text colors
        matplotlib.rcParams['text.color'] = fg_col
        matplotlib.rcParams['axes.labelcolor'] = fg_col
        matplotlib.rcParams['xtick.color'] = fg_col
        matplotlib.rcParams['ytick.color'] = fg_col
        
        if vtype == "importance":
            # Feature Importance from Random Forest
            if self.model.is_trained:
                feat_importances = pd.Series(self.model.rf_model.feature_importances_, index=['N', 'P', 'K', 'Temp', 'Humidity', 'pH', 'Rainfall'])
                feat_importances = feat_importances.sort_values(ascending=True)
                
                # Colors matching emerald theme
                colors_list = sns.color_palette("viridis", len(feat_importances))
                feat_importances.plot(kind='barh', ax=ax, color=colors_list)
                ax.set_title("Machine Learning Feature Importance", fontsize=12, fontweight='bold', color=fg_col)
                ax.set_xlabel("Relative Importance Weight", fontsize=10, color=fg_col)
            else:
                ax.text(0.5, 0.5, "Train the model first to show feature importance.", ha='center', va='center')
                
        elif vtype == "heatmap":
            # Feature correlation
            corr = df[['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']].corr()
            sns.heatmap(corr, annot=True, cmap="coolwarm", fmt=".2f", ax=ax, cbar=True, square=True)
            ax.set_title("Soil & Environmental Correlation Heatmap", fontsize=12, fontweight='bold', color=fg_col)
            
        elif vtype == "distribution":
            # Crop counts distribution
            counts = df['label'].value_counts()
            sns.barplot(x=counts.index, y=counts.values, ax=ax, palette="magma")
            ax.set_title("Dataset Crop Records Distribution", fontsize=12, fontweight='bold', color=fg_col)
            ax.set_xlabel("Crop Name", fontsize=10, color=fg_col)
            ax.set_ylabel("Records Count", fontsize=10, color=fg_col)
            plt.xticks(rotation=45, ha='right')
            
        fig.tight_layout()
        
        # Render on Canvas
        self.plot_canvas = FigureCanvasTkAgg(fig, master=self.plot_container)
        self.plot_canvas.draw()
        self.plot_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        plt.close(fig)

    # ==========================================
    # HISTORY TAB
    # ==========================================
    def build_history_tab(self):
        self.history_frame = tk.Frame(self.content_area)
        
        # Header
        self.hist_header = tk.Frame(self.history_frame, pady=15)
        self.hist_header.pack(fill=tk.X, padx=25)
        
        self.hist_title = tk.Label(self.hist_header, text="System Prediction History", font=("Segoe UI", 18, "bold"))
        self.hist_title.pack(anchor="w")
        
        self.hist_sub = tk.Label(self.hist_header, text="Review crops previously predicted by the system during this or prior sessions.", font=("Segoe UI", 10))
        self.hist_sub.pack(anchor="w", pady=(2, 0))
        
        # Grid Treeview for logs
        self.table_frame = tk.Frame(self.history_frame, bd=1, relief=tk.SOLID)
        self.table_frame.pack(fill=tk.BOTH, expand=True, padx=25, pady=(5, 10))
        
        cols = ('N', 'P', 'K', 'Temp', 'Humid', 'pH', 'Rain', 'Crop', 'Yield', 'Time')
        self.history_table = ttk.Treeview(self.table_frame, columns=cols, show='headings', selectmode='browse')
        
        col_widths = {
            'N': 50, 'P': 50, 'K': 50, 'Temp': 65, 'Humid': 65, 'pH': 50, 'Rain': 65, 'Crop': 100, 'Yield': 80, 'Time': 150
        }
        for c in cols:
            self.history_table.heading(c, text=c)
            self.history_table.column(c, width=col_widths[c], anchor=tk.CENTER)
            
        self.history_table.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        table_scroll = ttk.Scrollbar(self.table_frame, command=self.history_table.yview)
        table_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.history_table.configure(yscrollcommand=table_scroll.set)
        
        # Actions bar
        self.hist_actions = tk.Frame(self.history_frame, pady=15)
        self.hist_actions.pack(fill=tk.X, padx=25, side=tk.BOTTOM)
        
        self.export_btn = tk.Button(
            self.hist_actions,
            text="📥 Export History (CSV)",
            font=("Segoe UI", 10, "bold"),
            cursor="hand2",
            padx=15,
            pady=8,
            command=self.export_history_csv
        )
        self.export_btn.pack(side=tk.LEFT)
        
        self.clear_hist_btn = tk.Button(
            self.hist_actions,
            text="🗑️ Clear Logs",
            font=("Segoe UI", 10),
            cursor="hand2",
            padx=15,
            pady=8,
            command=self.clear_history_logs
        )
        self.clear_hist_btn.pack(side=tk.RIGHT)

    def load_history_from_csv(self):
        if os.path.exists(self.history_file):
            try:
                return pd.read_csv(self.history_file)
            except Exception:
                pass
        # Empty DataFrame template
        return pd.DataFrame(columns=['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall', 'predicted_crop', 'yield', 'timestamp'])

    def save_history_to_csv(self):
        try:
            self.history_data.to_csv(self.history_file, index=False)
        except Exception as e:
            print(f"Error saving prediction history: {e}")

    def refresh_history_table(self):
        # Clear table
        for item in self.history_table.get_children():
            self.history_table.delete(item)
            
        # Populates rows in reverse chronological order (newest first)
        for _, row in self.history_data.iloc[::-1].iterrows():
            self.history_table.insert('', tk.END, values=(
                int(row['N']), int(row['P']), int(row['K']),
                f"{row['temperature']:.1f}°C", f"{row['humidity']:.1f}%",
                f"{row['ph']:.1f}", f"{row['rainfall']:.1f}mm",
                row['predicted_crop'], f"{row['yield']} t/h", row['timestamp']
            ))

    def clear_history_logs(self):
        if self.history_data.empty:
            return
            
        confirm = messagebox.askyesno("Confirm Clear", "Are you sure you want to delete all prediction history log entries?")
        if confirm:
            self.history_data = pd.DataFrame(columns=['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall', 'predicted_crop', 'yield', 'timestamp'])
            self.save_history_to_csv()
            self.refresh_history_table()
            messagebox.showinfo("Cleared", "Prediction log history has been reset successfully.")

    def export_history_csv(self):
        if self.history_data.empty:
            messagebox.showwarning("Export Empty", "No history available to export.")
            return
            
        export_path = "crop_predictions_export.csv"
        try:
            self.history_data.to_csv(export_path, index=False)
            messagebox.showinfo("Export Success", f"Successfully exported prediction logs!\nSaved to: {os.path.abspath(export_path)}")
        except Exception as e:
            messagebox.showerror("Export Error", f"Unable to save export file.\nDetail: {e}")

    # ==========================================
    # ABOUT TAB
    # ==========================================
    def build_about_tab(self):
        self.about_frame = tk.Frame(self.content_area)
        
        # Header
        self.about_header = tk.Frame(self.about_frame, pady=15)
        self.about_header.pack(fill=tk.X, padx=25)
        
        self.about_title = tk.Label(self.about_header, text="About Crop Prediction System", font=("Segoe UI", 18, "bold"))
        self.about_title.pack(anchor="w")
        
        # Card body
        self.about_card = tk.Frame(self.about_frame, bd=1, relief=tk.SOLID, padx=25, pady=25)
        self.about_card.pack(fill=tk.BOTH, expand=True, padx=25, pady=(5, 25))
        
        # Project Info Content
        info_text = (
            "Crop Prediction System Using Machine Learning\n"
            "----------------------------------------------------\n"
            "This software is designed to assist farmers, agronomists, and agricultural researchers in predicting the most optimal crops to grow in specific field environments. By inputting nutrient indices (Nitrogen, Phosphorus, Potassium) alongside critical weather parameters, the machine learning engine calculates recommended crop varieties, predicts expected output yields, and lists chemical fertilizer balance guidelines.\n\n"
            "System Features:\n"
            "• Machine Learning Core: Uses a trained Random Forest Classifier for precise recommendations (98.6%+ validation accuracy).\n"
            "• Live Weather Integration: Auto-fill local environmental variables directly from coordinates or city name search.\n"
            "• Actionable Agronomy Suggestions: Highlights exactly which soil elements are deficient or high, recommending specific treatments.\n"
            "• Prediction Analytics: Embedded Matplotlib analytics comparing features, dataset counts, and correlations.\n"
            "• Multimodal Feedback: Voice text-to-speech output aids usability in remote settings.\n"
            "• Dark & Light Modes: Enhances UI legibility across high-glare and low-light environments."
        )
        
        self.about_lbl = tk.Label(
            self.about_card, 
            text=info_text, 
            font=("Segoe UI", 10), 
            justify=tk.LEFT, 
            anchor="nw", 
            wraplength=700
        )
        self.about_lbl.pack(fill=tk.BOTH, expand=True)

    # ==========================================
    # THEME SWITCHER
    # ==========================================
    def toggle_theme(self):
        self.current_theme = "light" if self.current_theme == "dark" else "dark"
        self.apply_theme()
        
    def apply_theme(self):
        theme_colors = self.colors[self.current_theme]
        
        # Main containers
        self.root.configure(bg=theme_colors["bg_main"])
        self.main_container.configure(bg=theme_colors["bg_main"])
        self.sidebar.configure(bg=theme_colors["bg_sidebar"])
        self.content_area.configure(bg=theme_colors["bg_main"])
        
        # Sidebar Label & Canvas
        self.sidebar_title.configure(bg=theme_colors["bg_sidebar"], fg=theme_colors["fg_title"])
        self.draw_logo()
        
        # Sidebar Navigation Buttons
        for tid, btn in self.nav_buttons.items():
            if getattr(btn, 'is_selected', False):
                btn.configure(bg=theme_colors["primary"], fg="#ffffff")
            else:
                btn.configure(bg=theme_colors["bg_sidebar"], fg=theme_colors["fg_body"])
                
        self.theme_btn.configure(
            bg=theme_colors["primary"], 
            fg="#ffffff",
            text=f"🌓 Toggle Theme ({'Light' if self.current_theme == 'dark' else 'Dark'})"
        )
        
        # 1. Prediction Tab styling updates
        self.predict_frame.configure(bg=theme_colors["bg_main"])
        self.header_panel.configure(bg=theme_colors["bg_main"])
        self.header_title.configure(bg=theme_colors["bg_main"], fg=theme_colors["fg_title"])
        self.header_sub.configure(bg=theme_colors["bg_main"], fg=theme_colors["fg_body"])
        self.pred_columns.configure(bg=theme_colors["bg_main"])
        
        # Inputs Card
        self.inputs_card.configure(bg=theme_colors["bg_card"], bd=1, relief=tk.SOLID, highlightbackground=theme_colors["border"])
        self.form_title.configure(bg=theme_colors["bg_card"], fg=theme_colors["fg_title"])
        self.preset_frame.configure(bg=theme_colors["bg_card"])
        self.preset_lbl.configure(bg=theme_colors["bg_card"], fg=theme_colors["fg_body"])
        self.weather_frame.configure(bg=theme_colors["bg_card"], fg=theme_colors["primary"])
        self.weather_city_lbl.configure(bg=theme_colors["bg_card"], fg=theme_colors["fg_body"])
        self.weather_city_entry.configure(bg=theme_colors["entry_bg"], fg=theme_colors["entry_fg"], insertbackground=theme_colors["entry_fg"], bd=1, relief=tk.SOLID)
        self.weather_btn.configure(bg=theme_colors["primary"], fg="#ffffff", activebackground=theme_colors["primary_hover"])
        self.grid_frame.configure(bg=theme_colors["bg_card"])
        
        for var, entry in self.entries.items():
            entry.configure(bg=theme_colors["entry_bg"], fg=theme_colors["entry_fg"], insertbackground=theme_colors["entry_fg"], bd=1, relief=tk.SOLID)
            # Find and update corresponding label in same row
            grid_info = entry.master.grid_info()
            row_idx = grid_info["row"]
            # Update label colors in the grid frame
            for child in self.grid_frame.winfo_children():
                if isinstance(child, tk.Label) and child.grid_info()["row"] == row_idx:
                    child.configure(bg=theme_colors["bg_card"], fg=theme_colors["fg_body"])
            # Update hint color in entry master frame
            for child in entry.master.winfo_children():
                if isinstance(child, tk.Label) and child != entry:
                    child.configure(bg=theme_colors["bg_card"], fg=theme_colors["fg_muted"])
            entry.master.configure(bg=theme_colors["bg_card"])
                    
        self.btn_frame.configure(bg=theme_colors["bg_card"])
        self.predict_btn.configure(bg=theme_colors["primary"], fg="#ffffff", activebackground=theme_colors["primary_hover"])
        self.clear_btn.configure(bg=theme_colors["entry_bg"], fg=theme_colors["entry_fg"], activebackground=theme_colors["border"])
        self.exit_btn.configure(bg=theme_colors["danger"], fg="#ffffff", activebackground=theme_colors["danger_hover"])
        
        # Results Card
        self.results_card.configure(bg=theme_colors["bg_card"], bd=1, relief=tk.SOLID, highlightbackground=theme_colors["border"])
        self.result_header_lbl.configure(bg=theme_colors["bg_card"], fg=theme_colors["fg_title"])
        self.result_display_frame.configure(bg=theme_colors["bg_card_inner"], highlightbackground=theme_colors["border"])
        self.result_crop_lbl.configure(bg=theme_colors["bg_card_inner"], fg=theme_colors["primary"])
        self.result_stats_lbl.configure(bg=theme_colors["bg_card_inner"], fg=theme_colors["fg_muted"])
        
        # Tab notebook styling
        self.tab_info.configure(bg=theme_colors["bg_card"])
        self.crop_title_lbl.configure(bg=theme_colors["bg_card"], fg=theme_colors["fg_title"])
        self.crop_detail_grid.configure(bg=theme_colors["bg_card"])
        for child in self.crop_detail_grid.winfo_children():
            if isinstance(child, tk.Label):
                is_lbl_name = (child.grid_info()["column"] == 0)
                child.configure(
                    bg=theme_colors["bg_card"], 
                    fg=theme_colors["fg_title"] if is_lbl_name else theme_colors["fg_body"]
                )
        self.crop_desc_lbl.configure(bg=theme_colors["bg_card"])
        
        self.tab_ferts.configure(bg=theme_colors["bg_card"])
        self.ferts_title.configure(bg=theme_colors["bg_card"], fg=theme_colors["fg_title"])
        self.ferts_scroll_frame.configure(bg=theme_colors["bg_card"])
        self.ferts_text.configure(bg=theme_colors["bg_card_inner"], fg=theme_colors["fg_body"])
        
        # 2. Visualizations Tab
        self.visualize_frame.configure(bg=theme_colors["bg_main"])
        self.vis_header.configure(bg=theme_colors["bg_main"])
        self.vis_title.configure(bg=theme_colors["bg_main"], fg=theme_colors["fg_title"])
        self.vis_sub.configure(bg=theme_colors["bg_main"], fg=theme_colors["fg_body"])
        self.chart_select_frame.configure(bg=theme_colors["bg_main"])
        self.plot_container.configure(bg=theme_colors["bg_card"], highlightbackground=theme_colors["border"])
        
        for btn in self.vis_btns:
            btn.configure(
                bg=theme_colors["bg_card"],
                fg=theme_colors["fg_body"],
                activebackground=theme_colors["primary_hover"],
                activeforeground="#ffffff"
            )
            
        if self.visualize_frame.winfo_viewable():
            self.draw_selected_visualization()
            
        # 3. History Tab
        self.history_frame.configure(bg=theme_colors["bg_main"])
        self.hist_header.configure(bg=theme_colors["bg_main"])
        self.hist_title.configure(bg=theme_colors["bg_main"], fg=theme_colors["fg_title"])
        self.hist_sub.configure(bg=theme_colors["bg_main"], fg=theme_colors["fg_body"])
        self.table_frame.configure(bg=theme_colors["bg_card"], highlightbackground=theme_colors["border"])
        self.hist_actions.configure(bg=theme_colors["bg_main"])
        
        self.export_btn.configure(bg=theme_colors["primary"], fg="#ffffff", activebackground=theme_colors["primary_hover"])
        self.clear_hist_btn.configure(bg=theme_colors["danger"], fg="#ffffff", activebackground=theme_colors["danger_hover"])
        
        # Style Treeview colors
        self.style.configure(
            "Treeview",
            background=theme_colors["bg_card"],
            foreground=theme_colors["fg_body"],
            fieldbackground=theme_colors["bg_card"],
            rowheight=26
        )
        self.style.map("Treeview", background=[("selected", theme_colors["primary"])], foreground=[("selected", "#ffffff")])
        self.style.configure(
            "Treeview.Heading",
            background=theme_colors["bg_sidebar"],
            foreground=theme_colors["fg_title"],
            font=("Segoe UI", 9, "bold")
        )
        
        # 4. About Tab
        self.about_frame.configure(bg=theme_colors["bg_main"])
        self.about_header.configure(bg=theme_colors["bg_main"])
        self.about_title.configure(bg=theme_colors["bg_main"], fg=theme_colors["fg_title"])
        self.about_card.configure(bg=theme_colors["bg_card"], highlightbackground=theme_colors["border"])
        self.about_lbl.configure(bg=theme_colors["bg_card"], fg=theme_colors["fg_body"])
        
        # Refresh widgets to redraw correctly
        self.root.update_idletasks()

if __name__ == '__main__':
    root = tk.Tk()
    app = CropPredictionApp(root)
    # Apply initial theme
    app.apply_theme()
    root.mainloop()
