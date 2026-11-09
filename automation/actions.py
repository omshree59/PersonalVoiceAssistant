import os
import sys
import subprocess
import webbrowser
import urllib.parse
import time
import json
import re
import pyautogui
pyautogui.FAILSAFE = False

# Ensure project root is in python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config
from automation.profile_helper import match_profile, get_installed_chrome_profiles

_START_APPS_CACHE = None

def get_installed_windows_apps():
    """
    Returns a dict mapping lowercase application names to their (display_name, AppID) from Get-StartApps.
    Cached for fast subsequent lookups.
    """
    global _START_APPS_CACHE
    if _START_APPS_CACHE is not None:
        return _START_APPS_CACHE

    apps = {}
    try:
        cmd = [
            "powershell",
            "-NoProfile",
            "-NonInteractive",
            "-Command",
            "Get-StartApps | ConvertTo-Json -Compress"
        ]
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
        if res.returncode == 0 and res.stdout.strip():
            data = json.loads(res.stdout)
            if isinstance(data, dict):
                data = [data]
            for item in data:
                name = item.get("Name", "").strip()
                appid = item.get("AppID", "").strip()
                if name and appid:
                    apps[name.lower()] = (name, appid)
    except Exception as e:
        print(f"[Actions] Error querying Get-StartApps: {e}")

    _START_APPS_CACHE = apps
    return apps

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
            subprocess.Popen(command_list, shell=True)
            return True
        except Exception as e2:
            print(f"[Actions] Shell fallback failed: {e2}")
            return False

def open_youtube(query=None, new_window=False):
    """
    Opens YouTube. If query is provided, opens search results.
    By default opens as a new tab in the running Chrome window (or a new window if specified).
    """
    settings = config.load_settings()
    chrome_path = settings.get("chrome_path")
    app_mode = settings.get("youtube_app_mode", False)
    
    if query:
        encoded = urllib.parse.quote_plus(query)
        target_url = f"https://www.youtube.com/results?search_query={encoded}"
    else:
        target_url = "https://www.youtube.com"
        
    if chrome_path and os.path.exists(chrome_path):
        if app_mode:
            launch_process([chrome_path, f"--app={target_url}"])
            return f"Opening YouTube Desktop ({'Search: ' + query if query else 'Home'})"
        elif new_window:
            launch_process([chrome_path, "--new-window", target_url])
            return f"Opening YouTube in new Chrome window ({'Search: ' + query if query else 'Home'})"
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
    
    settings = config.load_settings()
    chrome_path = settings.get("chrome_path")
    
    if chrome_path and os.path.exists(chrome_path):
        launch_process([chrome_path, f"--profile-directory={dir_name}"])
        time.sleep(0.5)
        return f"Selected profile: {profile_name}"
    else:
        return "Chrome not found to select profile."

def open_google_search(query, new_window=False):
    """Searches Google for the given query in Chrome."""
    encoded = urllib.parse.quote_plus(query)
    url = f"https://www.google.com/search?q={encoded}"
    settings = config.load_settings()
    chrome_path = settings.get("chrome_path")
    if chrome_path and os.path.exists(chrome_path):
        if new_window:
            launch_process([chrome_path, "--new-window", url])
        else:
            launch_process([chrome_path, url])
    else:
        webbrowser.open(url)
    return f"Searching Google for: '{query}'"

def open_website(url, name=None, new_window=False):
    """Opens any specified website in Chrome (as a tab or new window)."""
    if not url.startswith("http"):
        url = "https://" + url
    settings = config.load_settings()
    chrome_path = settings.get("chrome_path")
    if chrome_path and os.path.exists(chrome_path):
        if new_window:
            launch_process([chrome_path, "--new-window", url])
        else:
            launch_process([chrome_path, url])
    else:
        webbrowser.open(url)
    return f"Opening {name or url}"

