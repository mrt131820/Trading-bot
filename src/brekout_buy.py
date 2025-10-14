#!/usr/bin/env python3
"""
NIFTY Weekly Option Buying Bot (Sandbox + Production)

Behavior:
- At ENTRY_HH:ENTRY_MM → Place SL-L BUY orders at 15% above CMP (ATM CE & PE)
  Trigger = CMP * 1.15, Limit = Trigger + 5
- When buy order fills → place SL (SELL SL-L) = 15% below entry
- Trail SL upward: for each STEP_UP_PCT rise (30%), raise SL by TRAIL_INC_PCT (15%) of initial SL
- Exit all open positions at EXIT_HH:EXIT_MM
"""

import json
import os, sys, time, datetime, random, requests
from typing import Dict, Optional, Tuple

# If you keep credentials as a module, adjust import path accordingly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
try:
    from config.credentials import credentials as cfg
except Exception:
    # fallback: read from env to avoid import issues
    cfg = {
        "mode": os.getenv("MODE", "sandbox"),
        "access_token": os.getenv("ACCESS_TOKEN_BUY", ""),
        "sandbox_access_token": os.getenv("SANDBOX_ACCESS_TOKEN", ""),
    }

# ---------------- CONFIG -------------------
MODE = cfg.get("mode", "sandbox").lower()
TOKEN = cfg.get("access_token_buy") if MODE == "production" else cfg.get("sandbox_access_token")
if not TOKEN:
    print("Warning: no token found for selected mode. If you intended production, set credentials properly.")
API_BASE = "https://api.upstox.com" if MODE == "production" else "https://api-sandbox.upstox.com"
HEADERS = {"Authorization": f"Bearer {TOKEN}", "Accept": "application/json", "Content-Type": "application/json"}

# Strategy params
BREAKOUT_PCT = 16.
SL_PCT = 16.0
STEP_UP_PCT = 30.0
TRAIL_INC_PCT = 15.0    # 15% of initial SL per step (kept as requested)
ENTRY_HH, ENTRY_MM = 10, 30
EXIT_HH, EXIT_MM = 14, 30
POLL_INTERVAL = 5
NIFTY_INSTRUMENT_KEY = "NSE_INDEX|Nifty 50"
QTY = 300

# Optional behavior
CANCEL_OPPOSITE_ON_FILL = False  # If True, cancel the other leg once one leg fills

# Sandbox knobs
SANDBOX_SIM_SEED = 42
SANDBOX_SIM_START_SPOT = 19500.0
SANDBOX_SIM_BASE_PREMIUM = 130.0
SANDBOX_SIM_LOT_SIZE = 50
SANDBOX_SIM_SPOT_SIGMA = 30.0
SANDBOX_SIM_OPT_DELTA_SENS = 1.2
SANDBOX_SIM_THETA_DECAY = 0.1
SANDBOX_SIM_MIN_PREMIUM = 1.0
SANDBOX_SIM_VERBOSE = True

# ---------------- TIME / UTIL ----------------
IST = datetime.timezone(datetime.timedelta(hours=5, minutes=30))
def now_ist() -> datetime.datetime:
    return datetime.datetime.now(tz=IST)

def wait_until_ist(hour:int, minute:int):
    while True:
        t = now_ist()
        if (t.hour, t.minute) >= (hour, minute): 
            return
        time.sleep(1)

def normalize_key(k:str)->str:
    return k.replace(":", "|").upper()

def safe_get(d:Dict[str,float], key:str)->Optional[float]:
    if key in d: return d[key]
    for alt in (key.replace("|", ":"), key.replace(":", "|")):
        if alt in d: return d[alt]
    return None

def round_nearest_50(x:float)->int:
    return int(round(x/50.0)*50)

def this_or_next_tuesday_date_iso():
    today = now_ist().date()
    days_ahead = (1 - today.weekday()) % 7
    return (today + datetime.timedelta(days=days_ahead)).isoformat()

# ---------------- SL LOGIC ----------------
def compute_initial_sl(entry: float) -> float:
    today = now_ist().date()
    if today.weekday() == 1:  # Tuesday
        return round(entry - 30, 1)
    return round(entry * (1 - SL_PCT/100.0), 1)

def compute_trailing_sl(entry: float, step_level: int) -> float:
    """Trail SL upward by TRAIL_INC_PCT of initial SL per step"""
    today = now_ist().date()
    if today.weekday() == 1:
        base_sl = entry - 30
        return round(base_sl + 30 * step_level, 1)
    else:
        base_sl = entry * (1 - SL_PCT/100.0)
        trail_amount = base_sl * (TRAIL_INC_PCT / 100.0) * step_level
        return round(base_sl + trail_amount, 1)

