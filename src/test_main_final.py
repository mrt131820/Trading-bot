#!/usr/bin/env python3
"""
NIFTY Weekly Short-Straddle bot (Upstox v3 LTP + Option Chain)

Spec:
- Sell ATM CE & PE at 10:30 IST
- 20% SL on each leg
- Monitor basket P&L; trail ₹5,000 for every +₹5,000
- If one leg hits SL, move the other leg's SL to COST
- EOD exit ~15:20 IST
- Logs trail steps & exits clearly
"""

import json, time, datetime, random, requests
from typing import Dict, Optional, Tuple

# ------------------ CONFIG / CREDS --------------------
with open("config/credentials.json") as f:
    cfg = json.load(f)

MODE   = cfg.get("mode", "production").lower()
if MODE == "production":
    TOKEN = cfg.get("access_token")  
else:
    TOKEN = cfg.get("sandbox_access_token")
if not TOKEN:
    raise SystemExit("Missing access token in config/credentials.json")

API_BASE = "https://api-sandbox.upstox.com" if MODE == "sandbox" else "https://api.upstox.com"
HEADERS  = {"Authorization": f"Bearer {TOKEN}", "Accept": "application/json", "Content-Type": "application/json"}

# -------- Strategy params ----------------------------
STOPLOSS_PCT  = 21.0
POLL_INTERVAL = 1 if MODE == "sandbox" else 5
ENTRY_HH, ENTRY_MM = 10, 30       # 10:30 AM IST ✅
EXIT_HH,  EXIT_MM  = 15, 25      # 15:20 IST ✅
LOCK_STEP  = 5000                  # trail 5k for every +5k ✅
LOCK_ARM   = 5000                  # arm at first +5k ✅
NIFTY_INSTRUMENT_KEY = "NSE_INDEX|Nifty 50"

# Sandbox knobs
SANDBOX_SIM_SEED = 42
SANDBOX_SIM_START_SPOT = 24500.0
SANDBOX_SIM_LOT_SIZE   = 75
SANDBOX_SIM_BASE_PREMIUM = 200
SANDBOX_SIM_SPOT_SIGMA   = 6.0
SANDBOX_SIM_OPT_DELTA_SENS = 0.5
SANDBOX_SIM_THETA_DECAY    = 0.20
SANDBOX_SIM_MIN_PREMIUM    = 0.5
SANDBOX_SIM_VERBOSE        = True

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

# ----------------- Utility ----------------------------
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

def this_or_next_tuesday_date_iso():
    """Return this Tuesday (today if Tuesday), else next Thursday. ✅"""
    today = now_ist().date()
    days_ahead = (1 - today.weekday()) % 7   # Mon=0
    return (today + datetime.timedelta(days=days_ahead)).isoformat()

def round_nearest_50(x: float) -> int: 
    return int(round(x/50.0)*50)

def compute_sl_price_for_sold(entry: float, pct: float) -> float:
    today = datetime.date.today().weekday()  # Monday=0, Tuesday=1, ...
    if today == 1:  # Tuesday
        return round(entry + 30, 1)
    else:
        return round(entry * (1 + pct / 100.0), 1)

def extract_order_id(resp: dict) -> Optional[str]:
    if not resp: return None
    d = resp.get("data") or resp
    return d.get("order_id") or d.get("orderId")

# ---------- API wrappers ------------------------------
def get_ltp_for(instrument_keys) -> Dict[str,float]:
    if MODE=="sandbox": 
        raise RuntimeError("Sandbox uses simulated prices.")
    if isinstance(instrument_keys, list): 
        instrument_keys=",".join(instrument_keys)
    url=f"{API_BASE}/v3/market-quote/ltp"
    r=requests.get(url, headers=HEADERS, params={"instrument_key":instrument_keys}, timeout=10)
    r.raise_for_status()
    data = r.json().get("data",{})
    out  = {}
    for k,v in data.items(): 
        token = v.get("instrument_token") or normalize_key(k)
        out[token] = float(v.get("last_price") or v.get("ltp") or 0.0)
    return out

def get_option_chain(expiry_date_iso: str):
    if MODE=="sandbox": 
        raise RuntimeError("Sandbox has no option chain.")
    url=f"{API_BASE}/v2/option/chain"
    r=requests.get(url, headers=HEADERS, params={"instrument_key":NIFTY_INSTRUMENT_KEY,"expiry_date":expiry_date_iso}, timeout=15)
    r.raise_for_status()
    return r.json().get("data",[])

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
        payload["price"]=round(trig+5,1)  # small offset ✅
    r=requests.post(url, headers=HEADERS, json=payload, timeout=20)
    r.raise_for_status()
    return r.json()

