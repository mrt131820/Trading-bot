import os

credentials = {
  "client_id": os.getenv("CLIENT_ID", "xxxx"),
  "client_secret": os.getenv("CLIENT_SECRET"),
  "redirect_uri": os.getenv("REDIRECT_URI"),
  "refresh_token": os.getenv("REFRESH_TOKEN"),
  "access_token": os.getenv("TOKEN"),
  "sandbox_client_id": os.getenv("SANDBOX_CLIENT_ID"),
  "sandbox_client_secret": os.getenv("SANDBOX_CLIENT_SECRET"),
  "sandbox_redirect_uri": os.getenv("SANDBOX_REDIRECT_URI"),
  "sandbox_code": os.getenv("SANDBOX_CODE"),
  "sandbox_access_token": os.getenv("SANDBOX_ACCESS_TOKEN"),
  "mode": os.getenv("MODE", "sandbox")  # Change to "production" for live trading
}