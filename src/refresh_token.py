import json, requests

def refresh_access_token():
    """Refresh or generate Upstox access token"""

    with open("config/credentials.json") as f:
        cfg = json.load(f)

    CLIENT_ID     = cfg.get("client_id")
    CLIENT_SECRET = cfg.get("client_secret")
    REDIRECT_URI  = cfg.get("redirect_uri")
    REFRESH_TOKEN = cfg.get("refresh_token")
    AUTH_CODE     = cfg.get("code")   # one-time code from login URL

    url = "https://api.upstox.com/v2/login/authorization/token"

    # -------------------- REFRESH FLOW --------------------
    if REFRESH_TOKEN:
        data = {
            "grant_type": "refresh_token",
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "refresh_token": REFRESH_TOKEN,
        }
        print("🔄 Using refresh_token flow...")

    # -------------------- AUTHORIZATION CODE FLOW --------------------
    elif AUTH_CODE:
        data = {
            "grant_type": "authorization_code",
            "code": AUTH_CODE,
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "redirect_uri": REDIRECT_URI,
        }
        print("⚡ Using authorization_code flow (first time)...")

    else:
        raise SystemExit("❌ Missing both refresh_token and code in config/credentials.json.")

    r = requests.post(url, data=data, timeout=10)
    if r.status_code != 200:
        print("❌ Token request failed:", r.status_code, r.text)
        r.raise_for_status()

    token_data = r.json()
    access_token  = token_data["access_token"]
    new_refresh   = token_data.get("refresh_token")

    # Update JSON file so next run always uses refresh flow
    cfg["access_token"] = access_token
    if new_refresh:
        cfg["refresh_token"] = new_refresh
    # Clear code after first use
    if "code" in cfg:
        cfg.pop("code")

    with open("config/credentials.json", "w") as f:
        json.dump(cfg, f, indent=2)

    return access_token

