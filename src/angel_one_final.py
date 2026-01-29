from SmartApi import smartConnect, smartWebSocketV2
from config.credentials_angel_one import credentials
from .ws_manager import AngelWSManager
import pyotp, time, datetime, pytz, json

# =============================
# TIMEZONE (MANDATORY FOR GITHUB ACTIONS)
# =============================
IST = pytz.timezone("Asia/Kolkata")

def now_ist():
    return datetime.datetime.now(IST)

# =============================
# USER CONFIGURATION
# =============================
API_KEY = credentials["api_key"]
CLIENT_CODE = credentials["client_code"]
PASSWORD = credentials["password"]
TOTP_SECRET = credentials["totp_secret"]

MODE = "production"  # or "sandbox"

STOPLOSS_PCT  = 21.0
ENTRY_HH, ENTRY_MM = 10, 30
EXIT_HH, EXIT_MM   = 15, 25

LOCK_STEP = 1000
LOCK_ARM  = 1000

INDEX_TOKEN = "99926000"   # NIFTY
INDEX_NAME  = "NIFTY"

LOT_MULTIPLIER = 1

# =============================
# LOGIN
# =============================
obj = smartConnect.SmartConnect(api_key=API_KEY)
session = obj.generateSession(
    CLIENT_CODE,
    PASSWORD,
    pyotp.TOTP(TOTP_SECRET).now()
)
token = session['data']['jwtToken']
feedToken = session['data']['feedToken']

# =============================
# LOAD INSTRUMENT MASTER
# =============================
def load_instruments(path="instruments.json"):
    with open(path, "r") as f:
        data = json.load(f)

    instruments = []
    for r in data:
        if r.get("exch_seg") != "NFO":
            continue
        if r.get("instrumenttype") != "OPTIDX":
            continue
        if r.get("name") != INDEX_NAME:
            continue

        instruments.append({
            "symbol": r["symbol"],
            "token": r["token"],
            "name": r["name"],
            "expiry": r["expiry"],       
            "strike": int(float(r["strike"])) // 100, 
            "lotsize": int(r["lotsize"]),
        })
    return instruments

INSTRUMENTS = load_instruments()

# =============================
# AUTO WEEKLY EXPIRY
# =============================
def get_weekly_expiry(index_name, instruments):
    today = datetime.date.today()

    def parse_exp(e):
        return datetime.datetime.strptime(e, "%d%b%Y").date()

    expiries = sorted(
        {i["expiry"] for i in instruments if i["name"] == index_name},
        key=parse_exp
    )

    for e in expiries:
        if parse_exp(e) >= today:
            return e

    raise RuntimeError("No valid expiry found")

# =============================
# WEBSOCKET
# =============================
ltp_map = {}

# =============================
# HELPERS
# =============================
def round_nearest_50(x):
    return int(round(x / 50) * 50)

def get_atm_strike():
    while INDEX_TOKEN not in ltp_map:
        time.sleep(0.5)
    return round_nearest_50(ltp_map[INDEX_TOKEN])

def get_option_tokens(atm_strike, expiry, instruments):
    strikes = sorted({
        i["strike"]
        for i in instruments
        if i["expiry"] == expiry
    })

    if not strikes:
        raise RuntimeError("No strikes found for expiry")

    selected_strike = min(strikes, key=lambda x: abs(x - atm_strike))

    ce = pe = None
    for row in instruments:
        if row["strike"] == selected_strike and row["expiry"] == expiry:
            if row["symbol"].endswith("CE"):
                ce = row
            elif row["symbol"].endswith("PE"):
                pe = row

    if not ce or not pe:
        raise RuntimeError(f"CE/PE not found for strike {selected_strike}")

    print(f"Using strike {selected_strike} (ATM approx {atm_strike})")
    return ce, pe


def place_order(token, symbol, side, qty, sl=None):
    order = {
        "variety": "STOPLOSS" if sl else "NORMAL",
        "tradingsymbol": symbol,
        "symboltoken": token,
        "exchange": "NFO",
        "transactiontype": side,
        "ordertype": "MARKET" if not sl else "STOPLOSS_LIMIT",
        "producttype": "INTRADAY",
        "duration": "DAY",
        "quantity": qty
    }
    if sl:
        order["triggerprice"] = round(sl, 1)
        order["price"] = round(sl + 5, 1)

    return obj.placeOrder(order)

