#!/usr/bin/env python3
"""
Production short-straddle bot for NIFTY weekly:
- Sell ATM CE and PE (closest 50)
- Place 20% SL for each sold leg (SL = entry * 1.20)
- If one leg's SL hits: buy-to-close that leg and modify the other leg's SL to its entry (move SL to cost)
"""

import json
import time
import datetime
import requests
from typing import Dict, Optional

# ------------------ CONFIG / CREDS --------------------
with open("config/credentials.json") as f:
    cfg = json.load(f)

MODE = cfg.get("mode", "production").lower()
TOKEN = cfg.get("access_token") if MODE == "production" else cfg.get("sandbox_access_token")
if not TOKEN:
    raise SystemExit("Missing access token in config/credentials.json")

API_BASE = "https://api-sandbox.upstox.com" if MODE == "sandbox" else "https://api.upstox.com"
HEADERS = {"Authorization": f"Bearer {TOKEN}", "Accept": "application/json", "Content-Type": "application/json"}

# Strategy params
STOPLOSS_PCT = 20.0   # percent
POLL_INTERVAL = 5     # seconds
# NIFTY underlying instrument key:
NIFTY_INSTRUMENT_KEY = "NSE_INDEX|Nifty 50"

# ---------- Helper functions (API wrappers) -----------
def get_ltp_for(instrument_keys: str) -> Dict[str, float]:
    """Call /v2/market-quote/ltp?instrument_key=<comma-separated>"""
    url = f"{API_BASE}/v2/market-quote/ltp"
    resp = requests.get(url, headers=HEADERS, params={"instrument_key": instrument_keys}, timeout=10)
    resp.raise_for_status()
    data = resp.json().get("data", {})
    print("LTP Raw Data:", data) 
    out = {}
    for k, v in data.items():
        # last_price key may be named last_price or ltp depending on payload
        lp = v.get("last_price") or v.get("ltp") or v.get("lastPrice") or 0.0
        normalized_key = k.replace(":", "|")
        out[normalized_key] = float(lp)
    return out

def get_option_chain(expiry_date_iso: str):
    """
    Call PUT/GET the option chain for NIFTY for a given expiry date.
    Endpoint: GET /v2/option/chain?instrument_key=<>&expiry_date=YYYY-MM-DD
    """
    url = f"{API_BASE}/v2/option/chain"
    params = {"instrument_key": NIFTY_INSTRUMENT_KEY, "expiry_date": expiry_date_iso}
    r = requests.get(url, headers=HEADERS, params=params, timeout=15)
    r.raise_for_status()
    return r.json().get("data", [])


def place_order(instrument_token: str, transaction_type: str, quantity: int, order_type: str = "MARKET", product: str = "I", price: float = 0.0, trigger_price: Optional[float] = None):
    """
    POST /v2/order/place
    Returns JSON.
    """
    url = f"{API_BASE}/v2/order/place"
    payload = {
       "quantity": quantity,
        "product": product,
        "validity": "DAY",
        "price": price,
        "instrument_token": instrument_token,
        "order_type": order_type,
        "transaction_type": transaction_type,
        "disclosed_quantity": 0,
        "trigger_price": 0,
        "is_amo": False               
    }
    if trigger_price is not None:
        payload["trigger_price"] = trigger_price
        payload["price"] = round(trigger_price + 5, 1)

    try:
        r = requests.post(url, headers=HEADERS, json=payload, timeout=20)
        r.raise_for_status()
        return r.json()
    except requests.exceptions.HTTPError as e:
        print("Order placement failed!")
        print("Payload sent:", payload)
        print("Status code:", r.status_code)
        print("Response text:", r.text)
        raise

def get_order_details(order_id: str):
    """GET /v2/order/details?order_id=..."""
    url = f"{API_BASE}/v2/order/details"
    r = requests.get(url, headers=HEADERS, params={"order_id": order_id}, timeout=10)
    r.raise_for_status()
    return r.json()

def modify_order(payload: Dict):
    """PUT /v2/order/modify with payload (must include order_id)"""
    url = f"{API_BASE}/v2/order/modify"
    r = requests.put(url, headers=HEADERS, json=payload, timeout=15)
    r.raise_for_status()
    return r.json()

# ----------------- Utility ---------------------------
def next_thursday_date_iso():
    today = datetime.date.today()
    days_ahead = 3 - today.weekday()  # Thursday=3
    if days_ahead <= 0:
        days_ahead += 7
    nxt = today + datetime.timedelta(days_ahead)
    return nxt.isoformat()  # YYYY-MM-DD

def round_nearest_50(x: float) -> int:
    # careful arithmetic: round to nearest 50
    return int(round(x / 50.0) * 50)

def compute_sl_price_for_sold(entry_price: float, pct: float) -> float:
    return round(entry_price * (1 + pct/100.0), 2)

