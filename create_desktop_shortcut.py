import os
import sys
import win32com.client

def create_shortcut():
    """Creates a Windows desktop shortcut for the Voice Listener."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    desktop_dir = os.path.expandvars(r"%USERPROFILE%\Desktop")
    shortcut_path = os.path.join(desktop_dir, "Voice Listener.lnk")
    
    # Target script: run_silent.vbs or pythonw app.py
    vbs_path = os.path.join(base_dir, "run_silent.vbs")
    ico_path = os.path.join(base_dir, "assets", "icon.ico")
    
    try:
        shell = win32com.client.Dispatch("WScript.Shell")
        shortcut = shell.CreateShortCut(shortcut_path)
        shortcut.TargetPath = "wscript.exe"
        shortcut.Arguments = f'"{vbs_path}"'
        shortcut.WorkingDirectory = base_dir
        shortcut.Description = "Personal Desktop Voice Listener"
        if os.path.exists(ico_path):
            shortcut.IconLocation = f"{ico_path},0"
        shortcut.Save()
        print(f"[Shortcut] Successfully created desktop shortcut:\n  -> {shortcut_path}")
        return True
    except Exception as e:
        print(f"[Shortcut] Failed to create shortcut: {e}")
        return False

if __name__ == "__main__":
    create_shortcut()