# ---------------- SANDBOX SIM ----------------
class PriceSimulator:
    def __init__(self, spot0:float, ce:str, pe:str):
        random.seed(SANDBOX_SIM_SEED)
        self.spot = spot0
        self.ce_token, self.pe_token = ce, pe
        self.ce = self.pe = SANDBOX_SIM_BASE_PREMIUM

    def tick(self) -> Dict[str,float]:
        dS = random.gauss(0, SANDBOX_SIM_SPOT_SIGMA)
        self.spot += dS
        self.ce = max(SANDBOX_SIM_MIN_PREMIUM, self.ce + SANDBOX_SIM_OPT_DELTA_SENS*dS - SANDBOX_SIM_THETA_DECAY)
        self.pe = max(SANDBOX_SIM_MIN_PREMIUM, self.pe - SANDBOX_SIM_OPT_DELTA_SENS*dS - SANDBOX_SIM_THETA_DECAY)
        if SANDBOX_SIM_VERBOSE:
            print(f"[SIM] CE={self.ce:.1f} PE={self.pe:.1f}")
        return {self.ce_token: round(self.ce,1), self.pe_token: round(self.pe,1)}

def build_sandbox_chain(expiry_iso:str, spot:float) -> Tuple[str,str,int]:
    atm = round_nearest_50(spot)
    return f"SIM|CE_ATM_{atm}", f"SIM|PE_ATM_{atm}", SANDBOX_SIM_LOT_SIZE

# ---------------- API WRAPPERS ----------------
def get_ltp_for(instrument_keys) -> Dict[str,float]:
    """Production: call Upstox LTP endpoint. Accept list or single string."""
    if MODE == "sandbox":
        raise RuntimeError("get_ltp_for should not be used in sandbox mode.")
    if isinstance(instrument_keys, list):
        instrument_keys = ",".join(instrument_keys)
    url = f"{API_BASE}/v3/market-quote/ltp"
    r = requests.get(url, headers=HEADERS, params={"instrument_key": instrument_keys}, timeout=10)
    r.raise_for_status()
    data = r.json().get("data", {})
    out = {}
    for k, v in data.items():
        token = v.get("instrument_token") or normalize_key(k)
        out[token] = float(v.get("last_price") or v.get("ltp") or 0.0)
    return out

def get_option_chain(expiry_date_iso: str):
    """Return option chain data (raw) from Upstox."""
    if MODE == "sandbox":
        raise RuntimeError("get_option_chain should not be used in sandbox mode.")
    url = f"{API_BASE}/v2/option/chain"
    r = requests.get(url, headers=HEADERS, params={"instrument_key": NIFTY_INSTRUMENT_KEY, "expiry_date": expiry_date_iso}, timeout=15)
    r.raise_for_status()
    return r.json().get("data", [])

def place_order(token:str, side:str, qty:int, order_type="MARKET", product="D", price=0.0, trigger_price=None):
    """Default product set to 'D' (NRML) for short options. ✅"""
    url=f"{API_BASE}/v2/order/place"
    payload={"quantity":qty,"product":product,"validity":"DAY",
             "price":0 if order_type=="MARKET" else round(float(price or 0.0),1),
             "instrument_token":token,"order_type":order_type,"transaction_type":side,
             "disclosed_quantity":0,"trigger_price":0,"is_amo":False}
    if order_type=="SL":
        if trigger_price is None: 
            raise ValueError("SL needs trigger_price")
        trig = round(float(trigger_price),1)
        payload["trigger_price"]=trig
        payload["price"]=round(trig+5,1) if side=="BUY" else round(trig-5,1)  # small offset ✅
    r=requests.post(url, headers=HEADERS, json=payload, timeout=20)
    if not r.ok:
        print("[ERROR] Order payload:", json.dumps(payload, indent=2))
        print("[ERROR] Upstox response:", r.text)
    r.raise_for_status()
    return r.json()

def cancel_order(oid:str):
    if not oid:
        return
    if MODE == "sandbox":
        print(f"[SIM CANCEL] order {oid}")
        return
    url = f"{API_BASE}/v2/order/cancel"
    r = requests.delete(url, headers=HEADERS, params={"order_id": oid}, timeout=30)
    r.raise_for_status()

def get_order_status(order_id: str) -> Dict:
    """Query order status (production). Return dict with 'status' and 'filled_price' if available."""
    if MODE == "sandbox":
        return {"status": "OPEN", "filled_price": None}
    url = f"{API_BASE}/v2/order/details"
    r = requests.get(url, headers=HEADERS, params={"order_id": order_id}, timeout=10)
    if not r.ok:
        print("[ERROR] Upstox response:", r.text)
    r.raise_for_status()
    d = r.json().get("data", {})
    return {
        "status": d.get("status") or d.get("order_status"),
        "filled_price": float(d.get("average_fill_price") or d.get("filled_price") or 0.0)
    }