def get_order_details(oid:str):
    if MODE=="sandbox": 
        raise RuntimeError("Sandbox no order details")
    url=f"{API_BASE}/v2/order/details"
    r=requests.get(url, headers=HEADERS, params={"order_id":oid}, timeout=10)
    r.raise_for_status()
    return r.json()

def cancel_order(oid: str):
    if MODE == "sandbox":
        print(f"[SIM] Cancel order {oid}")
        return {"status": "success", "order_id": oid}

    url = f"https://api-hft.upstox.com/v3/order/cancel"
    r = requests.delete(url, headers=HEADERS, params={"order_id": oid}, timeout=10)
    r.raise_for_status()
    return r.json()

# ----------------- Sandbox simulators -----------------
class PriceSimulator:
    def __init__(self, spot0:float, strike:int, ce:str, pe:str):
        random.seed(SANDBOX_SIM_SEED)
        self.spot=spot0; self.prev_spot=spot0
        self.strike=strike; self.ce_token=ce; self.pe_token=pe
        self.ce=float(SANDBOX_SIM_BASE_PREMIUM); self.pe=float(SANDBOX_SIM_BASE_PREMIUM)
    def tick(self)->Dict[str,float]:
        self.prev_spot=self.spot
        self.spot+=random.gauss(0,SANDBOX_SIM_SPOT_SIGMA)
        dS=self.spot-self.prev_spot
        self.ce=max(SANDBOX_SIM_MIN_PREMIUM,self.ce+SANDBOX_SIM_OPT_DELTA_SENS*dS-SANDBOX_SIM_THETA_DECAY)
        self.pe=max(SANDBOX_SIM_MIN_PREMIUM,self.pe-SANDBOX_SIM_OPT_DELTA_SENS*dS-SANDBOX_SIM_THETA_DECAY)
        if SANDBOX_SIM_VERBOSE: 
            print(f"[SIM] Spot {self.prev_spot:.1f}->{self.spot:.1f} CE={self.ce:.2f} PE={self.pe:.2f}")
        return {"SPOT":round(self.spot,1),
                self.ce_token:round(self.ce,1),
                self.pe_token:round(self.pe,1)}

def build_sandbox_chain(expiry_iso:str, spot:float)->Tuple[str,str,int]:
    atm=round_nearest_50(spot)
    ce=f"SIM|CE_ATM_{atm}"         # distinct tokens ✅
    pe=f"SIM|PE_ATM_{atm}"
    lot=SANDBOX_SIM_LOT_SIZE
    print(f"[SIM] Built sandbox chain ATM {atm}: CE={ce} PE={pe} lot={lot}")
    return ce,pe,lot

# ----------------- Helpers for P&L --------------------
def record_close_and_realized(state, leg, qty, ltp_for_close=None, close_order_id=None):
    exit_px=None
    if MODE!="sandbox" and close_order_id:
        try:
            time.sleep(0.5)
            od=get_order_details(close_order_id).get("data") or {}
            exit_px=float(od.get("average_price") or 0.0)
        except Exception:
            exit_px=None
    if exit_px is None: 
        exit_px=float(ltp_for_close) if ltp_for_close else float(state[leg]["sl_trigger"])
    realized=(state[leg]["entry"]-exit_px)*qty
    state[leg]["realized"]=realized
    state[leg]["close_price"]=exit_px
    state[leg]["open"]=False

