import threading
import time
from SmartApi import smartWebSocketV2

class AngelWSManager:
    def __init__(self, api_key, client_code, auth_token, feed_token, ltp_map):
        self.api_key = api_key
        self.client_code = client_code
        self.auth_token = auth_token
        self.feed_token = feed_token
        self.ltp_map = ltp_map

        self.ws = None
        self.connected = False
        self.lock = threading.Lock()

    # ---------------- CALLBACKS ---------------- #

    def on_open(self, wsapp):
        print("✅ WS OPENED")
        self.connected = True

    def on_error(self, wsapp, error):
        print("❌ WS ERROR:", error)

    def on_close(self, wsapp):
        print("🔌 WS CLOSED")
        self.connected = False

    def on_data(self, wsapp, message):
        try:
            token = message["token"]
            ltp = message["last_traded_price"] / 100
            self.ltp_map[token] = ltp
        except Exception:
            pass

    # ---------------- START ---------------- #

    def start(self):
        self.ws = smartWebSocketV2.SmartWebSocketV2(
            auth_token=self.auth_token,
            api_key=self.api_key,
            client_code=self.client_code,
            feed_token=self.feed_token
        )

        self.ws.on_open = self.on_open
        self.ws.on_error = self.on_error
        self.ws.on_close = self.on_close
        self.ws.on_data = self.on_data

        threading.Thread(target=self.ws.connect, daemon=True).start()

        # wait for socket to be ready
        timeout = time.time() + 10
        while not self.connected:
            if time.time() > timeout:
                raise RuntimeError("WS connection timeout")
            time.sleep(0.1)

    # ---------------- SUBSCRIBE ---------------- #

    def subscribe_index(self, index_token):
        self._subscribe([
            {
                "exchangeType": 1,  # NSE_CM
                "tokens": [index_token]
            }
        ])

    def subscribe_options(self, option_tokens):
        self._subscribe([
            {
                "exchangeType": 2,  # NSE_FO
                "tokens": option_tokens
            }
        ])

    def _subscribe(self, token_list):
        with self.lock:
            self.ws.subscribe(
                correlation_id="straddle",
                mode=1,  # LTP
                token_list=token_list
            )
            print("Subscribed to tokens:", token_list)