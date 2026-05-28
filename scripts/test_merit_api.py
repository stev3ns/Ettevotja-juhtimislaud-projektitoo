import os
import json
import hmac
import hashlib
import base64
import requests
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv(override=True)

api_id = os.getenv("MERIT_API_ID", "").strip()
api_key = os.getenv("MERIT_API_KEY", "").strip()
base_url = os.getenv("MERIT_API_BASE_URL", "https://aktiva.merit.ee").strip()

print("Kasutatav API ID:", api_id)

if not api_id or not api_key or not base_url:
    raise SystemExit("Puudub MERIT_API_ID, MERIT_API_KEY või MERIT_API_BASE_URL .env failist.")

endpoint = "/api/v2/getpurchorders"
url = f"{base_url}{endpoint}"

payload = {
    "PeriodStart": "20260501",
    "PeriodEnd": "20260731",
    "UnPaid": False,
    "DateType": 0
}

http_body = json.dumps(payload, separators=(",", ":"), ensure_ascii=False)

timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")

data_to_sign = f"{api_id}{timestamp}{http_body}"

signature = base64.b64encode(
    hmac.new(
        api_key.encode("ascii"),
        data_to_sign.encode("utf-8"),
        hashlib.sha256
    ).digest()
).decode("utf-8")

params = {
    "apiId": api_id,
    "timestamp": timestamp,
    "signature": signature
}

response = requests.post(
    url,
    params=params,
    data=http_body,
    headers={"Content-Type": "application/json"}
)

print("URL:", response.url)
print("HTTP staatus:", response.status_code)
print("Vastuse algus:")
print(response.text[:2000])