# ---------------- CORE STRATEGY ----------------
def run_option_buy_strategy(wait_for_entry=True):
    print("="*60)
    print(f"Starting bot | MODE={MODE.upper()} | Time={now_ist().isoformat()}")
    print("="*60)

    expiry_iso = this_or_next_tuesday_date_iso()
    print("Target expiry:", expiry_iso)

    if wait_for_entry:
        print(f"Waiting until {ENTRY_HH:02d}:{ENTRY_MM:02d} IST...")
        wait_until_ist(ENTRY_HH, ENTRY_MM)

    # --- prepare instruments ---
    if MODE == "sandbox":
        spot = SANDBOX_SIM_START_SPOT
        ce, pe, lot = build_sandbox_chain(expiry_iso, spot)
        simulator = PriceSimulator(spot, ce, pe)
        ltp_map = simulator.tick()
        ce_cmp, pe_cmp = ltp_map[ce], ltp_map[pe]
    else:
        # production: fetch spot and find ATM CE/PE in chain
        spot_map = get_ltp_for([NIFTY_INSTRUMENT_KEY])
        spot = safe_get(spot_map, NIFTY_INSTRUMENT_KEY)
        if spot is None:
            raise SystemExit("Could not fetch NIFTY spot in production mode.")
        chain = get_option_chain(expiry_iso)
        atm = round_nearest_50(spot)
        ce = pe = None
        lot = None
        # parse chain for ATM strike (structure depends on provider)
        for item in chain:
            try:
                if int(item.get("strike_price", 0)) != atm:
                    continue
                co = item.get("call_options") or item.get("CE") or {}
                po = item.get("put_options") or item.get("PE") or {}
                if co and po:
                    ce = normalize_key(co.get("instrument_key") or co.get("instrumentToken") or "")
                    pe = normalize_key(po.get("instrument_key") or po.get("instrumentToken") or "")
                    lot = int(item.get("lot_size") or item.get("lot") or lot or 1)
                    break
            except Exception:
                continue
        if not ce or not pe:
            raise SystemExit(f"Could not find ATM CE/PE for ATM={atm} in option chain.")
        ltp_map = get_ltp_for([ce, pe])
        ce_cmp, pe_cmp = safe_get(ltp_map, ce), safe_get(ltp_map, pe)

    print(f"CMP CE={ce_cmp}, PE={pe_cmp}")

    # validate qty vs lot
    if lot:
        if QTY % lot != 0:
            raise SystemExit(f"QTY={QTY} must be a multiple of lot_size={lot}. Adjust QTY or lot.")
    qty = QTY

    # compute triggers
    today = now_ist().date()
    if today.weekday() == 1:
        ce_trig = round(ce_cmp + 30,1)
        pe_trig = round(pe_cmp + 30,1)
    else:
        ce_trig = round(ce_cmp * (1+BREAKOUT_PCT/100), 1)
        pe_trig = round(pe_cmp * (1+BREAKOUT_PCT/100), 1)
    ce_lim, pe_lim = ce_trig + 5, pe_trig + 5

    print(f"Placing SL-L Buys: CE trig={ce_trig} lim={ce_lim} | PE trig={pe_trig} lim={pe_lim}")

    # state
    state = {
        "CE": {"token": ce, "buy_order_id": None, "sl_order_id": None, "open": False, "entry": None, "sl_trigger": None},
        "PE": {"token": pe, "buy_order_id": None, "sl_order_id": None, "open": False, "entry": None, "sl_trigger": None},
    }

    # place initial SL-L BUY orders (both legs)
    for leg, trig in (("CE", ce_trig), ("PE", pe_trig)):
        resp = place_order(state[leg]["token"], "BUY", qty, "SL", "D", trigger_price=trig)
        state[leg]["buy_order_id"] = resp["data"]["order_id"]

    print("Monitoring...")
    exit_time = now_ist().replace(hour=EXIT_HH, minute=EXIT_MM, second=0, microsecond=0)

    # main loop
    while True:
        t = now_ist()
        if t >= exit_time:
            print("[EXIT] Exit time reached — closing positions and cancelling SLs.")
            for leg in ("CE","PE"):
                # Cancel any pending buy order
                if state[leg]["buy_order_id"]:
                    cancel_order(state[leg]["buy_order_id"])
                # Cancel any SL order
                if state[leg]["sl_order_id"]:
                    cancel_order(state[leg]["sl_order_id"])
                # Close open position if any
                if state[leg]["open"]:
                    place_order(state[leg]["token"], "SELL", qty, "MARKET", "D")
            break

        # fetch LTPs
        if MODE == "sandbox":
            ltp_map = simulator.tick()
        else:
            try:
                ltp_map = get_ltp_for([ce, pe])
            except Exception as e:
                print("[WARN] LTP fetch failed:", e)
                time.sleep(POLL_INTERVAL)
                continue

        ce_ltp = safe_get(ltp_map, ce)
        pe_ltp = safe_get(ltp_map, pe)

        # iterate legs
        for leg, ltp, trig in (("CE", ce_ltp, ce_trig), ("PE", pe_ltp, pe_trig)):
            st = state[leg]

            # --- Production: detect fills using order status; Sandbox: simulate fill on LTP >= trig ---
            if not st["open"]:
                if MODE == "sandbox":
                    if ltp is not None and ltp >= trig:
                        # simulate fill
                        st["open"] = True
                        st["entry"] = trig
                        st["sl_trigger"] = compute_initial_sl(trig)
                        print(f"[SIM FILL] {leg} filled at {trig} | SL={st['sl_trigger']}")
                        # place SL sell
                        resp = place_order(st["token"], "SELL", qty, "SL", "D", trigger_price=st["sl_trigger"])
                        st["sl_order_id"] = resp["data"]["order_id"]
                        # optionally cancel opposite leg buy order
                        if CANCEL_OPPOSITE_ON_FILL:
                            opp = "PE" if leg == "CE" else "CE"
                            if state[opp]["buy_order_id"]:
                                cancel_order(state[opp]["buy_order_id"])
                                print(f"[CANCEL] Opposite leg {opp} buy order cancelled after {leg} fill.")
                    # else no fill in sandbox this tick
                else:
                    # production: poll buy order status to detect filled
                    buy_oid = st["buy_order_id"]
                    if buy_oid:
                        try:
                            status = get_order_status(buy_oid)
                        except Exception as e:
                            print(f"[WARN] get_order_status failed for {buy_oid}: {e}")
                            status = {"status": "UNKNOWN", "filled_price": None}
                        s = (status.get("status") or "").upper()
                        if s in ("COMPLETE","FILLED","EXECUTED","CANCELLED_AND_EXCH_TRADED","TRADED"):
                            # treated as filled (adjust depending on Upstox fields)
                            fill_price = status.get("filled_price") or trig
                            st["open"] = True
                            st["entry"] = fill_price
                            st["sl_trigger"] = compute_initial_sl(fill_price)
                            print(f"[FILL] {leg} filled at {fill_price} | SL={st['sl_trigger']}")
                            # place SL sell (SELL SL-L)
                            resp = place_order(st["token"], "SELL", qty, "SL", "D", trigger_price=st["sl_trigger"])
                            st["sl_order_id"] = resp["data"]["order_id"]
                            if CANCEL_OPPOSITE_ON_FILL:
                                opp = "PE" if leg == "CE" else "CE"
                                if state[opp]["buy_order_id"]:
                                    cancel_order(state[opp]["buy_order_id"])
                                    print(f"[CANCEL] Opposite leg {opp} buy order cancelled after {leg} fill.")
                    # else no buy order id present or not filled yet

            # If not open yet, continue
            if not st["open"]:
                continue

            entry, sl = st["entry"], st["sl_trigger"]
            if ltp is None:
                continue

            # --- Stop Loss hit (market exit) ---
            if ltp <= sl:
                print(f"[SL HIT] {leg}: LTP={ltp} <= SL={sl} — exiting.")
                st["open"] = False
                st["buy_order_id"] = None
                st["sl_order_id"] = None
                continue

            # --- Trailing logic ---
            today = now_ist().date()
            if today.weekday() == 1:  # Tuesday: step every 30 points
                step_div = 30.0
            else:
                step_div = entry * (STEP_UP_PCT / 100.0)
            if step_div <= 0:
                continue
            step = int(max(0, (ltp - entry) // step_div))
            if step > 0:
                new_sl = compute_trailing_sl(entry, step)
                if new_sl > sl:
                    print(f"[TRAIL] {leg}: step={step}, SL {sl} -> {new_sl}")
                    if st["sl_order_id"]:
                        cancel_order(st["sl_order_id"])
                    resp = place_order(st["token"], "SELL", qty, "SL", "D", trigger_price=new_sl)
                    st["sl_order_id"] = resp["data"]["order_id"]
                    st["sl_trigger"] = new_sl

        time.sleep(POLL_INTERVAL)

    print("Strategy finished.")

# ---------------- ENTRYPOINT ----------------
if __name__ == "__main__":
    run_option_buy_strategy(wait_for_entry=True)