def open_windows_app(app_name):
    """
    Opens common and installed Windows applications by name or AppID.
    Supports native apps like WhatsApp, Xbox, Steam, Spotify, VS Code, Calculator, etc.
    Returns (success: bool, message: str).
    """
    clean = app_name.lower().strip()
    clean = re.sub(r"^the\s+", "", clean)
    clean = re.sub(r"\s+app(?:lication)?$", "", clean).strip()

    if not clean:
        return False, "No application name specified."

    # 1. Known high-priority application mappings & URI schemes
    known_apps = {
        "whatsapp": ("WhatsApp", "shell:AppsFolder\\5319275A.WhatsAppDesktop_cv1g1gvanyjgm!App"),
        "xbox": ("Xbox", "shell:AppsFolder\\Microsoft.GamingApp_8wekyb3d8bbwe!Microsoft.Xbox.App"),
        "spotify": ("Spotify", "spotify:"),
        "discord": ("Discord", "discord:"),
        "steam": ("Steam", "steam:"),
        "notepad": ("Notepad", "notepad.exe"),
        "calculator": ("Calculator", "calc.exe"),
        "calc": ("Calculator", "calc.exe"),
        "explorer": ("File Explorer", "explorer.exe"),
        "file explorer": ("File Explorer", "explorer.exe"),
        "files": ("File Explorer", "explorer.exe"),
        "cmd": ("Command Prompt", "cmd.exe"),
        "command prompt": ("Command Prompt", "cmd.exe"),
        "terminal": ("Windows Terminal", "wt.exe"),
        "windows terminal": ("Windows Terminal", "wt.exe"),
        "powershell": ("PowerShell", "powershell.exe"),
        "task manager": ("Task Manager", "taskmgr.exe"),
        "taskmgr": ("Task Manager", "taskmgr.exe"),
        "settings": ("Windows Settings", "ms-settings:"),
        "camera": ("Camera", "microsoft.windows.camera:"),
        "snipping tool": ("Snipping Tool", "snippingtool.exe"),
        "snip": ("Snipping Tool", "snippingtool.exe"),
        "paint": ("Paint", "mspaint.exe"),
        "vs code": ("Visual Studio Code", "code"),
        "vscode": ("Visual Studio Code", "code"),
        "visual studio code": ("Visual Studio Code", "code"),
    }

    if clean in known_apps:
        display_name, target = known_apps[clean]
        try:
            if target.startswith("shell:") or (":" in target and not (len(target) > 1 and target[1] == ":")):
                os.startfile(target)
            else:
                subprocess.Popen([target], shell=True)
            return True, f"Opening {display_name}"
        except Exception as e:
            try:
                subprocess.Popen(f"start {target}", shell=True)
                return True, f"Opening {display_name}"
            except Exception as e2:
                print(f"[Actions] Failed to launch known app {display_name}: {e2}")

    # 2. Check installed Windows StartApps dynamically
    installed = get_installed_windows_apps()
    
    # Exact match in installed apps
    if clean in installed:
        disp, app_id = installed[clean]
        try:
            os.startfile(f"shell:AppsFolder\\{app_id}")
            return True, f"Opening {disp}"
        except Exception:
            subprocess.Popen(["explorer.exe", f"shell:AppsFolder\\{app_id}"])
            return True, f"Opening {disp}"

    # Partial / substring match in installed apps
    for app_key, (disp, app_id) in installed.items():
        if clean == app_key or clean in app_key or app_key.startswith(clean):
            try:
                os.startfile(f"shell:AppsFolder\\{app_id}")
                return True, f"Opening {disp}"
            except Exception:
                subprocess.Popen(["explorer.exe", f"shell:AppsFolder\\{app_id}"])
                return True, f"Opening {disp}"

    # 3. Generic Windows start fallback
    try:
        subprocess.Popen(f"start {clean}", shell=True)
        return True, f"Launching {clean.title()}"
    except Exception as e:
        return False, f"Could not launch application: {clean}"

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
