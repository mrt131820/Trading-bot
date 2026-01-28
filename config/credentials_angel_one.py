import os

credentials = {
  "api_key": os.getenv("API_KEY"),
  "client_code": os.getenv("CLIENT_CODE"),
  "password": os.getenv("PASSWORD"),
  "totp_secret": os.getenv("TOTP_SECRET")
}
