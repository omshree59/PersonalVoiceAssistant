import os
import sys
import subprocess
import webbrowser
import urllib.parse
import time
import pyautogui
pyautogui.FAILSAFE = False

# Ensure project root is in python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config
from automation.profile_helper import match_profile, get_installed_chrome_profiles

def launch_process(command_list):
    """Safely launches a background detached subprocess on Windows."""
    try:
        subprocess.Popen(
            command_list,
            creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP
        )
        return True
    except Exception as e:
        print(f"[Actions] Subprocess launch failed: {e}")
        try:
            # Fallback to os.startfile or standard Popen
            subprocess.Popen(command_list, shell=True)
            return True
        except Exception as e2:
            print(f"[Actions] Shell fallback failed: {e2}")
            return False

def open_youtube(query=None):
    """
    Opens YouTube. If query is provided, opens search results.
    Uses Chrome standalone app mode if configured for an app-like experience.
    """
    settings = config.load_settings()
    chrome_path = settings.get("chrome_path")
    app_mode = settings.get("youtube_app_mode", True)
    
    if query:
        encoded = urllib.parse.quote_plus(query)
        target_url = f"https://www.youtube.com/results?search_query={encoded}"
    else:
        target_url = "https://www.youtube.com"
        
    if chrome_path and os.path.exists(chrome_path):
        if app_mode:
            # Standalone App window (looks like dedicated YouTube desktop app)
            launch_process([chrome_path, f"--app={target_url}"])
            return f"Opening YouTube Desktop ({'Search: ' + query if query else 'Home'})"
        else:
            launch_process([chrome_path, target_url])
            return f"Opening YouTube in Chrome ({'Search: ' + query if query else 'Home'})"
    else:
        webbrowser.open(target_url)
        return f"Opening YouTube in browser ({'Search: ' + query if query else 'Home'})"

def open_chrome_with_profile(profile_query="Default"):
    """
    Launches Chrome directly with the target profile.
    Supports queries like 'my profile', 'omshree', 'vit', 'college', or directory name.
    """
    settings = config.load_settings()
    chrome_path = settings.get("chrome_path")
    
    if not chrome_path or not os.path.exists(chrome_path):
        return "Chrome executable not found on system."
        
    dir_name, info = match_profile(profile_query)
    profile_name = info.get("name", dir_name)
    
    # Launch Chrome directly into the specified profile
    cmd = [chrome_path, f"--profile-directory={dir_name}"]
    launch_process(cmd)
    
    return f"Opened Chrome with profile: {profile_name}"

def click_chrome_profile(profile_query="Default"):
    """
    Handles the command: 'click my profile' or selects the profile in Chrome.
    If Chrome profile picker is active, activates the profile.
    Otherwise opens Chrome with that profile.
    """
    dir_name, info = match_profile(profile_query)
    profile_name = info.get("name", dir_name)
    
    # We can bring Chrome to focus or launch directly with profile
    settings = config.load_settings()
    chrome_path = settings.get("chrome_path")
    
    if chrome_path and os.path.exists(chrome_path):
        # Direct profile directory launch is 100% reliable in Chromium
        launch_process([chrome_path, f"--profile-directory={dir_name}"])
        # Give brief delay and ensure window is active
        time.sleep(0.5)
        return f"Selected profile: {profile_name}"
    else:
        return "Chrome not found to select profile."

def open_google_search(query):
    """Searches Google for the given query."""
    encoded = urllib.parse.quote_plus(query)
    url = f"https://www.google.com/search?q={encoded}"
    settings = config.load_settings()
    chrome_path = settings.get("chrome_path")
    if chrome_path and os.path.exists(chrome_path):
        launch_process([chrome_path, url])
    else:
        webbrowser.open(url)
    return f"Searching Google for: '{query}'"

def open_website(url, name=None):
    """Opens any specified website."""
    if not url.startswith("http"):
        url = "https://" + url
    settings = config.load_settings()
    chrome_path = settings.get("chrome_path")
    if chrome_path and os.path.exists(chrome_path):
        launch_process([chrome_path, url])
    else:
        webbrowser.open(url)
    return f"Opening {name or url}"

def open_windows_app(app_name):
    """Opens common Windows apps by name."""
    app_lower = app_name.lower().strip()
    
    app_map = {
        "notepad": "notepad.exe",
        "calculator": "calc.exe",
        "calc": "calc.exe",
        "explorer": "explorer.exe",
        "file explorer": "explorer.exe",
        "files": "explorer.exe",
        "cmd": "cmd.exe",
        "command prompt": "cmd.exe",
        "terminal": "wt.exe",
        "powershell": "powershell.exe",
        "task manager": "taskmgr.exe",
        "settings": "ms-settings:",
        "camera": "microsoft.windows.camera:",
        "snipping tool": "snippingtool.exe",
        "paint": "mspaint.exe",
    }
    
    target = app_map.get(app_lower)
    if target:
        try:
            if target.startswith("ms-"):
                os.system(f"start {target}")
            else:
                subprocess.Popen([target], shell=True)
            return f"Opening {app_name.title()}"
        except Exception as e:
            return f"Failed to open {app_name}: {e}"
            
    # Generic start
    try:
        subprocess.Popen(["start", app_name], shell=True)
        return f"Launching {app_name}"
    except Exception as e:
        return f"Could not launch {app_name}"

def control_volume(action):
    """Controls volume (up, down, mute)."""
    action = action.lower()
    if "up" in action:
        pyautogui.press("volumeup", presses=4)
        return "Volume Increased"
    elif "down" in action:
        pyautogui.press("volumedown", presses=4)
        return "Volume Decreased"
    elif "mute" in action or "unmute" in action:
        pyautogui.press("volumemute")
        return "Volume Toggled Mute"
    return "Volume command not recognized"

def take_screenshot():
    """Triggers Windows snipping tool or captures screen."""
    try:
        pyautogui.hotkey("win", "shift", "s")
        return "Snipping Tool activated"
    except Exception as e:
        return f"Screenshot failed: {e}"

def minimize_all_windows():
    """Minimizes all windows to show the desktop."""
    try:
        pyautogui.hotkey("win", "d")
        return "Showing Desktop"
    except Exception as e:
        return f"Desktop toggle failed: {e}"
