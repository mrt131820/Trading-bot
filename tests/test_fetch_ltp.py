import json, time, datetime, math, random, requests
from typing import Dict, Optional, Tuple

API_BASE = "https://api.upstox.com"  # or sandbox URL
HEADERS = {
    "Authorization": "Bearer eyJ0eXAiOiJKV1QiLCJrZXlfaWQiOiJza192MS4wIiwiYWxnIjoiSFMyNTYifQ.eyJzdWIiOiI0MDY4NzkiLCJqdGkiOiI2OGFiZTc0YmQ0OTIxYjRjZDIzYTIyNDkiLCJpc011bHRpQ2xpZW50IjpmYWxzZSwiaXNQbHVzUGxhbiI6ZmFsc2UsImlhdCI6MTc1NjA5NjMzMSwiaXNzIjoidWRhcGktZ2F0ZXdheS1zZXJ2aWNlIiwiZXhwIjoxNzU2MTU5MjAwfQ.ob-oMiYHEMwwXKYmR-d6i5E23VkW0csc0bxbWLxPnpU",
    "Accept": "application/json",
    "Content-Type": "application/json"
}

NIFTY_INSTRUMENT_KEY = "NSE_INDEX|Nifty 50"

# ----------------- Time helpers -----------------------
IST = datetime.timezone(datetime.timedelta(hours=5, minutes=30))
def now_ist() -> datetime.datetime: 
    return datetime.datetime.now(tz=IST)

def wait_until_ist(hour: int, minute: int):
    while True:
        t = now_ist()
        if (t.hour, t.minute) >= (hour, minute): 
            return
        time.sleep(5)

# ----------------- Utility ---------------------------
def next_thursday_date_iso():
    today = datetime.date.today()
    days_ahead = 3 - today.weekday()  # Thursday=3
    if days_ahead <= 0:
        days_ahead += 7
    nxt = today + datetime.timedelta(days_ahead)
    return nxt.isoformat()  # YYYY-MM-DD

def normalize_key(k: str) -> str: 
    return k.replace(":", "|").upper()

def safe_get(ltp_map: Dict[str,float], token: str) -> Optional[float]:
    if token in ltp_map:
        return ltp_map[token]
    if token.replace("|", ":") in ltp_map:
        return ltp_map[token.replace("|", ":")]
    if token.replace(":", "|") in ltp_map:
        return ltp_map[token.replace(":", "|")]
    print(f"[WARN] Token {token} not found in {list(ltp_map.keys())}")
    return None


def this_or_next_thursday_date_iso():
    """Return this Thursday (today if Thursday), else next Thursday. ✅"""
    today = now_ist().date()
    days_ahead = (3 - today.weekday()) % 7   # Mon=0
    return (today + datetime.timedelta(days=days_ahead)).isoformat()

def round_nearest_50(x: float) -> int: 
    return int(round(x/50.0)*50)


def get_ltp_for(instrument_keys) -> Dict[str,float]:
    # if MODE=="sandbox": 
    #     raise RuntimeError("Sandbox uses simulated prices.")
    if isinstance(instrument_keys, list): 
        instrument_keys=",".join(instrument_keys)
    url=f"{API_BASE}/v3/market-quote/ltp"
    r=requests.get(url, headers=HEADERS, params={"instrument_key":instrument_keys}, timeout=10)
    r.raise_for_status()
    data = r.json().get("data",{})
    print("DEBUG LTP response:", data)
    out  = {}
    for k,v in data.items(): 
        token = v.get("instrument_token") or normalize_key(k)
        out[token] = float(v.get("last_price") or v.get("ltp") or 0.0)
    return out


spot_map=get_ltp_for(NIFTY_INSTRUMENT_KEY)
spot=safe_get(spot_map,NIFTY_INSTRUMENT_KEY)

atm_strike = round_nearest_50(float(spot))
print("ATM Strike (nearest 50):", atm_strike)

state={"CE":{"token":'NSE_FO|71970',"entry":105.7,"sl_trigger":126.8,"open":True,"order_id":250825000125987,"sl_order_id":250825000126019,"realized":0.0,"close_price":None},
           "PE":{"token":'NSE_FO|71971',"entry":74.8,"sl_trigger":89.8,"open":True,"order_id":250825000125999,"sl_order_id":250825000126029,"realized":0.0,"close_price":None}}
trail={"armed":False,"locked_min":0,"last_step_reached":0}
get_ltp_for([state["CE"]["token"],state["PE"]["token"]])

ltp_map=get_ltp_for([state["CE"]["token"],state["PE"]["token"]])
ce_ltp,pe_ltp=safe_get(ltp_map,state["CE"]["token"]),safe_get(ltp_map,state["PE"]["token"])

print(ce_ltp,pe_ltp)