# ----------------- Core flow ----------------------------
def run_short_straddle(wait_for_entry=False):
    print("MODE:",MODE)
    expiry_iso=this_or_next_tuesday_date_iso()     # ✅
    print("Target expiry:",expiry_iso)
    if wait_for_entry: 
        print(f"Waiting until {ENTRY_HH:02d}:{ENTRY_MM:02d} IST...")
        wait_until_ist(ENTRY_HH,ENTRY_MM)

    if MODE=="sandbox":
        spot=SANDBOX_SIM_START_SPOT
        ce,pe,lot=build_sandbox_chain(expiry_iso,spot)
        simulator=PriceSimulator(spot,round_nearest_50(spot),ce,pe)
    else:
        spot_map=get_ltp_for(NIFTY_INSTRUMENT_KEY)
        spot=safe_get(spot_map,NIFTY_INSTRUMENT_KEY)
        if not spot: 
            raise SystemExit("Failed to get NIFTY spot LTP")
        chain=get_option_chain(expiry_iso)
        atm=round_nearest_50(spot); ce=pe=lot=None
        for item in chain:
            if int(item.get("strike_price") or item.get("strike",0))!=atm: 
                continue
            if item.get("call_options") and not ce: 
                ce = normalize_key(item["call_options"].get("instrument_key")); lot=item.get("lot_size")
            if item.get("put_options") and not pe: 
                pe = normalize_key(item["put_options"].get("instrument_key")); lot=item.get("lot_size")
        if not ce or not pe: 
            raise SystemExit(f"No CE/PE tokens for {atm}")

    print("NIFTY spot:",spot); print("CE:",ce,"PE:",pe)
    qty=int(lot)*4 if lot else 300
    print("Qty per leg:",qty)

    # Entry legs
        # --- Entry Legs ---
    if MODE == "sandbox":
        # Simulated SELL orders (no API call)
        ce_oid, pe_oid = f"SIM_CE_{random.randint(1000,9999)}", f"SIM_PE_{random.randint(1000,9999)}"
        ltp_map = simulator.tick()
        ce_entry, pe_entry = float(ltp_map.get(ce)), float(ltp_map.get(pe))
        print(f"[SIM ORDER] SELL {ce} x{qty} @ {ce_entry}, oid={ce_oid}")
        print(f"[SIM ORDER] SELL {pe} x{qty} @ {pe_entry}, oid={pe_oid}")
    else:
        # Real API orders
        resp_ce = place_order(ce, "SELL", qty, "MARKET", "D")
        time.sleep(0.3)
        resp_pe = place_order(pe, "SELL", qty, "MARKET", "D")
        ce_oid, pe_oid = extract_order_id(resp_ce), extract_order_id(resp_pe)
        print("CE oid:", ce_oid, "PE oid:", pe_oid)

        # Try fetching actual fill prices
        time.sleep(1)
        try:
            ce_entry = float((get_order_details(ce_oid).get("data") or {}).get("average_price", 0.0))
            pe_entry = float((get_order_details(pe_oid).get("data") or {}).get("average_price", 0.0))
        except:
            ltp_map = get_ltp_for([ce, pe])
            ce_entry, pe_entry = safe_get(ltp_map, ce), safe_get(ltp_map, pe)

    print("CE entry:", ce_entry, "PE entry:", pe_entry)

     # --- Stop-loss Orders ---
    ce_sl = compute_sl_price_for_sold(ce_entry, STOPLOSS_PCT)
    pe_sl = compute_sl_price_for_sold(pe_entry, STOPLOSS_PCT)

    if MODE == "sandbox":
        # Simulated SL orders
        ce_sl_oid = f"SIM_SL_CE_{random.randint(1000,9999)}"
        pe_sl_oid = f"SIM_SL_PE_{random.randint(1000,9999)}"
        print(f"[SIM SL ORDER] BUY {ce} x{qty} @ trigger={ce_sl}, oid={ce_sl_oid}")
        print(f"[SIM SL ORDER] BUY {pe} x{qty} @ trigger={pe_sl}, oid={pe_sl_oid}")
    else:
        # Real SL orders
        ce_sl_oid = extract_order_id(place_order(ce, "BUY", qty, "SL", "D", trigger_price=ce_sl))
        pe_sl_oid = extract_order_id(place_order(pe, "BUY", qty, "SL", "D", trigger_price=pe_sl))
        print("CE SL price:", ce_sl, "PE SL price:", pe_sl)
        print("CE SL oid:", ce_sl_oid, "PE SL oid:", pe_sl_oid)

    state={"CE":{"token":ce,"entry":ce_entry,"sl_trigger":ce_sl,"open":True,"order_id":ce_oid,"sl_order_id":ce_sl_oid,"realized":0.0,"close_price":None},
           "PE":{"token":pe,"entry":pe_entry,"sl_trigger":pe_sl,"open":True,"order_id":pe_oid,"sl_order_id":pe_sl_oid,"realized":0.0,"close_price":None}}
    trail={"armed":False,"locked_min":0,"last_step_reached":0}
    print("Entering monitoring loop...")

    while state["CE"]["open"] or state["PE"]["open"]:
        t=now_ist()
        if (t.hour,t.minute)>=(EXIT_HH,EXIT_MM):
            print("Time exit. Closing...")
            if MODE == "sandbox":
                if state["CE"]["open"]: record_close_and_realized(state, "CE", qty, ltp_for_close=ce_ltp)
                if state["PE"]["open"]: record_close_and_realized(state, "PE", qty, ltp_for_close=pe_ltp)
            else:
                for leg in ("CE","PE"):
                    if state[leg]["open"]:
                        resp=place_order(state[leg]["token"],"BUY",qty,"MARKET","D")
                        cancel_order(state[leg]["sl_order_id"])
                        record_close_and_realized(state,leg,qty,ltp_for_close=None,close_order_id=extract_order_id(resp))
            break

        try:
            ltp_map=simulator.tick() if MODE=="sandbox" else get_ltp_for([state["CE"]["token"],state["PE"]["token"]])
            ce_ltp,pe_ltp=safe_get(ltp_map,state["CE"]["token"]),safe_get(ltp_map,state["PE"]["token"])

            # --- SL checks ---
            for leg,ltp in (("CE",ce_ltp),("PE",pe_ltp)):
                if not state[leg]["open"]: 
                    continue
                if ltp is None: 
                    print(f"No LTP {leg}"); continue
                if float(ltp)>=float(state[leg]["sl_trigger"]):
                    print(f"[SL] ❌ {leg} SL hit at {ltp}. Closing position...")
                    try:
                        record_close_and_realized(state,leg,qty,ltp_for_close=ltp)
                    except: 
                        record_close_and_realized(state,leg,qty,ltp_for_close=ltp)
                    print(f"[SL] {leg} realized P&L = {state[leg]['realized']}")
                    # Move other leg SL to cost
                    other="PE" if leg=="CE" else "CE"
                    if state[other]["open"]:
                        try:
                            if state[other]["sl_order_id"]:
                                cancel_order(state[other]["sl_order_id"])
                        except Exception as e:
                            print("Cancel SL (other leg) failed:", e)
                        try:
                            resp=place_order(state[other]["token"],"BUY",qty,"SL","D",
                                             trigger_price=float(state[other]["entry"]))
                            state[other]["sl_order_id"]=extract_order_id(resp)
                            state[other]["sl_trigger"]=float(state[other]["entry"])
                            print(f"[SL] 👉 {other} SL moved to COST at {state[other]['sl_trigger']}")
                        except Exception as e: 
                            print("Re-placing SL at cost failed:", e)

            # --- Basket P&L ---
            unreal=0.0
            if state["CE"]["open"] and ce_ltp is not None: 
                unreal+=(state["CE"]["entry"]-ce_ltp)*qty
            if state["PE"]["open"] and pe_ltp is not None: 
                unreal+=(state["PE"]["entry"]-pe_ltp)*qty
            realized=state["CE"]["realized"]+state["PE"]["realized"]
            pnl=round(realized+unreal,1)

            print(f"[PnL] Basket P&L = {pnl} (Realized={realized}, Unrealized={unreal})")

            # --- Lock & Trail (₹5k for every +₹5k) ✅ ---
            if not trail["armed"] and pnl>=LOCK_ARM:
                trail["armed"]=True
                trail["last_step_reached"]=(pnl//LOCK_STEP)*LOCK_STEP
                step=int(trail["last_step_reached"])
                trail["locked_min"]=max(0, step-LOCK_STEP)
                print(f"[Lock&Trail] 🚀 Armed at P&L {pnl}. Initial lock = {trail['locked_min']}")
            if trail["armed"]:
                step=int(pnl//LOCK_STEP)*LOCK_STEP
                if step>trail["last_step_reached"]:
                    trail["last_step_reached"]=step
                    trail["locked_min"]=max(0, step-LOCK_STEP)
                    print(f"[Lock&Trail] 🔒 Trail advanced → Step={step}, Locked={trail['locked_min']}")
                if pnl<=trail["locked_min"] and (state["CE"]["open"] or state["PE"]["open"]):
                    print(f"[Lock&Trail] ❌ Exit triggered. Current P&L={pnl}, Locked={trail['locked_min']}")
                    for leg,ltp in (("CE",ce_ltp),("PE",pe_ltp)):
                        if state[leg]["open"]:
                            try:
                                cancel_order(state[leg]["sl_order_id"])
                                resp=place_order(state[leg]["token"],"BUY",qty,"MARKET","D")
                                print(f"[Trail Exit] Cancelled SL for {leg} ({state[leg]['sl_order_id']})")
                                record_close_and_realized(state,leg,qty,ltp_for_close=ltp,
                                                          close_order_id=extract_order_id(resp))
                            except: 
                                record_close_and_realized(state,leg,qty,ltp_for_close=ltp)
                    break

        except Exception as e: 
            print("Error:", e)
        time.sleep(POLL_INTERVAL)

    print("All legs closed.")
    print("Final realized P&L:", state["CE"]["realized"]+state["PE"]["realized"])
    print("Details:",state)

# --------------- main ---------------
if __name__=="__main__":
    run_short_straddle(wait_for_entry=True)
