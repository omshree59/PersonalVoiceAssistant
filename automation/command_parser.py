import os
import sys
import re
import time

# Ensure project root is in python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from automation.actions import (
    open_youtube,
    open_chrome_with_profile,
    click_chrome_profile,
    open_google_search,
    open_website,
    open_windows_app,
    control_volume,
    take_screenshot,
    minimize_all_windows
)

# Common websites quick lookup
KNOWN_WEBSITES = {
    "github": "https://github.com",
    "google": "https://google.com",
    "chatgpt": "https://chatgpt.com",
    "openai": "https://chatgpt.com",
    "reddit": "https://reddit.com",
    "gmail": "https://mail.google.com",
    "netflix": "https://netflix.com",
    "spotify": "https://open.spotify.com",
    "twitter": "https://x.com",
    "x": "https://x.com",
    "instagram": "https://instagram.com",
    "whatsapp": "https://web.whatsapp.com",
    "linkedin": "https://linkedin.com",
    "twitch": "https://twitch.tv",
    "amazon": "https://amazon.com",
}

def clean_transcript(text):
    """Normalizes voice transcript."""
    t = text.lower().strip()
    # Remove trailing punctuation
    t = re.sub(r"[.,?!]+$", "", t)
    return t

def split_chained_commands(text):
    """
    Detects chained commands separated by:
    - 'and then'
    - 'then'
    - 'and' (when followed by an action verb like click, open, search, etc.)
    """
    t = clean_transcript(text)
    
    # Check for 'and then'
    if " and then " in t:
        return [part.strip() for part in t.split(" and then ") if part.strip()]
        
    # Check for ' then '
    if " then " in t:
        return [part.strip() for part in t.split(" then ") if part.strip()]
        
    # Check for ' and ' followed by an action verb
    match = re.split(r"\s+and\s+(?=(?:click|select|open|launch|search|press|type|close|minimize)\b)", t)
    if len(match) > 1:
        return [part.strip() for part in match if part.strip()]
        
    return [t]

def execute_single_command(cmd_text):
    """
    Executes a single voice command. Returns (success: bool, response_message: str).
    """
    t = clean_transcript(cmd_text)
    if not t:
        return False, "No speech detected"
        
    # 1. YouTube Commands
    if "youtube" in t:
        # Search on YouTube: "search python tutorial on youtube" or "youtube search lofi"
        search_match = re.search(r"(?:search|find|play)\s+(.+?)\s+(?:on|in)\s+youtube", t)
        if not search_match:
            search_match = re.search(r"youtube\s+(?:search|find|play)\s+(.+)", t)
        if search_match:
            query = search_match.group(1).strip()
            msg = open_youtube(query=query)
            return True, msg
            
        # Just open YouTube: "open youtube", "launch youtube app", "go to youtube"
        if any(w in t for w in ["open", "launch", "start", "go to", "show"]) or t == "youtube":
            msg = open_youtube()
            return True, msg

    # 2. Chrome and Profile Commands
    # e.g. "open chrome and then click my profile" or "click my profile" or "open my profile"
    if "profile" in t or "chrome" in t:
        # User says: "click my profile" / "select my profile" / "click profile"
        if any(w in t for w in ["click", "select", "choose", "switch"]):
            msg = click_chrome_profile(t)
            return True, msg
            
        # User says: "open chrome with my profile" or "open my profile in chrome" or "open profile omshree"
        if "profile" in t and ("open" in t or "launch" in t):
            msg = open_chrome_with_profile(t)
            return True, msg
            
        # User says: "open chrome" / "launch chrome"
        if t in ["open chrome", "launch chrome", "start chrome", "chrome"]:
            msg = open_chrome_with_profile("Default")
            return True, msg

    # 3. Google Search
    # "search python asyncio on google" or "google how to cook pasta"
    google_match = re.search(r"(?:search|find)\s+(.+?)\s+(?:on|in)\s+google", t)
    if google_match:
        query = google_match.group(1).strip()
        msg = open_google_search(query)
        return True, msg
        
    if t.startswith("google "):
        query = t[7:].strip()
        msg = open_google_search(query)
        return True, msg

    # 4. Known Websites
    for site_key, site_url in KNOWN_WEBSITES.items():
        if f"open {site_key}" in t or f"launch {site_key}" in t or f"go to {site_key}" in t:
            msg = open_website(site_url, site_key.title())
            return True, msg

    # 5. Volume Controls
    if "volume" in t or "mute" in t or "unmute" in t:
        msg = control_volume(t)
        return True, msg

    # 6. Screenshot
    if any(w in t for w in ["screenshot", "screen shot", "snip"]):
        msg = take_screenshot()
        return True, msg

    # 7. Minimize all / Show desktop
    if any(p in t for p in ["minimize all", "show desktop", "minimize windows", "go to desktop"]):
        msg = minimize_all_windows()
        return True, msg

    # 8. Windows Apps: "open notepad", "open calculator", "open cmd", etc.
    app_open_match = re.search(r"(?:open|launch|start)\s+([a-zA-Z0-9_\s]+)", t)
    if app_open_match:
        app_target = app_open_match.group(1).strip()
        msg = open_windows_app(app_target)
        return True, msg

    # Fallback search if phrased as a question
    if t.startswith("what is") or t.startswith("who is") or t.startswith("how to"):
        msg = open_google_search(t)
        return True, msg

    return False, f"Command not recognized: '{cmd_text}'"

def parse_and_execute(full_transcript):
    """
    Main entry point for command execution.
    Handles single commands or chained sequences ('open chrome and then click my profile').
    Returns a list of result messages.
    """
    commands = split_chained_commands(full_transcript)
    results = []
    
    for idx, cmd in enumerate(commands):
        if idx > 0:
            # Brief pause between sequential steps for window to settle
            time.sleep(0.8)
            
        success, message = execute_single_command(cmd)
        results.append(message)
        print(f"[CommandParser] Step {idx+1}: '{cmd}' -> {message}")
        
    return " | ".join(results)

if __name__ == "__main__":
    test_cases = [
        "open youtube",
        "search lofi hip hop on youtube",
        "open chrome and then click my profile",
        "open chrome and click my profile",
        "open calculator",
        "volume up",
        "open github",
        "show desktop",
    ]
    print("Testing Command Parser:")
    for tc in test_cases:
        print(f"\nVoice Input: '{tc}'")
        res = parse_and_execute(tc)
        print(f"Result: {res}")
