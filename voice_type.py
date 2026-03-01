"""
Voice Type - Hold Shift to speak, release to type.
Uses Groq Whisper API for fast, accurate speech-to-text.
"""

__version__ = "2.2.0"
__author__ = "Anton AI Agent"

import sys
import os
import threading
import time
import json
import tempfile
import re
from pathlib import Path

if sys.stdout:
    sys.stdout.reconfigure(line_buffering=True)
if sys.stderr:
    sys.stderr.reconfigure(line_buffering=True)

print("Loading Voice Type...")

import keyboard
import pyperclip
import tkinter as tk
from tkinter import font as tkfont, ttk, messagebox
import pyaudio
import wave
import httpx
import pystray
from PIL import Image, ImageDraw

print("Ready!")

# Config
CONFIG_FILE = Path.home() / ".voice-type-config.json"
MACROS_FILE = Path.home() / ".voice-type-macros.json"
STATS_FILE = Path.home() / ".voice-type-stats.json"
SAMPLE_RATE = 16000

# Default filter words - common filler words the model outputs when nothing is said
DEFAULT_FILTER_WORDS = ["thank you", "thanks", "thank you.", "thanks."]

# Default macros
DEFAULT_MACROS = {
    "signature": "Best regards,",
    "cheers": "Cheers,",
    "thanks ahead": "Thanks in advance!",
    "let me check": "Let me check on that and get back to you.",
    "sounds good": "Sounds good, let me know if you need anything else!",
    "will do": "Will do!",
    "today date": "{{DATE}}",
    "now time": "{{TIME}}",
}

# Statistics tracking
DEFAULT_STATS = {
    "total_words": 0,
    "total_sessions": 0,
    "total_transcriptions": 0,
    "total_minutes": 0.0,
    "first_used": None,
    "last_used": None,
}

# History storage
HISTORY_FILE = Path.home() / ".voice-type-history.json"
HISTORY = []

# Load config
config_data = {
    "api_key": "",
    "mic_index": None,
    "hotkey": "shift",
    "accounting_mode": False,
    "history_enabled": True,
    "quicken_mode": False,  # Type character-by-character for Quicken compatibility
    "language": "auto",  # Auto-detect language or specify (en, es, fr, de, etc.)
    "auto_stop": False,  # Auto-stop recording after silence
    "silence_threshold": 2.0,  # Seconds of silence before auto-stop
    "always_on_top": True,  # Widget always on top
    "autohide": True,  # Auto-hide widget after transcription
    "compact_mode": False,  # Smaller widget
    "accent_color": "#6366f1",  # Custom accent color
    "save_audio": False,  # Save audio recordings
    "auto_copy": True,  # Auto-copy transcription to clipboard
    "show_timer": True,  # Show recording timer
    "minimize_startup": False,  # Start minimized to tray
    "widget_position": None,  # Remember widget position [x, y]
    # Custom vocabulary - words to prioritize in transcription
    "custom_vocabulary": [],
    # Word replacements - auto-replace words
    "word_replacements": {},
    # Granular punctuation controls
    "punctuation": {
        "periods": True,
        "commas": True,
        "question_marks": True,
        "exclamation_marks": True,
        "colons": True,
        "semicolons": True,
        "quotes": True,
    },
    "filter_words": DEFAULT_FILTER_WORDS
}
if CONFIG_FILE.exists():
    try:
        config_data = json.loads(CONFIG_FILE.read_text())
    except:
        pass

# Also try old config file for backward compatibility
old_config = Path.home() / "voice-type-config.txt"
if not config_data.get("api_key") and old_config.exists():
    config_data["api_key"] = old_config.read_text().strip()

API_KEY = config_data.get("api_key", "")
MIC_INDEX = config_data.get("mic_index")
HOTKEY = config_data.get("hotkey", "shift")
ACCOUNTING_MODE = config_data.get("accounting_mode", False)
DOUBLE_SPACE_PERIOD = config_data.get("double_space_period", False)
CAPITALIZE_SENTENCES = config_data.get("capitalize_sentences", True)  # Auto-capitalize first letter
SMART_QUOTES = config_data.get("smart_quotes", False)
ACCOUNTING_COMMA = config_data.get("accounting_comma", False)
CASUAL_MODE = config_data.get("casual_mode", False)
THEME = config_data.get("theme", "dark")  # "dark" or "light"
HISTORY_ENABLED = config_data.get("history_enabled", True)
QUICKEN_MODE = config_data.get("quicken_mode", False)  # Character-by-character typing for Quicken
LANGUAGE = config_data.get("language", "auto")  # Auto-detect or specify language
AUTO_STOP = config_data.get("auto_stop", False)  # Auto-stop recording after silence
SILENCE_THRESHOLD = config_data.get("silence_threshold", 2.0)  # Seconds of silence before auto-stop
ALWAYS_ON_TOP = config_data.get("always_on_top", True)  # Widget always on top
AUTOHIDE_ENABLED = config_data.get("autohide", True)  # Auto-hide widget after transcription
COMPACT_MODE = config_data.get("compact_mode", False)  # Smaller widget
ACCENT_COLOR = config_data.get("accent_color", "#6366f1")  # Custom accent color
SAVE_AUDIO = config_data.get("save_audio", False)  # Save audio recordings
AUTO_COPY = config_data.get("auto_copy", True)  # Auto-copy transcription to clipboard
SHOW_TIMER = config_data.get("show_timer", True)  # Show recording timer
MINIMIZE_STARTUP = config_data.get("minimize_startup", False)  # Start minimized to tray
WIDGET_POSITION = config_data.get("widget_position", None)  # Remember widget position
CUSTOM_VOCABULARY = config_data.get("custom_vocabulary", [])  # Custom words for transcription
WORD_REPLACEMENTS = config_data.get("word_replacements", {})  # Auto-replace words
FILTER_WORDS = config_data.get("filter_words", DEFAULT_FILTER_WORDS)

# Granular punctuation settings
PUNCTUATION = config_data.get("punctuation", {
    "periods": True,
    "commas": True,
    "question_marks": True,
    "exclamation_marks": True,
    "colons": True,
    "semicolons": True,
    "quotes": True,
})

# Load macros
MACROS = DEFAULT_MACROS.copy()
if MACROS_FILE.exists():
    try:
        user_macros = json.loads(MACROS_FILE.read_text())
        MACROS.update(user_macros)
        print(f"[startup] Loaded {len(user_macros)} custom macros")
    except:
        pass

# Load statistics
STATS = DEFAULT_STATS.copy()
if STATS_FILE.exists():
    try:
        saved_stats = json.loads(STATS_FILE.read_text())
        STATS.update(saved_stats)
    except:
        pass

# Load history
if HISTORY_FILE.exists() and HISTORY_ENABLED:
    try:
        HISTORY = json.loads(HISTORY_FILE.read_text())
        print(f"[startup] Loaded {len(HISTORY)} history items")
    except:
        pass

# Debug: Show config on startup
print(f"[startup] Config file: {CONFIG_FILE}")
print(f"[startup] ACCOUNTING_MODE from config: {ACCOUNTING_MODE}")
print(f"[startup] Full config: {config_data}")


# Auto-start helper functions
def set_autostart(enabled):
    """Enable or disable auto-start on Windows boot."""
    if sys.platform != "win32":
        return False
    
    try:
        import winreg
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        app_name = "VoiceType"
        
        if enabled:
            # Get the path to the executable or script
            if getattr(sys, 'frozen', False):
                # Running as compiled exe
                exe_path = sys.executable
            else:
                # Running as script
                exe_path = f'"{sys.executable}" "{Path(__file__).resolve()}"'
            
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(key, app_name, 0, winreg.REG_SZ, exe_path)
            winreg.CloseKey(key)
            print(f"[autostart] Enabled: {exe_path}")
            return True
        else:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE)
            try:
                winreg.DeleteValue(key, app_name)
                print("[autostart] Disabled")
            except FileNotFoundError:
                pass
            winreg.CloseKey(key)
            return True
    except Exception as e:
        print(f"[autostart] Error: {e}")
        return False


# State
class State:
    recording = False
    running = True


state = State()
settings_open = False
tray_icon = None
last_transcription = ""  # Store last transcription for copy feature
last_transcription = ""  # Store last transcription for copy feature