def extract_order_id(place_resp: dict) -> Optional[str]:
    # common shapes: { "data": { "order_id": "..." } } or { "order_id": "..." }
    if not place_resp:
        return None
    if isinstance(place_resp, dict):
        d = place_resp.get("data") or place_resp
        return d.get("order_id") or d.get("orderId") or d.get("order_id")
    return None

# --------------- Core flow --------------------------
def run_prod_short_straddle():
    print("MODE:", MODE)
    expiry_iso = next_thursday_date_iso()
    print("Target expiry:", expiry_iso)

    # 1) Get spot LTP for NIFTY
    spot_map = get_ltp_for(NIFTY_INSTRUMENT_KEY)
    spot = spot_map.get(NIFTY_INSTRUMENT_KEY)
    if not spot:
        raise SystemExit("Failed to get NIFTY spot LTP")
    print("NIFTY spot:", spot)

    # ATM strike (nearest 50)
    atm_strike = round_nearest_50(spot)
    print("ATM strike (nearest 50):", atm_strike)

    # 2) Fetch option chain for that expiry and find CE & PE instrument_token for ATM strike
    chain = get_option_chain(expiry_iso)
    if not chain:
        raise SystemExit("No option chain returned (API might not support or expiry mismatch)")

    # chain entries expected to contain fields: strike, option_type ('CE'/'PE'), instrument_token (e.g. 'NSE_FO|12345'), lot_size etc.
    ce_token = pe_token = None
    lot_size = None
    for item in chain:
        # item may contain 'strike', 'option_type', 'instrument_key' (or 'instrument_token')
        strike = item.get("strike_price") or item.get("strike") or item.get("strikePrice")
        if strike is None or int(strike) != int(atm_strike):
            continue

        call_opt = item.get("call_options")
        put_opt = item.get("put_options")

        if call_opt and not ce_token:
            ce_token = call_opt.get("instrument_key") or call_opt.get("instrument_token") or call_opt.get("instrumentKey")
            lot_size = lot_size or item.get("lot_size") or item.get("lotSize") or item.get("contract_size")

        if put_opt and not pe_token:
            pe_token = put_opt.get("instrument_key") or put_opt.get("instrument_token") or put_opt.get("instrumentKey")
            lot_size = lot_size or item.get("lot_size") or item.get("lotSize") or item.get("contract_size")

    if not ce_token or not pe_token:
        raise SystemExit(f"Could not find CE/PE tokens for strike {atm_strike}. Check option chain keys or instrument formats.")

    print("CE token:", ce_token, "PE token:", pe_token, "Lot size:", lot_size)

    quantity = int(lot_size) if lot_size else 75  # default 50 if not provided
    print("Order quantity (per leg):", quantity)

    # 3) Place SELL market orders for CE & PE
    print("Placing SELL MARKET for CE...")
    resp_ce = place_order(ce_token, transaction_type="SELL", quantity=quantity, order_type="MARKET", product="I")
    time.sleep(0.3)
    print("Placing SELL MARKET for PE...")
    resp_pe = place_order(pe_token, transaction_type="SELL", quantity=quantity, order_type="MARKET", product="I")

    ce_order_id = extract_order_id(resp_ce)
    pe_order_id = extract_order_id(resp_pe)
    print("CE order id:", ce_order_id, "PE order id:", pe_order_id)

    # 4) Wait briefly then fetch executed avg prices from order details
    time.sleep(1)
    ce_details = get_order_details(ce_order_id) if ce_order_id else {}
    pe_details = get_order_details(pe_order_id) if pe_order_id else {}

    # average price field may be avg_price, average_price, executed_price etc.
    def avg_price_from(od):
        d = od.get("data") or od
        return float(d.get("average_price") or d.get("avg_price") or d.get("averagePrice") or d.get("price") or 0.0)

    ce_entry = avg_price_from(ce_details)
    pe_entry = avg_price_from(pe_details)
    if not ce_entry or not pe_entry:
        # fallback to LTP if avg price not returned
        ltp_map = get_ltp_for(f"{ce_token},{pe_token}")
        ce_entry = ce_entry or ltp_map.get(ce_token)
        pe_entry = pe_entry or ltp_map.get(pe_token)

    print("CE entry:", ce_entry, "PE entry:", pe_entry)

    # 5) Place SL BUY (protective) orders for each leg at entry * (1 + STOPLOSS_PCT)
    ce_sl_trigger = compute_sl = round(ce_entry * (1 + STOPLOSS_PCT / 100.0), 2)
    pe_sl_trigger = round(pe_entry * (1 + STOPLOSS_PCT / 100.0), 2)
    print(f"Placing initial SL-BUY orders: CE SL @ {ce_sl_trigger}, PE SL @ {pe_sl_trigger}")

    # Place SL BUY orders (order_type='SL' and trigger_price set)
    resp_ce_sl = place_order(ce_token, transaction_type="BUY", quantity=quantity, order_type="SL", product="I", trigger_price=ce_sl_trigger)
    time.sleep(0.2)
    resp_pe_sl = place_order(pe_token, transaction_type="BUY", quantity=quantity, order_type="SL", product="I", trigger_price=pe_sl_trigger)

    ce_sl_order_id = extract_order_id(resp_ce_sl)
    pe_sl_order_id = extract_order_id(resp_pe_sl)
    print("CE SL order id:", ce_sl_order_id, "PE SL order id:", pe_sl_order_id)

    # 6) Monitor LTPs and SL order fills
    state = {
        "CE": {"token": ce_token, "entry": ce_entry, "sl_trigger": ce_sl_trigger, "open": True, "order_id": ce_order_id, "sl_order_id": ce_sl_order_id},
        "PE": {"token": pe_token, "entry": pe_entry, "sl_trigger": pe_sl_trigger, "open": True, "order_id": pe_order_id, "sl_order_id": pe_sl_order_id},
    }

    print("Entering monitoring loop. Poll interval:", POLL_INTERVAL)
    while state["CE"]["open"] or state["PE"]["open"]:
        try:
            # fetch latest LTPs
            keys = ",".join([state["CE"]["token"], state["PE"]["token"]])
            ltp_map = get_ltp_for(keys)

            # check each leg for SL hit (price >= sl_trigger)
            for leg in ["CE", "PE"]:
                if not state[leg]["open"]:
                    continue
                tok = state[leg]["token"]
                ltp = ltp_map.get(tok)
                if ltp is None:
                    # if cannot get ltp, try querying order details to see if SL order executed
                    print(f"No LTP for {leg}, attempting to check SL order fill via order details.")
                else:
                    print(f"{leg} LTP {ltp}, SL trigger {state[leg]['sl_trigger']}")
                    if ltp >= state[leg]["sl_trigger"]:
                        print(f"Detected SL condition for {leg} by LTP hitting trigger.")
                        # Ensure we haven't already closed; buy to close (market) now
                        try:
                            print(f"Buying-to-close {leg} at market...")
                            resp_close = place_order(state[leg]["token"], transaction_type="BUY", quantity=quantity, order_type="MARKET", product="I")
                            print(f"Buy-to-close response for {leg}:", resp_close)
                        except Exception as e:
                            print("Error buying to close:", e)
                        state[leg]["open"] = False

                        # Cancel the SL order if it's still open (best-effort)
                        other = "PE" if leg == "CE" else "CE"
                        try:
                            if state[leg]["sl_order_id"]:
                                print(f"Attempting to cancel SL order {state[leg]['sl_order_id']}")
                                # Cancel endpoint: /v2/order/cancel?order_id=...
                                url_cancel = f"{API_BASE}/v2/order/cancel"
                                r = requests.put(url_cancel, headers=HEADERS, json={"order_id": state[leg]["sl_order_id"]}, timeout=10)
                                print("Cancel SL response status:", r.status_code, r.text)
                        except Exception as ee:
                            print("Cancel SL failed:", ee)

                        # Modify other leg's SL order to entry price (move to cost)
                        if state[other]["open"] and state[other].get("sl_order_id"):
                            print(f"Modifying {other} SL order {state[other]['sl_order_id']} to trigger at cost {state[other]['entry']}")
                            modify_payload = {
                                "order_id": state[other]["sl_order_id"],
                                "trigger_price": float(state[other]["entry"]),
                                # optionally set price/order_type fields if needed
                                "order_type": "SL",
                                "validity": "DAY"
                            }
                            try:
                                mod_resp = modify_order(modify_payload)
                                print("Modify response:", mod_resp)
                                # also update internal sl_trigger
                                state[other]["sl_trigger"] = float(state[other]["entry"])
                            except Exception as me:
                                print("Modify order error:", me)
                        else:
                            print(f"No open SL order found for {other}, cannot modify. Consider placing a new SL-BUY at cost.")
                            # Alternatively place a fresh SL BUY at cost:
                            if state[other]["open"]:
                                try:
                                    resp_protect = place_order(state[other]["token"], transaction_type="BUY", quantity=quantity, order_type="SL", product="I", trigger_price=state[other]["entry"])
                                    print("Placed fresh protective SL-BUY at cost for other leg:", resp_protect)
                                    state[other]["sl_order_id"] = extract_order_id(resp_protect)
                                    state[other]["sl_trigger"] = state[other]["entry"]
                                except Exception as e:
                                    print("Failed to place fresh protective SL-BUY:", e)
            # small sleep
            time.sleep(POLL_INTERVAL)

        except Exception as ex:
            print("Error in monitoring loop:", ex)
            time.sleep(POLL_INTERVAL)

    print("Both legs processed. Exiting.")

# ----------------- run --------------------
if __name__ == "__main__":
    run_prod_short_straddle()
