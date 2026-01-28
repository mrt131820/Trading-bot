import os

credentials = {
  "api_key": os.getenv("API_KEY", "q2oK1kt9"),
  "client_code": os.getenv("CLIENT_CODE", "M1044520"),
  "password": os.getenv("PASSWORD", "2712"),
  "totp_secret": os.getenv("TOTP_SECRET", "WOSGISA3BB3OIW5KR732NBZXZI")
}