class FloatingWidget:
    """Floating window to show status with modern design."""

    def __init__(self):
        self.root = tk.Tk()
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", ALWAYS_ON_TOP)
        
        # Show in taskbar - this makes it behave like a normal app
        self.root.attributes("-toolwindow", False)

        # Theme support - dark or light
        self.apply_theme(THEME)
    
    def apply_theme(self, theme_name):
        """Apply color theme (dark or light) with custom accent color."""
        # Parse custom accent color or use default
        accent = ACCENT_COLOR if ACCENT_COLOR else "#6366f1"
        
        if theme_name == "light":
            # Light theme colors
            self.bg_dark = "#f5f5f5"
            self.bg_medium = "#ffffff"
            self.bg_light = "#e8e8e8"
            self.accent_primary = accent
            self.accent_secondary = "#6b5b95"
            self.accent_success = "#28a745"
            self.accent_warning = "#ffc107"
            self.text_primary = "#1a1a1a"
            self.text_secondary = "#666666"
            self.border_color = accent
        else:
            # Dark theme colors (default)
            self.bg_dark = "#1a1a2e"
            self.bg_medium = "#16213e"
            self.bg_light = "#0f3460"
            self.accent_primary = accent
            self.accent_secondary = "#533483"
            self.accent_success = "#00ff88"
            self.accent_warning = "#ffc107"
            self.text_primary = "#ffffff"
            self.text_secondary = "#a0a0a0"
            self.border_color = accent

        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # Widget dimensions - compact or normal
        if COMPACT_MODE:
            widget_width = 200
            widget_height = 60
        else:
            widget_width = 320
            widget_height = 130  # Increased for word count
        
        # Use saved position or center horizontally near bottom
        if WIDGET_POSITION and len(WIDGET_POSITION) == 2:
            x, y = WIDGET_POSITION
            # Make sure position is still on screen
            if x < 0 or x > screen_width - widget_width:
                x = (screen_width - widget_width) // 2
            if y < 0 or y > screen_height - widget_height:
                y = screen_height - widget_height - 100
        else:
            x = (screen_width - widget_width) // 2
            y = screen_height - widget_height - 100
        
        self.root.geometry(f"{widget_width}x{widget_height}+{x}+{y}")
        
        # Track current position for saving
        self.current_x = x
        self.current_y = y

        self.root.configure(bg=self.bg_dark)

        # Main frame with border
        self.main_frame = tk.Frame(
            self.root, 
            bg=self.bg_dark,
            highlightbackground=self.border_color,
            highlightthickness=2
        )
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)

        # Content frame
        self.content_frame = tk.Frame(self.main_frame, bg=self.bg_medium)
        self.content_frame.pack(fill=tk.BOTH, expand=True, padx=3, pady=3)

        # Status indicator row
        self.status_frame = tk.Frame(self.content_frame, bg=self.bg_medium)
        self.status_frame.pack(fill=tk.X, padx=15, pady=(12, 5))

        # Status icon/label
        self.status_font = tkfont.Font(family="Segoe UI", size=12, weight="bold")
        self.status_label = tk.Label(
            self.status_frame,
            text="● Ready",
            font=self.status_font,
            fg=self.accent_success,
            bg=self.bg_medium,
        )
        self.status_label.pack(side=tk.LEFT)

        # Recording indicator (hidden by default)
        self.rec_indicator = tk.Label(
            self.status_frame,
            text="",
            font=("Segoe UI", 10),
            fg=self.accent_primary,
            bg=self.bg_medium,
        )
        self.rec_indicator.pack(side=tk.RIGHT)
        
        # Timer label for recording duration
        self.timer_label = tk.Label(
            self.status_frame,
            text="",
            font=("Segoe UI", 10),
            fg=self.text_secondary,
            bg=self.bg_medium,
        )
        self.timer_label.pack(side=tk.RIGHT, padx=(0, 10))

        # Separator line
        self.separator = tk.Frame(self.content_frame, height=1, bg=self.border_color)
        self.separator.pack(fill=tk.X, padx=15, pady=8)

        # Text display
        self.text_font = tkfont.Font(family="Segoe UI", size=11)
        self.text_label = tk.Label(
            self.content_frame,
            text=f"Hold {HOTKEY.upper()} to speak...",
            font=self.text_font,
            fg=self.text_secondary,
            bg=self.bg_medium,
            wraplength=280,
        )
        self.text_label.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 5))
        
        # Keyboard shortcut hint
        self.hint_label = tk.Label(
            self.content_frame,
            text=f"Press {HOTKEY.upper()} to record | Right-click tray for settings",
            font=("Segoe UI", 8),
            fg=self.text_secondary,
            bg=self.bg_medium,
        )
        self.hint_label.pack(fill=tk.X, padx=15, pady=(0, 5))
        
        # Audio level indicator (progress bar style)
        self.level_frame = tk.Frame(self.content_frame, bg=self.bg_medium)
        self.level_frame.pack(fill=tk.X, padx=15, pady=(0, 5))
        
        self.level_canvas = tk.Canvas(
            self.level_frame,
            width=280,
            height=8,
            bg=self.bg_light,
            highlightthickness=0
        )
        self.level_canvas.pack(fill=tk.X)
        
        # Initialize level bar (green, shows mic input level)
        self.level_bar = self.level_canvas.create_rectangle(
            0, 0, 0, 8,
            fill=self.accent_success,
            outline=""
        )
        self.current_level = 0

        # Status colors
        self.colors = {
            "ready": (self.accent_success, "● Ready"),
            "recording": (self.accent_primary, "● Recording"),
            "processing": (self.accent_warning, "◐ Transcribing"),
            "done": (self.accent_success, "✓ Done"),
            "error": (self.accent_primary, "✕ Error"),
            "nokey": (self.accent_primary, "✕ No API Key"),
        }

        # Drag functionality
        self.drag_start_x = 0
        self.drag_start_y = 0
        self.content_frame.bind("<Button-1>", self.start_drag)
        self.content_frame.bind("<B1-Motion>", self.drag)
        self.status_label.bind("<Button-1>", self.start_drag)
        self.status_label.bind("<B1-Motion>", self.drag)
        self.text_label.bind("<Button-1>", self.start_drag)
        self.text_label.bind("<B1-Motion>", self.drag)
        
        # Right-click context menu
        self.context_menu = tk.Menu(self.root, tearoff=0, bg=self.bg_dark, fg=self.text_primary,
                                   activebackground=self.accent_primary, activeforeground="white")
        self.context_menu.add_command(label="📋 Copy Last", command=self.copy_last)
        self.context_menu.add_command(label="📜 History", command=self.open_history)
        self.context_menu.add_command(label="📁 Transcribe File...", command=lambda: None)  # Placeholder
        self.context_menu.add_separator()
        self.context_menu.add_command(label="⚙️ Settings", command=self.open_settings)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="📌 Always on Top", command=self.toggle_topmost)
        self.context_menu.add_command(label="👁️ Show/Hide", command=self.toggle_visibility)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="❌ Minimize", command=self.hide_widget)
        
        # Bind right-click
        self.content_frame.bind("<Button-3>", self.show_context_menu)
        self.status_label.bind("<Button-3>", self.show_context_menu)
        self.text_label.bind("<Button-3>", self.show_context_menu)

        # Start hidden
        self.hidden = True
        self.root.withdraw()

    def show_context_menu(self, event):
        """Show right-click context menu."""
        try:
            self.context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.context_menu.grab_release()

    def copy_last(self):
        """Copy last transcription."""
        global last_transcription
        if last_transcription:
            pyperclip.copy(last_transcription)

    def toggle_topmost(self):
        """Toggle always on top."""
        global ALWAYS_ON_TOP
        ALWAYS_ON_TOP = not ALWAYS_ON_TOP
        self.root.attributes("-topmost", ALWAYS_ON_TOP)
        config_data["always_on_top"] = ALWAYS_ON_TOP
        CONFIG_FILE.write_text(json.dumps(config_data))

    def toggle_visibility(self):
        """Toggle widget visibility."""
        if self.hidden:
            self.show_widget()
        else:
            self.hide_widget()

    def start_drag(self, event):
        self.drag_start_x = event.x
        self.drag_start_y = event.y

    def drag(self, event):
        x = self.root.winfo_x() + event.x - self.drag_start_x
        y = self.root.winfo_y() + event.y - self.drag_start_y
        self.root.geometry(f"+{x}+{y}")
        self.current_x = x
        self.current_y = y
        self.save_position()

    def save_position(self):
        """Save widget position to config."""
        config_data["widget_position"] = [self.current_x, self.current_y]
        CONFIG_FILE.write_text(json.dumps(config_data))

    def hide_widget(self):
        self.hidden = True
        self.root.withdraw()

    def show_widget(self):
        self.hidden = False
        self.root.deiconify()
    
    def update_level(self, level):
        """Update audio level indicator (0.0 to 1.0)."""
        if not hasattr(self, 'level_canvas'):
            return

        # Smooth the level changes
        self.current_level = self.current_level * 0.7 + level * 0.3

        # Update bar width
        canvas_width = 280
        bar_width = int(canvas_width * min(self.current_level, 1.0))

        self.level_canvas.coords(self.level_bar, 0, 0, bar_width, 8)

        # Change color based on level
        if self.current_level < 0.3:
            color = self.accent_success  # Green - quiet
        elif self.current_level < 0.7:
            color = self.accent_warning  # Yellow - good
        else:
            color = "#ff4444"  # Red - too loud

        self.level_canvas.itemconfig(self.level_bar, fill=color)

    def start_drag(self, event):
        """Record starting position for drag."""
        self.drag_start_x = event.x
        self.drag_start_y = event.y

    def do_drag(self, event):
        """Handle widget dragging."""
        x = self.root.winfo_x() + (event.x - self.drag_start_x)
        y = self.root.winfo_y() + (event.y - self.drag_start_y)
        self.root.geometry(f"+{x}+{y}")

    def open_settings(self):
        global settings_open
        if settings_open:
            return
        settings_open = True

        win = tk.Toplevel()
        win.title(f"VoiceType v{__version__} Settings")
        win.geometry("500x700")
        win.configure(bg=self.bg_dark)
        win.resizable(False, False)

        # Header
        header_frame = tk.Frame(win, bg=self.bg_medium, height=50)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        tk.Label(
            header_frame, 
            text="⚙ Voice Type Settings", 
            font=("Segoe UI", 14, "bold"),
            fg=self.border_color,
            bg=self.bg_medium
        ).pack(pady=12)

        # Separator
        tk.Frame(win, height=2, bg=self.border_color).pack(fill=tk.X)

        # Content frame
        content = tk.Frame(win, bg=self.bg_dark)
        content.pack(fill=tk.BOTH, expand=True, padx=25, pady=15)

        # Style for inputs
        input_style = {
            "bg": self.bg_light,
            "fg": self.text_primary,
            "insertbackground": self.text_primary,
            "relief": "flat",
            "font": ("Segoe UI", 10)
        }
        
        label_style = {
            "bg": self.bg_dark,
            "fg": self.text_secondary,
            "font": ("Segoe UI", 10)
        }

        # API Key Section
        tk.Label(content, text="🔐 API Key", font=("Segoe UI", 11, "bold"), 
                fg=self.border_color, bg=self.bg_dark).pack(anchor="w", pady=(0, 5))
        tk.Label(content, text="Groq API Key:", **label_style).pack(anchor="w")
        
        api_entry = tk.Entry(content, width=50, **input_style)
        api_entry.pack(fill=tk.X, pady=(5, 15))
        api_entry.insert(0, API_KEY)

        # Microphone Section
        tk.Label(content, text="🎤 Microphone", font=("Segoe UI", 11, "bold"),
                fg=self.border_color, bg=self.bg_dark).pack(anchor="w", pady=(0, 5))
        tk.Label(content, text="Select input device:", **label_style).pack(anchor="w")

        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Settings.TCombobox", 
                       fieldbackground=self.bg_light, 
                       background=self.bg_light, 
                       foreground=self.text_primary,
                       arrowcolor=self.border_color,
                       borderwidth=0)
        style.map("Settings.TCombobox",
                 fieldbackground=[('readonly', self.bg_light)],
                 selectbackground=[('readonly', self.border_color)],
                 selectforeground=[('readonly', self.bg_dark)])
        
        mic_combo = ttk.Combobox(content, width=47, style="Settings.TCombobox", font=("Segoe UI", 10))
        mic_combo.pack(fill=tk.X, pady=(5, 15))

        # Get mics
        p = pyaudio.PyAudio()
        mics = []
        for i in range(p.get_device_count()):
            dev = p.get_device_info_by_index(i)
            if dev["maxInputChannels"] > 0:
                mics.append((i, dev["name"]))
        p.terminate()

        mic_combo["values"] = [f"{i}: {n}" for i, n in mics]

        if MIC_INDEX is not None:
            for idx, (i, n) in enumerate(mics):
                if i == MIC_INDEX:
                    mic_combo.current(idx)
                    break
        elif mics:
            mic_combo.current(0)

        # Hotkey Section
        tk.Label(content, text="⌨ Push-to-Talk Key", font=("Segoe UI", 11, "bold"),
                fg=self.border_color, bg=self.bg_dark).pack(anchor="w", pady=(0, 5))
        
        hotkey_frame = tk.Frame(content, bg=self.bg_dark)
        hotkey_frame.pack(fill=tk.X, pady=(5, 15))

        hotkey_var = tk.StringVar(value=HOTKEY.upper())
        hotkey_entry = tk.Entry(
            hotkey_frame, 
            width=10,
            bg=self.bg_light,
            fg=self.border_color,
            insertbackground=self.border_color,
            textvariable=hotkey_var,
            font=("Segoe UI", 12, "bold"),
            justify="center",
            relief="flat"
        )
        hotkey_entry.pack(side=tk.LEFT)
        hotkey_entry.config(state="readonly")
        
        def on_hotkey_focus(event):
            hotkey_entry.config(state="normal")
            hotkey_var.set("...")
            hotkey_entry.config(state="readonly")
        
        def on_hotkey_keypress(event):
            key_name = None
            special_keys = {
                16: "shift", 17: "ctrl", 18: "alt",
                32: "space",
                112: "f1", 113: "f2", 114: "f3", 115: "f4",
                116: "f5", 117: "f6", 118: "f7", 119: "f8",
                120: "f9", 121: "f10", 122: "f11", 123: "f12",
            }
            
            if event.keycode in special_keys:
                key_name = special_keys[event.keycode]
            elif event.keysym and len(event.keysym) == 1:
                key_name = event.keysym.lower()
            elif event.keysym:
                key_name = event.keysym.lower()
            
            if key_name:
                hotkey_entry.config(state="normal")
                hotkey_var.set(key_name.upper())
                hotkey_entry.config(state="readonly")
            return "break"
        
        hotkey_entry.bind("<FocusIn>", on_hotkey_focus)
        hotkey_entry.bind("<KeyPress>", on_hotkey_keypress)

        tk.Label(hotkey_frame, text="  (click and press a key)", 
                bg=self.bg_dark, fg=self.text_secondary, font=("Segoe UI", 9)).pack(side=tk.LEFT)

        # Features Section
        tk.Label(content, text="✨ Features", font=("Segoe UI", 11, "bold"),
                fg=self.border_color, bg=self.bg_dark).pack(anchor="w", pady=(0, 5))
        
        accounting_var = tk.BooleanVar(value=ACCOUNTING_MODE)
        accounting_check = tk.Checkbutton(
            content,
            text="🔢 Accounting Mode (convert words like 'one' to '1')",
            variable=accounting_var,
            bg=self.bg_dark,
            fg=self.text_primary,
            selectcolor=self.bg_light,
            activebackground=self.bg_dark,
            activeforeground=self.text_primary,
            font=("Segoe UI", 10),
            cursor="hand2"
        )
        accounting_check.pack(anchor="w", pady=(5, 5))
        
        # Accounting comma formatting option
        comma_var = tk.BooleanVar(value=ACCOUNTING_COMMA)
        comma_check = tk.Checkbutton(
            content,
            text="   └─ Add commas to large numbers (e.g., '1,234,567')",
            variable=comma_var,
            bg=self.bg_dark,
            fg=self.text_secondary,
            selectcolor=self.bg_light,
            activebackground=self.bg_dark,
            activeforeground=self.text_primary,
            font=("Segoe UI", 9),
            cursor="hand2"
        )
        comma_check.pack(anchor="w", pady=(0, 5))
        
        # Casual mode option
        casual_var = tk.BooleanVar(value=CASUAL_MODE)
        casual_check = tk.Checkbutton(
            content,
            text="💬 Casual Mode (lowercase, no formal punctuation)",
            variable=casual_var,
            bg=self.bg_dark,
            fg=self.text_primary,
            selectcolor=self.bg_light,
            activebackground=self.bg_dark,
            activeforeground=self.text_primary,
            font=("Segoe UI", 10),
            cursor="hand2"
        )
        casual_check.pack(anchor="w", pady=(5, 15))

        # Filter Words
        tk.Label(content, text="🚫 Filter Words", font=("Segoe UI", 11, "bold"),
                fg=self.border_color, bg=self.bg_dark).pack(anchor="w", pady=(0, 5))
        tk.Label(content, text="Phrases to block (comma-separated):", **label_style).pack(anchor="w")

        filter_entry = tk.Entry(content, width=50, **input_style)
        filter_entry.pack(fill=tk.X, pady=(5, 5))
        filter_entry.insert(0, ", ".join(FILTER_WORDS) if FILTER_WORDS else "")
        
        tk.Label(content, text="Example: thank you, thanks", 
                bg=self.bg_dark, fg=self.text_secondary, font=("Segoe UI", 9)).pack(anchor="w", pady=(0, 15))

        # Statistics Section
        tk.Label(content, text="📊 Statistics", font=("Segoe UI", 11, "bold"),
                fg=self.border_color, bg=self.bg_dark).pack(anchor="w", pady=(0, 5))
        
        stats_frame = tk.Frame(content, bg=self.bg_light, padx=10, pady=10)
        stats_frame.pack(fill=tk.X, pady=(5, 15))
        
        stats_labels = [
            f"📝 Words typed: {STATS.get('total_words', 0):,}",
            f"🎤 Transcriptions: {STATS.get('total_transcriptions', 0):,}",
            f"📅 First used: {STATS.get('first_used', 'Never') or 'Never'}",
            f"🕒 Last used: {STATS.get('last_used', 'Never') or 'Never'}",
        ]
        
        for stat_text in stats_labels:
            tk.Label(stats_frame, text=stat_text, bg=self.bg_light, fg=self.text_primary,
                    font=("Segoe UI", 10)).pack(anchor="w")
        
        def reset_stats():
            global STATS
            STATS = DEFAULT_STATS.copy()
            STATS_FILE.write_text(json.dumps(STATS, indent=2))
            stats_updated_label.config(text="✓ Stats reset!")
            win.after(1500, lambda: stats_updated_label.config(text=""))
        
        stats_btn_frame = tk.Frame(stats_frame, bg=self.bg_light)
        stats_btn_frame.pack(anchor="w", pady=(10, 0))
        
        stats_updated_label = tk.Label(stats_btn_frame, text="", bg=self.bg_light, 
                                       fg=self.accent_success, font=("Segoe UI", 9))
        stats_updated_label.pack(side=tk.LEFT)
        
        tk.Button(stats_btn_frame, text="Reset Stats", bg=self.bg_medium, fg=self.text_primary,
                 command=reset_stats, font=("Segoe UI", 9), relief="flat", cursor="hand2").pack(side=tk.LEFT, padx=(0, 5))

        # Macros Section (collapsible)
        tk.Label(content, text="🔧 Voice Macros", font=("Segoe UI", 11, "bold"),
                fg=self.border_color, bg=self.bg_dark).pack(anchor="w", pady=(0, 5))
        tk.Label(content, text="Voice commands that expand to full text:", 
                bg=self.bg_dark, fg=self.text_secondary, font=("Segoe UI", 9)).pack(anchor="w")
        
        # Show a few example macros
        macros_text = tk.Text(content, height=4, width=50, bg=self.bg_light, fg=self.text_primary,
                             font=("Segoe UI", 9), relief="flat", wrap=tk.WORD)
        macros_text.pack(fill=tk.X, pady=(5, 5))
        
        example_macros = list(MACROS.items())[:5]
        macros_display = "\n".join([f'"{k}" → "{v[:30]}..."' if len(v) > 30 else f'"{k}" → "{v}"' 
                                   for k, v in example_macros])
        macros_text.insert("1.0", macros_display)
        macros_text.config(state="disabled")
        
        tk.Label(content, text=f"💡 {len(MACROS)} macros loaded. Edit ~/.voice-type-macros.json to customize.", 
                bg=self.bg_dark, fg=self.text_secondary, font=("Segoe UI", 9)).pack(anchor="w", pady=(0, 15))

        # Auto-start option (Windows only)
        autostart_var = tk.BooleanVar(value=config_data.get("autostart", False))
        if sys.platform == "win32":
            autostart_check = tk.Checkbutton(
                content,
                text="🚀 Start with Windows (auto-launch on boot)",
                variable=autostart_var,
                bg=self.bg_dark,
                fg=self.text_primary,
                selectcolor=self.bg_light,
                activebackground=self.bg_dark,
                activeforeground=self.text_primary,
                font=("Segoe UI", 10),
                cursor="hand2"
            )
            autostart_check.pack(anchor="w", pady=(0, 15))

        # Theme selection
        tk.Label(content, text="🎨 Theme", font=("Segoe UI", 11, "bold"),
                fg=self.border_color, bg=self.bg_dark).pack(anchor="w", pady=(0, 5))
        
        theme_frame = tk.Frame(content, bg=self.bg_dark)
        theme_frame.pack(fill=tk.X, pady=(0, 15))
        
        theme_var = tk.StringVar(value=THEME)
        theme_combo = ttk.Combobox(theme_frame, textvariable=theme_var, 
                                   values=["dark", "light"], state="readonly", width=20)
        theme_combo.pack(side=tk.LEFT)
        tk.Label(theme_frame, text="  Restart app to apply theme change", 
                bg=self.bg_dark, fg=self.text_secondary, font=("Segoe UI", 9)).pack(side=tk.LEFT)

        # Quicken mode (character-by-character typing for compatibility)
        tk.Label(content, text="💼 App Compatibility", font=("Segoe UI", 11, "bold"),
                fg=self.border_color, bg=self.bg_dark).pack(anchor="w", pady=(0, 5))
        
        quicken_var = tk.BooleanVar(value=QUICKEN_MODE)
        quicken_check = tk.Checkbutton(
            content,
            text="🧾 Quicken Mode (character-by-character typing)",
            variable=quicken_var,
            bg=self.bg_dark,
            fg=self.text_primary,
            selectcolor=self.bg_light,
            activebackground=self.bg_dark,
            activeforeground=self.text_primary,
            font=("Segoe UI", 10),
            cursor="hand2"
        )
        quicken_check.pack(anchor="w", pady=(0, 5))
        tk.Label(content, text="   Enable if text doesn't paste correctly in Quicken or similar apps", 
                bg=self.bg_dark, fg=self.text_secondary, font=("Segoe UI", 9)).pack(anchor="w", pady=(0, 15))

        # Language selection
        tk.Label(content, text="🌍 Language", font=("Segoe UI", 11, "bold"),
                fg=self.border_color, bg=self.bg_dark).pack(anchor="w", pady=(0, 5))
        
        lang_frame = tk.Frame(content, bg=self.bg_dark)
        lang_frame.pack(fill=tk.X, pady=(0, 15))
        
        language_var = tk.StringVar(value=LANGUAGE)
        lang_options = ["auto", "en", "es", "fr", "de", "it", "pt", "ru", "ja", "ko", "zh", "ar", "hi", "nl", "pl", "tr"]
        lang_combo = ttk.Combobox(lang_frame, textvariable=language_var, 
                                   values=lang_options, state="readonly", width=20)
        lang_combo.pack(side=tk.LEFT)
        tk.Label(lang_frame, text="  Auto = detect automatically", 
                bg=self.bg_dark, fg=self.text_secondary, font=("Segoe UI", 9)).pack(side=tk.LEFT)

        # Auto-stop on silence
        tk.Label(content, text="🎤 Recording", font=("Segoe UI", 11, "bold"),
                fg=self.border_color, bg=self.bg_dark).pack(anchor="w", pady=(0, 5))
        
        autostop_var = tk.BooleanVar(value=AUTO_STOP)
        autostop_check = tk.Checkbutton(
            content,
            text="🔇 Auto-stop after silence (hands-free mode)",
            variable=autostop_var,
            bg=self.bg_dark,
            fg=self.text_primary,
            selectcolor=self.bg_light,
            activebackground=self.bg_dark,
            activeforeground=self.text_primary,
            font=("Segoe UI", 10),
            cursor="hand2"
        )
        autostop_check.pack(anchor="w", pady=(0, 5))
        tk.Label(content, text="   Automatically stops recording when you stop talking", 
                bg=self.bg_dark, fg=self.text_secondary, font=("Segoe UI", 9)).pack(anchor="w", pady=(0, 5))
        
        # Always on top toggle
        ontop_var = tk.BooleanVar(value=ALWAYS_ON_TOP)
        ontop_check = tk.Checkbutton(
            content,
            text="📌 Widget always on top",
            variable=ontop_var,
            bg=self.bg_dark,
            fg=self.text_primary,
            selectcolor=self.bg_light,
            activebackground=self.bg_dark,
            activeforeground=self.text_primary,
            font=("Segoe UI", 10),
            cursor="hand2"
        )
        ontop_check.pack(anchor="w", pady=(0, 5))
        tk.Label(content, text="   Disable if widget blocks other windows", 
                bg=self.bg_dark, fg=self.text_secondary, font=("Segoe UI", 9)).pack(anchor="w", pady=(0, 5))

        # Auto-hide toggle
        autohide_var = tk.BooleanVar(value=AUTOHIDE_ENABLED)
        autohide_check = tk.Checkbutton(
            content,
            text="🙈 Auto-hide widget after transcription",
            variable=autohide_var,
            bg=self.bg_dark,
            fg=self.text_primary,
            selectcolor=self.bg_light,
            activebackground=self.bg_dark,
            activeforeground=self.text_primary,
            font=("Segoe UI", 10),
            cursor="hand2"
        )
        autohide_check.pack(anchor="w", pady=(0, 5))

        # Compact mode toggle
        compact_var = tk.BooleanVar(value=COMPACT_MODE)
        compact_check = tk.Checkbutton(
            content,
            text="📱 Compact mode (smaller widget)",
            variable=compact_var,
            bg=self.bg_dark,
            fg=self.text_primary,
            selectcolor=self.bg_light,
            activebackground=self.bg_dark,
            activeforeground=self.text_primary,
            font=("Segoe UI", 10),
            cursor="hand2"
        )
        compact_check.pack(anchor="w", pady=(0, 5))
        tk.Label(content, text="   Smaller widget for minimal screen space", 
                bg=self.bg_dark, fg=self.text_secondary, font=("Segoe UI", 9)).pack(anchor="w", pady=(0, 15))

        # Accent color selection
        tk.Label(content, text="🎨 Accent Color", font=("Segoe UI", 11, "bold"),
                fg=self.border_color, bg=self.bg_dark).pack(anchor="w", pady=(0, 5))
        
        color_frame = tk.Frame(content, bg=self.bg_dark)
        color_frame.pack(fill=tk.X, pady=(0, 15))
        
        color_var = tk.StringVar(value=ACCENT_COLOR)
        color_options = [
            ("💜 Purple", "#6366f1"),
            ("💙 Blue", "#3b82f6"),
            ("💚 Green", "#22c55e"),
            ("❤️ Red", "#ef4444"),
            ("🧡 Orange", "#f97316"),
            ("💗 Pink", "#ec4899"),
        ]
        
        color_combo = ttk.Combobox(color_frame, textvariable=color_var,
                                   values=[c[1] for c in color_options],
                                   state="readonly", width=10)
        color_combo.pack(side=tk.LEFT)
        
        # Color preview
        color_preview = tk.Label(color_frame, text="  Preview  ", bg=ACCENT_COLOR,
                                fg="white", font=("Segoe UI", 9))
        color_preview.pack(side=tk.LEFT, padx=10)
        
        def update_color_preview(*args):
            color_preview.configure(bg=color_var.get())
        color_var.trace("w", update_color_preview)

        # Custom Vocabulary section
        tk.Label(content, text="📖 Custom Vocabulary", font=("Segoe UI", 11, "bold"),
                fg=self.border_color, bg=self.bg_dark).pack(anchor="w", pady=(0, 5))
        tk.Label(content, text="   Words to prioritize in transcription (comma-separated)", 
                bg=self.bg_dark, fg=self.text_secondary, font=("Segoe UI", 9)).pack(anchor="w", pady=(0, 5))
        
        vocab_entry = tk.Entry(content, bg=self.bg_light, fg=self.text_primary,
                              insertbackground=self.text_primary,
                              font=("Segoe UI", 10), width=50)
        vocab_entry.insert(0, ", ".join(CUSTOM_VOCABULARY))
        vocab_entry.pack(anchor="w", pady=(0, 5))
        tk.Label(content, text="   Example: API, Kubernetes, PostgreSQL, WebSocket", 
                bg=self.bg_dark, fg=self.text_secondary, font=("Segoe UI", 9)).pack(anchor="w", pady=(0, 15))

        # Save audio recordings option
        save_audio_var = tk.BooleanVar(value=SAVE_AUDIO)
        save_audio_check = tk.Checkbutton(
            content,
            text="💾 Save audio recordings",
            variable=save_audio_var,
            bg=self.bg_dark,
            fg=self.text_primary,
            selectcolor=self.bg_light,
            activebackground=self.bg_dark,
            activeforeground=self.text_primary,
            font=("Segoe UI", 10),
            cursor="hand2"
        )
        save_audio_check.pack(anchor="w", pady=(0, 5))
        tk.Label(content, text="   Saves recordings to ~/VoiceType Recordings/", 
                bg=self.bg_dark, fg=self.text_secondary, font=("Segoe UI", 9)).pack(anchor="w", pady=(0, 5))
        
        # Auto-copy toggle
        auto_copy_var = tk.BooleanVar(value=AUTO_COPY)
        auto_copy_check = tk.Checkbutton(
            content,
            text="📋 Auto-copy to clipboard",
            variable=auto_copy_var,
            bg=self.bg_dark,
            fg=self.text_primary,
            selectcolor=self.bg_light,
            activebackground=self.bg_dark,
            activeforeground=self.text_primary,
            font=("Segoe UI", 10),
            cursor="hand2"
        )
        auto_copy_check.pack(anchor="w", pady=(0, 5))
        tk.Label(content, text="   Automatically copy transcription to clipboard", 
                bg=self.bg_dark, fg=self.text_secondary, font=("Segoe UI", 9)).pack(anchor="w", pady=(0, 5))
        
        # Show timer toggle
        show_timer_var = tk.BooleanVar(value=SHOW_TIMER)
        show_timer_check = tk.Checkbutton(
            content,
            text="⏱️ Show recording timer",
            variable=show_timer_var,
            bg=self.bg_dark,
            fg=self.text_primary,
            selectcolor=self.bg_light,
            activebackground=self.bg_dark,
            activeforeground=self.text_primary,
            font=("Segoe UI", 10),
            cursor="hand2"
        )
        show_timer_check.pack(anchor="w", pady=(0, 5))
        tk.Label(content, text="   Display recording duration while recording", 
                bg=self.bg_dark, fg=self.text_secondary, font=("Segoe UI", 9)).pack(anchor="w", pady=(0, 5))
        
        # Minimize on startup toggle
        minimize_startup_var = tk.BooleanVar(value=MINIMIZE_STARTUP)
        minimize_startup_check = tk.Checkbutton(
            content,
            text="📤 Start minimized to tray",
            variable=minimize_startup_var,
            bg=self.bg_dark,
            fg=self.text_primary,
            selectcolor=self.bg_light,
            activebackground=self.bg_dark,
            activeforeground=self.text_primary,
            font=("Segoe UI", 10),
            cursor="hand2"
        )
        minimize_startup_check.pack(anchor="w", pady=(0, 15))

        # Word Replacements section
        tk.Label(content, text="🔄 Word Replacements", font=("Segoe UI", 11, "bold"),
                fg=self.border_color, bg=self.bg_dark).pack(anchor="w", pady=(0, 5))
        tk.Label(content, text="   Auto-replace words (format: old=new, one per line)", 
                bg=self.bg_dark, fg=self.text_secondary, font=("Segoe UI", 9)).pack(anchor="w", pady=(0, 5))
        
        replacements_text = tk.Text(content, height=3, width=50, bg=self.bg_light, fg=self.text_primary,
                                   insertbackground=self.text_primary, font=("Segoe UI", 9))
        for old, new in WORD_REPLACEMENTS.items():
            replacements_text.insert(tk.END, f"{old}={new}\n")
        replacements_text.pack(anchor="w", pady=(0, 15))

        # Buttons
        btn_frame = tk.Frame(content, bg=self.bg_dark)
        btn_frame.pack(pady=20)

        def save():
            global API_KEY, MIC_INDEX, HOTKEY, ACCOUNTING_MODE, ACCOUNTING_COMMA, CASUAL_MODE, FILTER_WORDS, THEME, QUICKEN_MODE, LANGUAGE, AUTO_STOP, ALWAYS_ON_TOP, AUTOHIDE_ENABLED, COMPACT_MODE, ACCENT_COLOR, SAVE_AUDIO, AUTO_COPY, SHOW_TIMER, MINIMIZE_STARTUP, WORD_REPLACEMENTS
            API_KEY = api_entry.get().strip()
            idx = mic_combo.current()
            if idx >= 0 and mics:
                MIC_INDEX = mics[idx][0]
            
            new_hotkey = hotkey_var.get().lower()
            if new_hotkey and new_hotkey != "...":
                HOTKEY = new_hotkey

            ACCOUNTING_MODE = accounting_var.get()
            ACCOUNTING_COMMA = comma_var.get()
            CASUAL_MODE = casual_var.get()
            THEME = theme_var.get()
            QUICKEN_MODE = quicken_var.get()
            LANGUAGE = language_var.get()
            AUTO_STOP = autostop_var.get()
            ALWAYS_ON_TOP = ontop_var.get()
            AUTOHIDE_ENABLED = autohide_var.get()
            COMPACT_MODE = compact_var.get()
            ACCENT_COLOR = color_var.get()
            SAVE_AUDIO = save_audio_var.get()
            AUTO_COPY = auto_copy_var.get()
            SHOW_TIMER = show_timer_var.get()
            MINIMIZE_STARTUP = minimize_startup_var.get()
            
            # Parse word replacements
            replacements_text_val = replacements_text.get("1.0", tk.END).strip()
            WORD_REPLACEMENTS = {}
            for line in replacements_text_val.split("\n"):
                if "=" in line:
                    parts = line.split("=", 1)
                    if len(parts) == 2:
                        old, new = parts[0].strip(), parts[1].strip()
                        if old and new:
                            WORD_REPLACEMENTS[old] = new
            
            # Parse custom vocabulary
            vocab_text = vocab_entry.get().strip()
            if vocab_text:
                CUSTOM_VOCABULARY = [w.strip() for w in vocab_text.split(",") if w.strip()]
            else:
                CUSTOM_VOCABULARY = []
            
            filter_text_val = filter_entry.get().strip()
            if filter_text_val:
                FILTER_WORDS = [w.strip() for w in filter_text_val.split(",") if w.strip()]
            else:
                FILTER_WORDS = []
            
            # Handle autostart (Windows only)
            if sys.platform == "win32" and 'autostart_var' in dir():
                autostart_enabled = autostart_var.get()
                config_data["autostart"] = autostart_enabled
                set_autostart(autostart_enabled)

            config_data["api_key"] = API_KEY
            config_data["mic_index"] = MIC_INDEX
            config_data["hotkey"] = HOTKEY
            config_data["accounting_mode"] = ACCOUNTING_MODE
            config_data["accounting_comma"] = ACCOUNTING_COMMA
            config_data["casual_mode"] = CASUAL_MODE
            config_data["theme"] = THEME
            config_data["quicken_mode"] = QUICKEN_MODE
            config_data["language"] = LANGUAGE
            config_data["auto_stop"] = AUTO_STOP
            config_data["always_on_top"] = ALWAYS_ON_TOP
            config_data["autohide"] = AUTOHIDE_ENABLED
            config_data["compact_mode"] = COMPACT_MODE
            config_data["accent_color"] = ACCENT_COLOR
            config_data["save_audio"] = SAVE_AUDIO
            config_data["auto_copy"] = AUTO_COPY
            config_data["show_timer"] = SHOW_TIMER
            config_data["minimize_startup"] = MINIMIZE_STARTUP
            config_data["word_replacements"] = WORD_REPLACEMENTS
            config_data["widget_position"] = [widget.current_x, widget.current_y] if widget else WIDGET_POSITION
            config_data["custom_vocabulary"] = CUSTOM_VOCABULARY
            config_data["filter_words"] = FILTER_WORDS
            CONFIG_FILE.write_text(json.dumps(config_data))
            
            # Apply always-on-top setting immediately
            if widget:
                widget.root.attributes("-topmost", ALWAYS_ON_TOP)

            if tray_icon:
                tray_icon.title = f"VoiceType v{__version__} (Hold {HOTKEY.upper()})"

            save_btn.config(text="✓ Saved!", bg=self.accent_success)
            win.after(1500, lambda: save_btn.config(text="Save", bg=self.border_color))

        def reset_defaults():
            """Reset all settings to defaults."""
            if messagebox.askyesno("Reset Settings", "Reset all settings to defaults?\n\nAPI key will be preserved."):
                global config_data, HOTKEY, ACCOUNTING_MODE, ACCOUNTING_COMMA, CASUAL_MODE, THEME
                global QUICKEN_MODE, LANGUAGE, AUTO_STOP, ALWAYS_ON_TOP, AUTOHIDE_ENABLED, COMPACT_MODE, ACCENT_COLOR
                global SAVE_AUDIO, CUSTOM_VOCABULARY, FILTER_WORDS
                
                # Preserve API key
                saved_key = API_KEY
                
                # Reset to defaults
                HOTKEY = "shift"
                ACCOUNTING_MODE = False
                ACCOUNTING_COMMA = False
                CASUAL_MODE = False
                THEME = "dark"
                QUICKEN_MODE = False
                LANGUAGE = "auto"
                AUTO_STOP = False
                ALWAYS_ON_TOP = True
                AUTOHIDE_ENABLED = True
                COMPACT_MODE = False
                ACCENT_COLOR = "#6366f1"
                SAVE_AUDIO = False
                CUSTOM_VOCABULARY = []
                FILTER_WORDS = DEFAULT_FILTER_WORDS
                
                # Update config but keep API key
                config_data["api_key"] = saved_key
                config_data["hotkey"] = HOTKEY
                config_data["accounting_mode"] = ACCOUNTING_MODE
                config_data["accounting_comma"] = ACCOUNTING_COMMA
                config_data["casual_mode"] = CASUAL_MODE
                config_data["theme"] = THEME
                config_data["quicken_mode"] = QUICKEN_MODE
                config_data["language"] = LANGUAGE
                config_data["auto_stop"] = AUTO_STOP
                config_data["always_on_top"] = ALWAYS_ON_TOP
                config_data["autohide"] = AUTOHIDE_ENABLED
                config_data["compact_mode"] = COMPACT_MODE
                config_data["accent_color"] = ACCENT_COLOR
                config_data["save_audio"] = SAVE_AUDIO
                config_data["custom_vocabulary"] = CUSTOM_VOCABULARY
                config_data["filter_words"] = FILTER_WORDS
                
                CONFIG_FILE.write_text(json.dumps(config_data))
                
                messagebox.showinfo("Reset Complete", "Settings reset to defaults.\nPlease reopen settings to see changes.")
                close_settings()

        def get_key():
            import webbrowser
            webbrowser.open("https://console.groq.com/keys")

        def close_settings():
            global settings_open
            settings_open = False
            win.destroy()

        btn_style = {
            "font": ("Segoe UI", 10, "bold"),
            "relief": "flat",
            "cursor": "hand2",
            "width": 12,
            "height": 1
        }
        
        save_btn = tk.Button(btn_frame, text="Save", bg=self.border_color, fg="white",
                            command=save, **btn_style)
        save_btn.pack(side=tk.LEFT, padx=5)
        
        tk.Button(btn_frame, text="Reset Defaults", bg="#ef4444", fg="white",
                 command=reset_defaults, **btn_style).pack(side=tk.LEFT, padx=5)
        
        tk.Button(btn_frame, text="Get API Key", bg=self.accent_secondary, fg="white",
                 command=get_key, **btn_style).pack(side=tk.LEFT, padx=5)
        
        tk.Button(btn_frame, text="Close", bg=self.bg_light, fg=self.text_primary,
                 command=close_settings, **btn_style).pack(side=tk.LEFT, padx=5)

        def on_close():
            global settings_open
            settings_open = False
            win.destroy()

        win.protocol("WM_DELETE_WINDOW", on_close)

    def open_history(self):
        """Open history browser window with search."""
        global HISTORY
        if not HISTORY:
            return
        
        win = tk.Toplevel(self.root)
        win.title(f"VoiceType v{__version__} - History")
        win.geometry("500x400")
        win.configure(bg=self.bg_dark)
        
        # Search frame
        search_frame = tk.Frame(win, bg=self.bg_dark)
        search_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(search_frame, text="🔍", bg=self.bg_dark, fg=self.text_primary,
                font=("Segoe UI", 12)).pack(side=tk.LEFT)
        
        search_var = tk.StringVar()
        search_entry = tk.Entry(search_frame, textvariable=search_var, 
                               bg=self.bg_light, fg=self.text_primary,
                               insertbackground=self.text_primary,
                               font=("Segoe UI", 11), width=40)
        search_entry.pack(side=tk.LEFT, padx=5)
        
        # Results listbox
        results_frame = tk.Frame(win, bg=self.bg_dark)
        results_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        scrollbar = tk.Scrollbar(results_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        listbox = tk.Listbox(results_frame, bg=self.bg_light, fg=self.text_primary,
                            font=("Segoe UI", 10), selectmode=tk.SINGLE,
                            yscrollcommand=scrollbar.set)
        listbox.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=listbox.yview)
        
        # Copy button
        def copy_selected():
            selection = listbox.curselection()
            if selection:
                idx = selection[0]
                entry = filtered_history[idx]
                pyperclip.copy(entry.get("text", ""))
        
        btn_frame = tk.Frame(win, bg=self.bg_dark)
        btn_frame.pack(fill=tk.X, padx=10, pady=10)
        
        copy_btn = tk.Button(btn_frame, text="📋 Copy Selected", command=copy_selected,
                            bg=self.border_color, fg=self.text_primary,
                            font=("Segoe UI", 10))
        copy_btn.pack(side=tk.LEFT)
        
        # Filter history based on search
        filtered_history = HISTORY.copy()
        
        def update_results(*args):
            nonlocal filtered_history
            query = search_var.get().lower()
            listbox.delete(0, tk.END)
            filtered_history = []
            
            for entry in HISTORY:
                text = entry.get("text", "").lower()
                if not query or query in text:
                    filtered_history.append(entry)
                    timestamp = entry.get("timestamp", "")
                    preview = entry.get("text", "")[:50]
                    listbox.insert(tk.END, f"[{timestamp}] {preview}...")
        
        search_var.trace("w", update_results)
        update_results()
        
        win.transient(self.root)
        win.grab_set()

    def quit_app(self):
        state.running = False
        keyboard.unhook_all()
        if tray_icon:
            tray_icon.stop()
        self.root.quit()
        os._exit(0)

    def update_status(self, status_key, text=""):
        color, status_text = self.colors.get(status_key, self.colors["ready"])
        display = f"{status_text} {text}" if text else status_text
        self.status_label.configure(text=display, fg=color)
        if text and status_key == "done":
            self.text_label.configure(text=text, fg="#f8f8f2")
        elif status_key == "recording":
            self.text_label.configure(text="Speak now...", fg="#f8f8f2")
            # Start timer
            if SHOW_TIMER:
                self.start_timer()
        elif status_key == "processing":
            self.text_label.configure(text="Transcribing...", fg="#f8f8f2")
            self.stop_timer()

    def start_timer(self):
        """Start recording timer display."""
        self.recording_start = time.time()
        self.timer_running = True
        self.update_timer()

    def stop_timer(self):
        """Stop recording timer."""
        self.timer_running = False

    def update_timer(self):
        """Update timer display every 100ms."""
        if not self.timer_running:
            return
        elapsed = time.time() - self.recording_start
        mins = int(elapsed // 60)
        secs = int(elapsed % 60)
        if mins > 0:
            timer_text = f"⏱ {mins}:{secs:02d}"
        else:
            timer_text = f"⏱ {secs}s"
        # Update timer label if it exists
        if hasattr(self, 'timer_label'):
            self.timer_label.configure(text=timer_text)
        self.root.after(100, self.update_timer)

    def run(self):
        self.root.mainloop()


widget = None


def update_status(status_key, text=""):
    if widget:
        widget.root.after(0, lambda: widget.update_status(status_key, text))


def create_tray_icon():
    """Create system tray icon."""
    # Create a simple microphone icon
    width = 64
    height = 64
    image = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    dc = ImageDraw.Draw(image)

    # Draw microphone shape
    dc.ellipse([20, 8, 44, 36], fill="#50fa7b", outline="#50fa7b")
    dc.rectangle([28, 36, 36, 48], fill="#50fa7b")
    dc.arc([12, 32, 52, 56], 0, 180, fill="#50fa7b", width=3)
    dc.line([32, 52, 32, 60], fill="#50fa7b", width=3)
    dc.line([22, 60, 42, 60], fill="#50fa7b", width=3)

    def on_settings(icon, item):
        widget.root.after(0, widget.open_settings)
    
    def on_copy_last(icon, item):
        """Copy last transcription to clipboard."""
        global last_transcription
        if last_transcription:
            pyperclip.copy(last_transcription)
            print(f"[clipboard] Copied: {last_transcription[:50]}...")
    
    def on_show(icon, item):
        widget.root.after(0, widget.show_widget)
    
    def on_history(icon, item):
        widget.root.after(0, widget.open_history)

    def on_export(icon, item):
        export_history()

    def on_transcribe_file(icon, item):
        transcribe_audio_file()

    def on_quit(icon, item):
        widget.root.after(0, widget.quit_app)

    menu = pystray.Menu(
        pystray.MenuItem("Settings", on_settings),
        pystray.MenuItem("History", on_history),
        pystray.MenuItem("Export History", on_export),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("📁 Transcribe Audio File...", on_transcribe_file),
        pystray.MenuItem("Copy Last", on_copy_last, default=False),
        pystray.MenuItem("Show Widget", on_show),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("Quit", on_quit),
    )

    return pystray.Icon("voice_type", image, f"VoiceType v{__version__} (Hold {HOTKEY.upper()})", menu)


def transcribe_audio_file():
    """Transcribe an existing audio file from disk."""
    global last_transcription
    
    if not API_KEY:
        print("[error] No API key set")
        return
    
    from tkinter import filedialog
    
    file_path = filedialog.askopenfilename(
        title="Select Audio File",
        filetypes=[
            ("Audio Files", "*.wav *.mp3 *.m4a *.ogg *.flac *.webm"),
            ("WAV Files", "*.wav"),
            ("MP3 Files", "*.mp3"),
            ("All Files", "*.*")
        ]
    )
    
    if not file_path:
        return
    
    print(f"[file] Transcribing: {file_path}")
    update_status("processing", "Transcribing file...")
    widget.show_widget()
    
    def do_transcribe():
        global last_transcription
        text, error = transcribe_with_groq(file_path)
        
        if text:
            text = text.strip()
            last_transcription = text
            
            # Apply text processing
            if CAPITALIZE_SENTENCES:
                text = text[0].upper() + text[1:] if text else text
                text = re.sub(r'([.!?]\s+)([a-z])', lambda m: m.group(1) + m.group(2).upper(), text)
            
            word_count = len(text.split())
            char_count = len(text)
            update_status("done", f"{text}\n\n📝 {word_count} words | {char_count} chars")
            
            # Copy to clipboard
            pyperclip.copy(text)
            print(f"[file] Transcribed: {text[:50]}...")
            
            # Save to history
            save_to_history(text)
            
            # Type the text
            type_text(text)
        else:
            update_status("error", error or "Failed to transcribe")
        
        # Auto-hide after delay
        def hide_after():
            time.sleep(3)
            if widget and AUTOHIDE_ENABLED:
                widget.root.after(0, widget.hide_widget)
        threading.Thread(target=hide_after, daemon=True).start()
    
    threading.Thread(target=do_transcribe, daemon=True).start()


def transcribe_with_groq(audio_path):
    """Use Groq Whisper API for transcription."""
    global API_KEY, CUSTOM_VOCABULARY

    if not API_KEY:
        return None, "No API key"

    try:
        url = "https://api.groq.com/openai/v1/audio/transcriptions"
        headers = {"Authorization": f"Bearer {API_KEY}"}

        with open(audio_path, "rb") as f:
            files = {"file": ("audio.wav", f, "audio/wav")}
            data = {"model": "whisper-large-v3-turbo", "response_format": "json"}
            
            # Add language parameter if specified (not auto-detect)
            if LANGUAGE and LANGUAGE != "auto":
                data["language"] = LANGUAGE
            
            # Add custom vocabulary as prompt to improve transcription accuracy
            if CUSTOM_VOCABULARY:
                vocab_prompt = "Context: " + ", ".join(CUSTOM_VOCABULARY[:50])  # Limit to avoid token limits
                data["prompt"] = vocab_prompt

            with httpx.Client(timeout=30) as client:
                response = client.post(url, headers=headers, files=files, data=data)

        if response.status_code == 200:
            result = response.json()
            return result.get("text"), None
        else:
            return None, f"HTTP {response.status_code}"

    except Exception as e:
        return None, str(e)


# Emoji mapping for voice commands
EMOJI_MAP = {
    # Common emotions
    "happy emoji": "😊", "smile emoji": "😊", "smiling emoji": "😊",
    "sad emoji": "😢", "crying emoji": "😭", "tears emoji": "😭",
    "angry emoji": "😠", "mad emoji": "😠", "frustrated emoji": "😤",
    "laughing emoji": "😂", "lol emoji": "😂", "haha emoji": "😂",
    "love emoji": "❤️", "heart emoji": "❤️", "hearts emoji": "💕",
    "cool emoji": "😎", "sunglasses emoji": "😎",
    "wink emoji": "😉", "winking emoji": "😉",
    "surprised emoji": "😲", "shocked emoji": "😱",
    "thinking emoji": "🤔", "hmm emoji": "🤔",
    "sleepy emoji": "😴", "tired emoji": "😴",
    "sick emoji": "🤒", "ill emoji": "🤒",
    "nerd emoji": "🤓", "geek emoji": "🤓",
    
    # Reactions
    "thumbs up emoji": "👍", "thumbs down emoji": "👎",
    "ok emoji": "👌", "okay emoji": "👌",
    "clap emoji": "👏", "applause emoji": "👏",
    "fire emoji": "🔥", "hot emoji": "🔥", "lit emoji": "🔥",
    "star emoji": "⭐", "stars emoji": "✨",
    "party emoji": "🎉", "celebration emoji": "🎉", "confetti emoji": "🎊",
    "boom emoji": "💥", "explosion emoji": "💥",
    "check emoji": "✅", "checkmark emoji": "✅", "done emoji": "✅",
    "x emoji": "❌", "cross emoji": "❌", "no emoji": "❌",
    "question emoji": "❓", "confused emoji": "❓",
    "exclamation emoji": "❗", "warning emoji": "⚠️",
    "idea emoji": "💡", "lightbulb emoji": "💡", "bulb emoji": "💡",
    
    # Hands/Gestures
    "wave emoji": "👋", "hello emoji": "👋", "hi emoji": "👋",
    "peace emoji": "✌️", "victory emoji": "✌️",
    "fist emoji": "👊", "punch emoji": "👊",
    "fingers crossed emoji": "🤞", "good luck emoji": "🤞",
    "pray emoji": "🙏", "please emoji": "🙏", "thanks emoji": "🙏",
    "high five emoji": "🙌", "raise hands emoji": "🙌",
    "shrug emoji": "🤷", "idk emoji": "🤷",
    "facepalm emoji": "🤦",
    
    # Animals
    "dog emoji": "🐕", "puppy emoji": "🐶",
    "cat emoji": "🐱", "kitty emoji": "🐱",
    "monkey emoji": "🐵", "see no evil emoji": "🙈",
    "fox emoji": "🦊",
    "bear emoji": "🐻",
    "panda emoji": "🐼",
    "unicorn emoji": "🦄",
    "butterfly emoji": "🦋",
    "snake emoji": "🐍",
    
    # Food & Drinks
    "pizza emoji": "🍕",
    "burger emoji": "🍔", "hamburger emoji": "🍔",
    "coffee emoji": "☕", "latte emoji": "☕",
    "beer emoji": "🍺",
    "wine emoji": "🍷",
    "cake emoji": "🎂", "birthday emoji": "🎂",
    "ice cream emoji": "🍦",
    
    # Weather & Nature
    "sun emoji": "☀️", "sunny emoji": "☀️",
    "moon emoji": "🌙", "crescent moon emoji": "🌙",
    "cloud emoji": "☁️", "cloudy emoji": "☁️",
    "rain emoji": "🌧️", "rainy emoji": "🌧️",
    "snow emoji": "❄️", "snowflake emoji": "❄️",
    "rainbow emoji": "🌈",
    "flower emoji": "🌸", "blossom emoji": "🌸",
    "tree emoji": "🌳",
    
    # Objects & Symbols
    "rocket emoji": "🚀", "launch emoji": "🚀",
    "computer emoji": "💻", "laptop emoji": "💻",
    "phone emoji": "📱", "mobile emoji": "📱",
    "email emoji": "📧", "mail emoji": "📧",
    "book emoji": "📖",
    "pencil emoji": "✏️", "write emoji": "✏️",
    "lock emoji": "🔒", "secure emoji": "🔒",
    "key emoji": "🔑", "password emoji": "🔑",
    "clock emoji": "⏰", "alarm emoji": "⏰",
    "calendar emoji": "📅", "date emoji": "📅",
    "money emoji": "💰", "cash emoji": "💰", "dollar emoji": "💵",
    "gift emoji": "🎁", "present emoji": "🎁",
    "camera emoji": "📷", "photo emoji": "📷",
    
    # People & Activities
    "runner emoji": "🏃", "running emoji": "🏃",
    "dancer emoji": "💃", "dancing emoji": "💃",
    "coder emoji": "👨‍💻", "developer emoji": "👨‍💻", "programmer emoji": "👨‍💻",
    "artist emoji": "🎨", "paint emoji": "🎨",
    "gamer emoji": "🎮", "gaming emoji": "🎮", "video game emoji": "🎮",
    "music emoji": "🎵", "song emoji": "🎵", "note emoji": "🎵",
    "microphone emoji": "🎤", "mic emoji": "🎤",
    "movie emoji": "🎬", "film emoji": "🎬", "cinema emoji": "🎬",
    "workout emoji": "💪", "muscle emoji": "💪", "strong emoji": "💪",
    
    # Flags & Places
    "usa emoji": "🇺🇸", "america emoji": "🇺🇸", "us flag emoji": "🇺🇸",
    "uk emoji": "🇬🇧", "britain emoji": "🇬🇧", "england emoji": "🏴󠁧󠁢󠁥󠁮󠁧󠁿",
    "world emoji": "🌍", "globe emoji": "🌍", "earth emoji": "🌍",
    
    # Common phrases
    "100 emoji": "💯",
    "rock emoji": "🪨",
    "rock and roll emoji": "🤘", "metal emoji": "🤘",
    "skull emoji": "💀", "dead emoji": "💀",
    "ghost emoji": "👻",
    "alien emoji": "👽",
    "robot emoji": "🤖", "bot emoji": "🤖",
    "poop emoji": "💩", "shit emoji": "💩",
    "egg emoji": "🥚", "easter emoji": "🥚",
    "eye emoji": "👁️", "eyes emoji": "👀",
    "ear emoji": "👂",
    "nose emoji": "👃",
}


def convert_emojis(text):
    """Convert emoji phrases to actual emojis."""
    result = text
    
    # Sort by length (longest first) to avoid partial matches
    sorted_emojis = sorted(EMOJI_MAP.items(), key=lambda x: len(x[0]), reverse=True)
    
    for phrase, emoji in sorted_emojis:
        # Case-insensitive replacement
        pattern = re.compile(re.escape(phrase), re.IGNORECASE)
        result = pattern.sub(emoji, result)
    
    # Clean up any double spaces left after replacements
    result = re.sub(r'\s+', ' ', result).strip()
    
    return result


# Number word to digit mapping for accounting mode
# Only use unambiguous number words to avoid false positives
NUMBER_WORD_MAP = {
    # Basic numbers 0-9
    "zero": "0",
    "one": "1",
    "two": "2",
    "three": "3",
    "four": "4",
    "five": "5",
    "six": "6",
    "seven": "7",
    "eight": "8",
    "nine": "9",
    
    # Teens
    "ten": "10",
    "eleven": "11",
    "twelve": "12",
    "thirteen": "13",
    "fourteen": "14",
    "fifteen": "15",
    "sixteen": "16",
    "seventeen": "17",
    "eighteen": "18",
    "nineteen": "19",
    
    # Tens
    "twenty": "20",
    "thirty": "30",
    "forty": "40",
    "fourty": "40",
    "fifty": "50",
    "sixty": "60",
    "seventy": "70",
    "eighty": "80",
    "ninety": "90",
}


def convert_numbers_to_digits(text):
    """Convert number words to digits for accounting mode."""
    result = text
    
    # Sort by length (longest first) to avoid partial matches
    sorted_numbers = sorted(NUMBER_WORD_MAP.items(), key=lambda x: len(x[0]), reverse=True)
    
    for word, digit in sorted_numbers:
        # Match word boundaries including punctuation
        # This handles "one, two, three" properly
        pattern = re.compile(
            r'(?<![a-zA-Z])' + re.escape(word) + r'(?![a-zA-Z])',
            re.IGNORECASE
        )
        result = pattern.sub(digit, result)
    
    return result


# Common Whisper hallucinations when no speech is detected
HALLUCINATION_PHRASES = [
    "thank you",
    "thanks", 
    "thank you.",
    "thanks.",
    "thank you for watching",
    "thanks for watching",
    "you",
    "you.",
    "bye",
    "bye.",
    "goodbye",
    "goodbye.",
    "subtitle",
    "subtitles",
    "caption",
    "captions",
]


def filter_text(text):
    """Filter out unwanted words from transcription."""
    global FILTER_WORDS
    
    if not text:
        return ""
    
    result = text.strip()
    
    # If empty after stripping, return empty
    if not result:
        return ""
    
    # Only use user's custom filter words - NOT hardcoded hallucinations
    # User has full control over what to filter
    if not FILTER_WORDS:
        return result
    
    # Check if the entire text matches a filter word (case-insensitive)
    result_lower = result.lower()
    for filter_word in FILTER_WORDS:
        filter_word_lower = filter_word.lower().strip()
        if result_lower == filter_word_lower:
            print(f"[filtered] Matched filter: '{filter_word}'")
            return ""
    
    # Also check if text contains filter word as substring (for short texts)
    if len(result) < 30:
        for filter_word in FILTER_WORDS:
            filter_word_lower = filter_word.lower().strip()
            if filter_word_lower in result_lower:
                print(f"[filtered] Contains filter: '{filter_word}'")
                return ""
    
    return result


def normalize_numbers_from_api(text):
    """Remove commas from numbers in API response unless comma mode is enabled."""
    global ACCOUNTING_COMMA
    
    print(f"[NORMALIZE] ACCOUNTING_COMMA = {ACCOUNTING_COMMA}")
    
    if ACCOUNTING_COMMA:
        # Comma mode is ON - keep commas as they are from API
        print(f"[NORMALIZE] Keeping commas (comma mode ON)")
        return text
    
    # Comma mode is OFF - remove commas from numbers
    # This handles cases where Groq API returns "1,234,567"
    def remove_commas(match):
        return match.group(0).replace(',', '')
    
    result = re.sub(r'\b[\d,]+\b', remove_commas, text)
    print(f"[NORMALIZE] Removed commas: '{text}' -> '{result}'")
    return result


def format_number_with_commas(text):
    """Add commas to large numbers in text if accounting comma mode is enabled."""
    global ACCOUNTING_COMMA
    
    print(f"[COMMA_FUNC] ACCOUNTING_COMMA value: {ACCOUNTING_COMMA}")
    
    # Explicit check - must be True to add commas
    if ACCOUNTING_COMMA is not True:
        print(f"[COMMA_FUNC] SKIPPING commas - mode is OFF")
        return text
    
    def add_commas(match):
        num = match.group(0)
        # Add commas every 3 digits from the right
        if len(num) > 3:
            return "{:,}".format(int(num))
        return num
    
    # Find all numbers with 4+ digits and add commas
    print(f"[COMMA_FUNC] ADDING commas")
    return re.sub(r'\b\d{4,}\b', add_commas, text)


def apply_casual_mode(text):
    """Apply casual formatting: lowercase and informal punctuation."""
    global CASUAL_MODE
    
    if not CASUAL_MODE:
        return text
    
    print(f"[CASUAL] Applying casual mode to: '{text}'")
    
    # Convert to lowercase
    result = text.lower()
    
    # Replace formal punctuation with casual equivalents
    # Remove periods at end of sentences (casual texting style)
    result = re.sub(r'\.$', '', result)
    result = re.sub(r'\.(\s)', r'\1', result)
    
    # Keep exclamation and question marks as they add emotion
    # But remove multiple punctuation like "!!!" or "???" down to one
    result = re.sub(r'[!]{2,}', '!', result)
    result = re.sub(r'[?]{2,}', '?', result)
    
    # Remove formal commas that aren't needed for clarity
    # Keep commas in numbers though
    result = re.sub(r',\s+', ' ', result)
    
    print(f"[CASUAL] Result: '{result}'")
    return result


# Voice commands - speak these to control text
VOICE_COMMANDS = {
    # Editing commands
    "delete last word": "__DELETE_WORD__",
    "delete last sentence": "__DELETE_SENTENCE__",
    "delete all": "__DELETE_ALL__",
    "undo that": "__DELETE_WORD__",
    "scratch that": "__DELETE_WORD__",
    
    # Formatting commands
    "new paragraph": "\n\n",
    "new line": "\n",
    "tab": "\t",
    "indent": "\t",
    
    # Punctuation (explicit)
    "period": ".",
    "full stop": ".",
    "comma": ",",
    "question mark": "?",
    "exclamation mark": "!",
    "exclamation point": "!",
    "colon": ":",
    "semicolon": ";",
    "dash": " - ",
    "hyphen": "-",
    "quote": '"',
    "open quote": '"',
    "close quote": '"',
    "apostrophe": "'",
    
    # Special characters
    "at sign": "@",
    "at symbol": "@",
    "hash": "#",
    "hashtag": "#",
    "percent": "%",
    "percent sign": "%",
    "ampersand": "&",
    "asterisk": "*",
    "plus sign": "+",
    "minus sign": "-",
    "equals": "=",
    "slash": "/",
    "backslash": "\\",
    
    # Common replacements
    "dot com": ".com",
    "dot net": ".net",
    "dot org": ".org",
    "dot io": ".io",
}


def process_voice_commands(text):
    """Process voice commands and return modified text or special actions."""
    global VOICE_COMMANDS
    
    text_lower = text.lower().strip()
    
    # Check for exact command matches
    if text_lower in VOICE_COMMANDS:
        command_value = VOICE_COMMANDS[text_lower]
        
        # Handle special delete commands
        if command_value == "__DELETE_WORD__":
            print("[command] Delete last word")
            keyboard.press_and_release("ctrl+backspace")
            return None
        elif command_value == "__DELETE_SENTENCE__":
            print("[command] Delete last sentence")
            keyboard.press_and_release("ctrl+shift+left")
            keyboard.press_and_release("backspace")
            return None
        elif command_value == "__DELETE_ALL__":
            print("[command] Delete all")
            keyboard.press_and_release("ctrl+a")
            keyboard.press_and_release("backspace")
            return None
        
        # Return the replacement text
        print(f"[command] '{text}' → '{command_value}'")
        return command_value
    
    # Check for inline commands (commands within longer text)
    result = text
    for command, replacement in VOICE_COMMANDS.items():
        if replacement.startswith("__"):
            continue  # Skip special commands for inline use
        pattern = re.compile(re.escape(command), re.IGNORECASE)
        if pattern.search(result):
            result = pattern.sub(replacement, result)
            print(f"[command] Inline: '{command}' → '{replacement}'")
    
    return result


def type_text(text):
    """Type text using clipboard."""
    global ACCOUNTING_MODE, ACCOUNTING_COMMA, CASUAL_MODE
    
    # Very explicit debug
    print("=" * 60)
    print(f"[TYPE_TEXT] ACCOUNTING_MODE = {ACCOUNTING_MODE}")
    print(f"[TYPE_TEXT] ACCOUNTING_COMMA = {ACCOUNTING_COMMA}")
    print(f"[TYPE_TEXT] Original text: '{text}'")
    
    # First, normalize numbers from API (remove commas unless comma mode is ON)
    text = normalize_numbers_from_api(text)
    
    # Then convert number words to digits if accounting mode is enabled
    # Do this BEFORE filtering so "one" -> "1" works
    if ACCOUNTING_MODE:
        original = text
        text = convert_numbers_to_digits(text)
        print(f"[TYPE_TEXT] CONVERTED: '{original}' -> '{text}'")
        
        # Add commas to large numbers if enabled
        if ACCOUNTING_COMMA:
            text_before_comma = text
            text = format_number_with_commas(text)
            if text != text_before_comma:
                print(f"[TYPE_TEXT] COMMAS: '{text_before_comma}' -> '{text}'")
    else:
        print(f"[TYPE_TEXT] SKIPPING conversion - mode is OFF")
    print("=" * 60)
    
    # Apply filter after conversion
    text = filter_text(text)
    
    # If text was filtered out, don't type anything
    if not text:
        print("[filtered] Text was filtered out, nothing to type")
        return
    
    # Apply voice macros (expand text shortcuts)
    text = apply_macros(text)
    
    # Process voice commands (delete, new paragraph, etc.)
    command_result = process_voice_commands(text)
    if command_result is None:
        # It was an action command (delete), already executed
        print("[command] Action command executed")
        return
    text = command_result
    
    # Convert emoji phrases to actual emojis
    text = convert_emojis(text)
    
    # Apply casual mode (lowercase, informal punctuation)
    text = apply_casual_mode(text)
    
    # Update statistics
    update_stats(text)
    
    print(f"[typing] {text}")
    
    # Check if Quicken mode is enabled
    if QUICKEN_MODE:
        # Type character-by-character for Quicken compatibility
        print("[quicken] Using character-by-character typing")
        for char in text:
            keyboard.write(char)
            time.sleep(0.01)  # Small delay between characters for compatibility
        # Add space at end
        keyboard.write(" ")
    else:
        # Normal clipboard paste mode (faster)
        pyperclip.copy(text)
        time.sleep(0.05)
        keyboard.press_and_release("ctrl+v")


def apply_macros(text):
    """Apply voice macros to expand shortcuts."""
    global MACROS
    
    if not MACROS:
        return text
    
    result = text
    today = time.strftime("%Y-%m-%d")
    now = time.strftime("%H:%M:%S")
    datetime = time.strftime("%Y-%m-%d %H:%M:%S")
    
    # Sort by length (longest first) to avoid partial matches
    sorted_macros = sorted(MACROS.items(), key=lambda x: len(x[0]), reverse=True)
    
    for phrase, expansion in sorted_macros:
        # Case-insensitive replacement
        pattern = re.compile(re.escape(phrase), re.IGNORECASE)
        
        # Replace dynamic placeholders
        expansion = expansion.replace("{{DATE}}", today)
        expansion = expansion.replace("{{TIME}}", now)
        expansion = expansion.replace("{{DATETIME}}", datetime)
        
        result = pattern.sub(expansion, result)
    
    # Clean up any double spaces
    result = re.sub(r'\s+', ' ', result).strip()
    
    return result


def save_to_history(text):
    """Save transcription to history."""
    global HISTORY
    if not HISTORY_ENABLED or not text:
        return
    
    entry = {
        "text": text,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "words": len(text.split())
    }
    HISTORY.insert(0, entry)
    HISTORY = HISTORY[:100]  # Keep last 100
    
    try:
        HISTORY_FILE.write_text(json.dumps(HISTORY, indent=2))
    except:
        pass


def export_history():
    """Export history to a text file on desktop."""
    global HISTORY
    if not HISTORY:
        print("[export] No history to export")
        return
    
    from datetime import datetime
    desktop = Path.home() / "Desktop"
    if not desktop.exists():
        desktop = Path.home()
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    export_file = desktop / f"voice_type_history_{timestamp}.txt"
    
    try:
        with open(export_file, "w", encoding="utf-8") as f:
            f.write("VoiceType Transcription History\n")
            f.write(f"Exported: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total entries: {len(HISTORY)}\n")
            f.write("=" * 50 + "\n\n")
            
            for i, entry in enumerate(HISTORY, 1):
                f.write(f"[{entry.get('timestamp', 'Unknown')}] ({entry.get('words', 0)} words)\n")
                f.write(f"{entry.get('text', '')}\n\n")
        
        print(f"[export] Exported {len(HISTORY)} entries to {export_file}")
    except Exception as e:
        print(f"[export] Error: {e}")


def update_stats(text):
    """Update usage statistics."""
    global STATS
    
    word_count = len(text.split())
    STATS["total_words"] += word_count
    STATS["total_transcriptions"] += 1
    STATS["last_used"] = time.strftime("%Y-%m-%d %H:%M:%S")
    
    if STATS["first_used"] is None:
        STATS["first_used"] = STATS["last_used"]
    
    # Save stats to file
    try:
        STATS_FILE.write_text(json.dumps(STATS, indent=2))
    except:
        pass
    
    # Save to history
    save_to_history(text)


def record_and_transcribe():
    """Record audio while Shift is held, then transcribe with Groq Whisper."""
    # Show widget when recording starts
    if widget and widget.hidden:
        widget.root.after(0, widget.show_widget)
    update_status("recording", "Speak now...")
    print("Recording...")

    try:
        mic_idx = MIC_INDEX if MIC_INDEX is not None else 0

        p = pyaudio.PyAudio()

        chunk = 1024
        format = pyaudio.paInt16
        channels = 1
        rate = SAMPLE_RATE

        stream = p.open(
            format=format,
            channels=channels,
            rate=rate,
            input=True,
            input_device_index=mic_idx,
            frames_per_buffer=chunk,
        )

        frames = []
        start_time = time.time()
        last_sound_time = time.time()  # Track when we last heard sound
        silence_start = None

        while keyboard.is_pressed(HOTKEY):
            data = stream.read(chunk, exception_on_overflow=False)
            frames.append(data)
            
            # Calculate audio level for visual feedback
            import struct
            samples = struct.unpack(f'<{len(data)//2}h', data)
            max_sample = max(abs(s) for s in samples) if samples else 0
            level = min(max_sample / 32768.0, 1.0)  # Normalize to 0-1
            
            # Update widget level indicator
            if widget:
                widget.root.after(0, lambda l=level: widget.update_level(l))
            
            # Silence detection for auto-stop
            if AUTO_STOP:
                # Consider it sound if level is above 2% (background noise threshold)
                if level > 0.02:
                    last_sound_time = time.time()
                    silence_start = None
                else:
                    # Track silence start
                    if silence_start is None:
                        silence_start = time.time()
                    else:
                        silence_duration = time.time() - silence_start
                        # Auto-stop after threshold seconds of silence
                        if silence_duration >= SILENCE_THRESHOLD:
                            print(f"[auto-stop] {SILENCE_THRESHOLD}s silence detected")
                            break

        duration = time.time() - start_time
        print(f"Recorded {duration:.1f}s")

        stream.stop_stream()
        stream.close()
        p.terminate()

        if len(frames) < 15:
            update_status("error", "Too short")
            time.sleep(1)
            widget.root.after(0, widget.hide_widget)
            state.recording = False
            return

        if not API_KEY:
            update_status("nokey", "Open Settings")
            time.sleep(2)
            widget.root.after(0, widget.hide_widget)
            state.recording = False
            return

        update_status("processing", "")

        # Save to temp wav
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            temp_path = f.name

        wf = wave.open(temp_path, "wb")
        wf.setnchannels(channels)
        wf.setsampwidth(p.get_sample_size(format))
        wf.setframerate(rate)
        wf.writeframes(b"".join(frames))
        wf.close()

        # Transcribe
        text, error = transcribe_with_groq(temp_path)
        
        # Save audio if enabled
        if SAVE_AUDIO and text:
            audio_dir = Path.home() / "VoiceType Recordings"
            audio_dir.mkdir(exist_ok=True)
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            audio_file = audio_dir / f"recording_{timestamp}.wav"
            import shutil
            shutil.copy(temp_path, audio_file)
            print(f"[audio] Saved to {audio_file}")
        
        Path(temp_path).unlink(missing_ok=True)

        if text:
            text = text.strip()
            
            # Capitalize first letter of sentences if enabled
            if CAPITALIZE_SENTENCES:
                text = text[0].upper() + text[1:] if text else text
                # Capitalize after sentence endings
                import re
                text = re.sub(r'([.!?]\s+)([a-z])', lambda m: m.group(1) + m.group(2).upper(), text)

            # Apply smart quotes if enabled
            if SMART_QUOTES:
                # Replace straight quotes with curly quotes
                result = []
                in_quote = False
                for char in text:
                    if char == '"':
                        if in_quote:
                            result.append('"')  # Closing quote
                        else:
                            result.append('"')  # Opening quote
                        in_quote = not in_quote
                    else:
                        result.append(char)
                text = ''.join(result)
            
            # Apply word replacements if configured
            if WORD_REPLACEMENTS:
                for old_word, new_word in WORD_REPLACEMENTS.items():
                    text = text.replace(old_word, new_word)
            
            print(f"[whisper] {text}")
            
            # Store last transcription for copy feature
            last_transcription = text
            
            # Auto-copy to clipboard if enabled
            if AUTO_COPY:
                pyperclip.copy(text)
            
            # Show word/character count
            word_count = len(text.split())
            char_count = len(text)
            update_status("done", f"{text}\n\n📝 {word_count} words | {char_count} chars")
            type_text(text)

            def hide_after_done():
                time.sleep(2)
                if widget and AUTOHIDE_ENABLED:
                    widget.root.after(0, widget.hide_widget)

            threading.Thread(target=hide_after_done, daemon=True).start()
        else:
            update_status("error", error or "Failed")

            def hide_after_error():
                time.sleep(2)
                if widget:
                    widget.root.after(0, widget.hide_widget)

            threading.Thread(target=hide_after_error, daemon=True).start()

    except Exception as e:
        update_status("error", str(e)[:30])
        print(f"Error: {e}")
        time.sleep(1.5)
        widget.root.after(0, widget.hide_widget)
    finally:
        state.recording = False


# Keyboard shortcuts overlay
SHORTCUTS_OVERLAY_VISIBLE = False

def show_shortcuts_overlay():
    """Show a popup with all keyboard shortcuts."""
    global SHORTCUTS_OVERLAY_VISIBLE
    
    if SHORTCUTS_OVERLAY_VISIBLE:
        return
    
    SHORTCUTS_OVERLAY_VISIBLE = True
    
    overlay = tk.Tk()
    overlay.title("VoiceType - Keyboard Shortcuts")
    overlay.configure(bg="#1a1a2e")
    overlay.resizable(False, False)
    overlay.attributes("-topmost", True)
    
    # Center on screen
    overlay.update_idletasks()
    width = 400
    height = 450
    x = (overlay.winfo_screenwidth() // 2) - (width // 2)
    y = (overlay.winfo_screenheight() // 2) - (height // 2)
    overlay.geometry(f"{width}x{height}+{x}+{y}")
    
    # Title
    tk.Label(overlay, text="⌨️ Keyboard Shortcuts", font=("Segoe UI", 16, "bold"),
            bg="#1a1a2e", fg="#4a9eff").pack(pady=20)
    
    shortcuts = [
        ("Recording", f"Hold {HOTKEY.upper()}", "Push-to-talk"),
        ("", "", ""),
        ("Voice Commands", "", ""),
        ("Delete last word", "\"delete last word\"", "or \"undo that\""),
        ("Delete sentence", "\"delete last sentence\"", ""),
        ("New paragraph", "\"new paragraph\"", "or \"new line\""),
        ("Punctuation", "\"period\", \"comma\"", "\"question mark\""),
        ("", "", ""),
        ("In-App", "", ""),
        ("Show shortcuts", "F1", "This overlay"),
        ("Settings", "Right-click tray", "Open settings"),
        ("Quit", "Right-click tray → Quit", ""),
        ("", "", ""),
        ("Press ESC or click to close", "", ""),
    ]
    
    frame = tk.Frame(overlay, bg="#1a1a2e")
    frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
    
    for action, shortcut, note in shortcuts:
        row = tk.Frame(frame, bg="#1a1a2e")
        row.pack(fill=tk.X, pady=2)
        
        if action and not action.startswith("Press"):
            tk.Label(row, text=action, font=("Segoe UI", 10, "bold"),
                    bg="#1a1a2e", fg="#ffffff", width=20, anchor="w").pack(side=tk.LEFT)
            tk.Label(row, text=shortcut, font=("Segoe UI", 10),
                    bg="#1a1a2e", fg="#00ff88", width=25, anchor="w").pack(side=tk.LEFT)
            tk.Label(row, text=note, font=("Segoe UI", 9),
                    bg="#1a1a2e", fg="#a0a0a0", anchor="w").pack(side=tk.LEFT)
        elif action.startswith("Press"):
            tk.Label(row, text=action, font=("Segoe UI", 10, "italic"),
                    bg="#1a1a2e", fg="#a0a0a0").pack(side=tk.LEFT)
        else:
            # Section header
            tk.Label(row, text=shortcut, font=("Segoe UI", 11, "bold"),
                    bg="#1a1a2e", fg="#533483").pack(side=tk.LEFT)
    
    def close_overlay(e=None):
        global SHORTCUTS_OVERLAY_VISIBLE
        SHORTCUTS_OVERLAY_VISIBLE = False
        overlay.destroy()
    
    overlay.bind("<Escape>", close_overlay)
    overlay.bind("<Button-1>", close_overlay)
    overlay.protocol("WM_DELETE_WINDOW", close_overlay)
    
    overlay.mainloop()


def hotkey_loop():
    """Poll for hotkey state."""
    was_pressed = False
    while state.running:
        is_pressed = keyboard.is_pressed(HOTKEY)
        if is_pressed and not was_pressed and not state.recording:
            was_pressed = True
            state.recording = True
            threading.Thread(target=record_and_transcribe, daemon=True).start()
        elif not is_pressed and was_pressed:
            was_pressed = False
        
        # Check for F1 to show shortcuts overlay
        if keyboard.is_pressed("f1") and not SHORTCUTS_OVERLAY_VISIBLE:
            keyboard.release("f1")
            time.sleep(0.1)
            show_shortcuts_overlay()
        
        time.sleep(0.02)


def main():
    global widget, tray_icon, STATS

    print("=" * 50)
    print(f"Voice Type v{__version__} - Groq Whisper (Hold {HOTKEY.upper()})")
    print("=" * 50)

    # Increment session count
    STATS["total_sessions"] += 1
    try:
        STATS_FILE.write_text(json.dumps(STATS, indent=2))
    except:
        pass

    if not API_KEY:
        print("\n  No API key found!")
        print("Get free key: https://console.groq.com/keys")
    else:
        print(f"API key loaded ({len(API_KEY)} chars)")
    
    if MACROS:
        print(f"Macros loaded: {len(MACROS)}")

    widget = FloatingWidget()

    # Start minimized if configured
    if MINIMIZE_STARTUP:
        widget.hide_widget()
        print("Started minimized to tray")

    # Create and start tray icon
    tray_icon = create_tray_icon()
    threading.Thread(target=tray_icon.run, daemon=True).start()

    threading.Thread(target=hotkey_loop, daemon=True).start()

    print(f"\nReady! Hold {HOTKEY.upper()} to record.")

    # Auto-open settings window on startup
    widget.root.after(500, widget.open_settings)

    try:
        widget.run()
    except KeyboardInterrupt:
        widget.quit_app()


if __name__ == "__main__":
    main()
