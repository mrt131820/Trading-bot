#!/usr/bin/env python3
"""
Place ONE PROD order (SELL) for ATM NIFTY option (CE) for next weekly expiry.
Script prints discovery results and asks for CONFIRM before placing any live order.
"""

import json
import time
import datetime
import requests
from typing import Optional, Dict

# ----- Config -----
with open("config/credentials.json") as f:
    cfg = json.load(f)

MODE = cfg.get("mode", "production").lower()
TOKEN = cfg.get("access_token") if MODE == "production" else cfg.get("sandbox_access_token")
if not TOKEN:
    raise SystemExit("No access token found in config/credentials.json")

API_BASE = "https://api-sandbox.upstox.com" if MODE == "sandbox" else "https://api.upstox.com"
HEADERS = {"Authorization": f"Bearer {TOKEN}", "Accept": "application/json", "Content-Type": "application/json"}

# Strategy helpers
def next_thursday_iso():
    today = datetime.date.today()
    days_ahead = 3 - today.weekday()  # Thursday = 3
    if days_ahead <= 0:
        days_ahead += 7
    nxt = today + datetime.timedelta(days_ahead)
    return nxt.isoformat()  # YYYY-MM-DD

def round_nearest_50(x: float) -> int:
    return int(round(x / 50.0) * 50)

# ----- API wrappers -----
def get_ltp_for(instrument_key: str) -> Optional[float]:
    url = f"{API_BASE}/v2/market-quote/ltp"
    params = {"instrument_key": instrument_key}
    r = requests.get(url, headers=HEADERS, params=params, timeout=10)
    r.raise_for_status()
    j = r.json()
    data = j.get("data", {})
    item = data.get(instrument_key)
    if not item:
        return None
    return float(item.get("last_price") or item.get("ltp") or item.get("lastPrice") or 0.0)

def get_option_chain(expiry_iso: str) -> list:
    url = f"{API_BASE}/v2/option/chain"
    params = {"instrument_key": "NSE_INDEX|Nifty 50", "expiry_date": expiry_iso}
    r = requests.get(url, headers=HEADERS, params=params, timeout=15)
    r.raise_for_status()
    return r.json().get("data", [])

def place_order(instrument_token: str, transaction_type: str, quantity: int, order_type: str = "MARKET", product: str = "I", price: float = 0.0, trigger_price: Optional[float] = None) -> dict:
    url = f"{API_BASE}/v2/order/place"
    payload = {
        "instrument_token": instrument_token,
        "transaction_type": transaction_type,  # BUY or SELL
        "quantity": quantity,
        "order_type": order_type,
        "product": product,
        "validity": "DAY",
        "price": price
    }
    if trigger_price is not None:
        payload["trigger_price"] = trigger_price
    r = requests.post(url, headers=HEADERS, json=payload, timeout=20)
    r.raise_for_status()
    return r.json()

def get_order_details(order_id: str) -> dict:
    url = f"{API_BASE}/v2/order/details"
    r = requests.get(url, headers=HEADERS, params={"order_id": order_id}, timeout=10)
    r.raise_for_status()
    return r.json()

def extract_order_id(resp: dict) -> Optional[str]:
    if not resp:
        return None
    if isinstance(resp, dict):
        d = resp.get("data") or resp
        return d.get("order_id") or d.get("orderId") or d.get("orderId")
    return None

# ----- Flow: discover ATM option instrument, show lot size, ask confirm, place 1 SELL -----
def run_one_order_flow():
    expiry_iso = next_thursday_iso()
    print("Target expiry:", expiry_iso)

    # 1) get NIFTY spot
    nifty_key = "NSE_INDEX|Nifty 50"
    spot = get_ltp_for(nifty_key)
    if spot is None:
        raise SystemExit("Failed to fetch NIFTY spot LTP. Aborting.")
    print("NIFTY spot:", spot)

    atm_strike = round_nearest_50(spot)
    print("ATM strike (nearest 50):", atm_strike)

    # 2) fetch option chain for that expiry and find ATM CE/PE instrument tokens
    chain = get_option_chain(expiry_iso)
    if not chain:
        raise SystemExit("Option chain returned empty. Check API permissions / expiry_date format.")

    ce_token = pe_token = None
    lot_size = None
    for item in chain:
        strike = item.get("strike") or item.get("strike_price") or item.get("strikePrice")
        otype = (item.get("option_type") or item.get("optionType") or "").upper()
        inst = item.get("instrument_key") or item.get("instrument_token") or item.get("instrumentKey")
        if strike is None or inst is None or not otype:
            continue
        try:
            if int(strike) == int(atm_strike):
                if "CE" in otype:
                    ce_token = inst
                    lot_size = lot_size or item.get("lot_size") or item.get("lotSize") or item.get("contract_size")
                elif "PE" in otype:
                    pe_token = inst
                    lot_size = lot_size or item.get("lot_size") or item.get("lotSize") or item.get("contract_size")
        except Exception:
            continue

    print("Discovered tokens:")
    print(" CE token:", ce_token)
    print(" PE token:", pe_token)
    print(" Lot size from chain:", lot_size)
    if not ce_token:
        raise SystemExit("CE token not found for ATM. Aborting.")

    # Choose CE (you can change to PE)
    instrument = ce_token
    qty = int(lot_size) if lot_size else 1
    print(f"\nPlacing SINGLE SELL ORDER (dry run until you CONFIRM):\nInstrument: {instrument}\nQuantity: {qty}\nOrder type: MARKET\nProduct: Intraday (I)\n")

    confirm = input("Type CONFIRM to place the SELL MARKET order (or anything else to abort): ").strip()
    if confirm != "CONFIRM":
        print("Aborted by user.")
        return

    # 3) Place SELL market order
    print("Placing SELL market order...")
    resp = place_order(instrument, transaction_type="SELL", quantity=qty, order_type="MARKET", product="I")
    print("Place order response (raw):", resp)

    order_id = extract_order_id(resp)
    print("Extracted order_id:", order_id)
    if order_id:
        print("Waiting 1s then fetching order details...")
        time.sleep(1.5)
        od = get_order_details(order_id)
        print("Order details (raw):", od)
        # Attempt to extract average/executed price
        d = od.get("data") or od
        avg_price = float(d.get("average_price") or d.get("avgPrice") or d.get("avg_price") or d.get("filled_price") or 0.0)
        status = d.get("status") or d.get("order_status") or d.get("orderStatus")
        print(f"Order status: {status}, avg/executed price: {avg_price}")
        if avg_price <= 0:
            print("Avg price not populated. Will fallback to LTP if needed.")
    else:
        print("Could not extract order id. Check response above.")

    # 4) Offer to place 20% SL-BUY protective order
    if order_id:
        # decide entry for SL calc (prefer avg_price, else fallback to LTP)
        entry_price = avg_price if avg_price and avg_price > 0 else get_ltp_for(instrument)
        if not entry_price:
            print("Cannot determine entry price for SL. Aborting SL placement.")
            return
        sl_trigger = round(entry_price * (1 + 20.0/100.0), 2)
        print(f"Computed SL trigger price (20% above entry {entry_price}): {sl_trigger}")
        confirm2 = input("Type PLACE_SL to place a protective SL-BUY order at trigger price above: ").strip()
        if confirm2 == "PLACE_SL":
            print("Placing SL-BUY protective order...")
            resp_sl = place_order(instrument, transaction_type="BUY", quantity=qty, order_type="SL", product="I", trigger_price=sl_trigger)
            print("SL order response:", resp_sl)
        else:
            print("Skipped placing SL order. You can place it manually later.")

if __name__ == "__main__":
    run_one_order_flow()
