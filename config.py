import os
import json
import shutil

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
SETTINGS_FILE = os.path.join(BASE_DIR, "settings.json")

# Default configurations
DEFAULT_CONFIG = {
    # Audio & Listening settings
    "sample_rate": 16000,
    "silence_threshold": 0.015,       # RMS threshold for voice activity
    "silence_duration_seconds": 1.2,  # Stop listening after 1.2s of silence
    "max_listen_seconds": 9.0,        # Maximum continuous listening duration
    "speech_engine": "hybrid",        # "hybrid" (Google STT), "whisper", or "vosk"
    
    # Feedback settings
    "tts_enabled": True,              # Audible voice confirmations
    "tts_volume": 100,                # 0 to 100
    "sound_cues": True,               # Audio beep on listen / done
    
    # Chrome settings
    "chrome_path": "",                # Auto-detected if empty
    "default_profile": "Default",     # Default profile directory name
    "youtube_app_mode": False,         # Launch YouTube as standalone app window
    
    # UI Floating Widget settings
    "widget_size": 70,                # Width & height in pixels
    "always_on_top": False,           # Only exists on desktop, never hovers over other apps
    "window_x": None,                 # Auto-centered or remembered
    "window_y": None,
    "theme": "dark_neon",
}

def find_chrome_executable():
    """Finds Google Chrome executable path on Windows."""
    candidates = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
    ]
    for path in candidates:
        if os.path.exists(path):
            return path
    
    # Check PATH
    which_chrome = shutil.which("chrome.exe")
    if which_chrome:
        return which_chrome
    return ""

def load_settings():
    """Loads settings from JSON or creates defaults."""
    cfg = DEFAULT_CONFIG.copy()
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                user_cfg = json.load(f)
                cfg.update(user_cfg)
        except Exception as e:
            print(f"[Config] Error loading settings: {e}")
            
    if not cfg.get("chrome_path"):
        cfg["chrome_path"] = find_chrome_executable()
        
    return cfg

def save_settings(new_settings):
    """Saves updated settings to settings.json."""
    try:
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(new_settings, f, indent=4)
        return True
    except Exception as e:
        print(f"[Config] Error saving settings: {e}")
        return False
