import os
import json

def get_chrome_user_data_path():
    """Returns the Chrome User Data directory path."""
    return os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\User Data")

def get_installed_chrome_profiles():
    """
    Parses Chrome's Local State file to return all registered profiles.
    Returns a dict mapping directory name to profile info.
    """
    local_state_path = os.path.join(get_chrome_user_data_path(), "Local State")
    profiles = {}
    
    if not os.path.exists(local_state_path):
        return {
            "Default": {
                "name": "Default Profile",
                "gaia_name": "Default User",
                "email": ""
            }
        }
        
    try:
        with open(local_state_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            info_cache = data.get("profile", {}).get("info_cache", {})
            for dir_name, info in info_cache.items():
                profiles[dir_name] = {
                    "name": info.get("name", dir_name),
                    "gaia_name": info.get("gaia_name", ""),
                    "gaia_given_name": info.get("gaia_given_name", ""),
                    "email": info.get("user_name", ""),
                    "hosted_domain": info.get("hosted_domain", "")
                }
    except Exception as e:
        print(f"[ProfileHelper] Error reading Chrome Local State: {e}")
        profiles["Default"] = {"name": "Default", "gaia_name": "Default User", "email": ""}
        
    return profiles

def match_profile(query_text, profiles=None):
    """
    Finds the best matching profile directory name given user speech like:
    - 'my profile'
    - 'personal profile'
    - 'omshree'
    - 'college profile' / 'vit'
    - 'iit' / 'scale'
    """
    if profiles is None:
        profiles = get_installed_chrome_profiles()
        
    q = query_text.lower().strip()
    
    # Direct personal synonyms default to primary profile
    personal_keywords = ["my profile", "personal", "main", "primary", "default", "me", "myself", "omshree", "parida"]
    for kw in personal_keywords:
        if kw in q:
            # Look for profile matching personal email or Default
            for dir_name, p in profiles.items():
                if "gmail.com" in p["email"].lower() or "omshree" in p["name"].lower() or dir_name == "Default":
                    return dir_name, p
                    
    # Look for college / academic keywords
    for dir_name, p in profiles.items():
        domain = p.get("hosted_domain", "").lower()
        name = p.get("name", "").lower()
        email = p.get("email", "").lower()
        
        # Check VIT
        if any(k in q for k in ["vit", "college", "student", "vitap"]) and ("vit" in domain or "vit" in name or "vit" in email):
            return dir_name, p
            
        # Check IIT / scale
        if any(k in q for k in ["iit", "scale", "rpr", "ropar"]) and ("iitrpr" in domain or "scale" in name or "scale" in email):
            return dir_name, p
            
    # Substring search across all profiles
    for dir_name, p in profiles.items():
        if p["name"].lower() in q or (p["gaia_given_name"] and p["gaia_given_name"].lower() in q):
            return dir_name, p
            
    # Default fallback
    if "Default" in profiles:
        return "Default", profiles["Default"]
    elif profiles:
        first_key = list(profiles.keys())[0]
        return first_key, profiles[first_key]
        
    return "Default", {"name": "Default", "email": ""}

if __name__ == "__main__":
    profs = get_installed_chrome_profiles()
    print("Detected Chrome Profiles:")
    for d, info in profs.items():
        print(f" - [{d}]: {info['name']} ({info['email']}) [Domain: {info['hosted_domain']}]")
        
    test_queries = ["open my profile", "click my profile", "vit profile", "iit profile", "omshree profile"]
    print("\nMatching Tests:")
    for t in test_queries:
        matched_dir, matched_info = match_profile(t, profs)
        print(f" '{t}' -> Directory: {matched_dir} ({matched_info['name']})")