# =============================
# STRATEGY
# =============================
def run_short_straddle():
    while datetime.datetime.now().time() < datetime.time(ENTRY_HH, ENTRY_MM):
        time.sleep(5)

    ws = AngelWSManager(
    api_key=API_KEY,
    client_code=CLIENT_CODE,
    auth_token=token,
    feed_token=feedToken,
    ltp_map=ltp_map
    )

    ws.start()
    ws.subscribe_index(INDEX_TOKEN)


    print("Waiting till", ENTRY_HH, ENTRY_MM)
    while datetime.datetime.now().time() < datetime.time(ENTRY_HH, ENTRY_MM):
        time.sleep(5)

    strike = get_atm_strike()
    print("ATM Strike:", strike)

    expiry = get_weekly_expiry(INDEX_NAME, INSTRUMENTS)
    print("Using Expiry:", expiry)

    ce, pe = get_option_tokens(strike, expiry, INSTRUMENTS)
    ce_token, pe_token = ce["token"], pe["token"]

    ws.subscribe_options([ce_token, pe_token])

    while ce_token not in ltp_map or pe_token not in ltp_map:
        time.sleep(0.5)

    qty = ce["lotsize"] * LOT_MULTIPLIER

    # ENTRY
    place_order(ce_token, ce["symbol"], "SELL", qty)
    place_order(pe_token, pe["symbol"], "SELL", qty)

    time.sleep(1)

    ce_entry = ltp_map[ce_token]
    pe_entry = ltp_map[pe_token]

    ce_sl = max(ce_entry * (1 + STOPLOSS_PCT / 100), ce_entry+30)
    pe_sl = max(pe_entry * (1 + STOPLOSS_PCT / 100), pe_entry+30)

    ce_sl_order = place_order(
    ce_token,
    ce["symbol"],
    "BUY",
    qty,
    sl=ce_sl
    )

    pe_sl_order = place_order(
    pe_token,
    pe["symbol"],
    "BUY",
    qty,
    sl=pe_sl
    )

    print("Exchange SL placed:",
      "CE SL @", round(ce_sl, 1),
      "PE SL @", round(pe_sl, 1))

    state = {
        "CE": {
            "entry": ce_entry,
            "sl": ce_sl,
            "sl_order": ce_sl_order,
            "open": True
        },
         "PE": {
            "entry": pe_entry,
            "sl": pe_sl,
            "sl_order": pe_sl_order,
            "open": True
        },
    }


    trail = {"armed": False, "locked": 0}

    while state["CE"]["open"] or state["PE"]["open"]:
        if datetime.datetime.now().time() >= datetime.time(EXIT_HH, EXIT_MM):
            break

        ce_ltp = ltp_map.get(ce_token)
        print("CE LTP:", ce_ltp)
        pe_ltp = ltp_map.get(pe_token)
        print("PE LTP:", pe_ltp)

        if state["CE"]["open"] and ce_ltp >= state["CE"]["sl"]:
            state["CE"]["open"] = False
            print("CE SL hit")

            # ❗ Cancel PE SL and move to cost
            obj.cancelOrder(state["PE"]["sl_order"], "STOPLOSS")
            new_sl = state["PE"]["entry"]

            pe_sl_order = place_order(
                pe_token,
                pe["symbol"],
                "BUY",
                qty,
                sl=new_sl
            )

            state["PE"]["sl"] = new_sl
            state["PE"]["sl_order"] = pe_sl_order

        if state["PE"]["open"] and pe_ltp >= state["PE"]["sl"]:
            state["PE"]["open"] = False
            print("PE SL hit")

            # ❗ Cancel CE SL and move to cost
            obj.cancelOrder(state["CE"]["sl_order"], "STOPLOSS")
            new_sl = state["CE"]["entry"]

            ce_sl_order = place_order(
                ce_token,
                ce["symbol"],
                "BUY",
                qty,
                sl=new_sl
            )

            state["CE"]["sl"] = new_sl
            state["CE"]["sl_order"] = ce_sl_order

        unreal = 0
        if state["CE"]["open"]:
            unreal += (state["CE"]["entry"] - ce_ltp) * qty
        if state["PE"]["open"]:
            unreal += (state["PE"]["entry"] - pe_ltp) * qty

        if not trail["armed"] and unreal >= LOCK_ARM:
            trail["armed"] = True
            trail["locked"] = unreal - LOCK_STEP

        if trail["armed"] and unreal <= trail["locked"]:
            if state["CE"]["open"]:
                obj.cancelOrder(state["CE"]["sl_order"], "STOPLOSS")
            if state["PE"]["open"]:
                obj.cancelOrder(state["PE"]["sl_order"], "STOPLOSS")
            break

        time.sleep(1)

    if state["CE"]["open"]:
        obj.cancelOrder(state["CE"]["sl_order"], "STOPLOSS")
        place_order(ce_token, ce["symbol"], "BUY", qty)
    if state["PE"]["open"]:
        obj.cancelOrder(state["PE"]["sl_order"], "STOPLOSS")
        place_order(pe_token, pe["symbol"], "BUY", qty)

    print("Strategy complete")

# =============================
# RUN
# =============================
if __name__ == "__main__":
    run_short_straddle()
