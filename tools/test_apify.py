import os
from apify_client import ApifyClient
from dotenv import load_dotenv

load_dotenv()

token = os.getenv("APIFY_TOKEN")

if not token or "YOUR_APIFY_TOKEN" in token:
    print("❌ Error: APIFY_TOKEN is missing or default in .env")
    exit(1)

try:
    client = ApifyClient(token)
    user = client.user().get()
    print(f"✅ Connection Successful! Connected as: {user.get('username', 'Unknown User')}")
except Exception as e:
    print(f"❌ Connection Failed: {e}")
