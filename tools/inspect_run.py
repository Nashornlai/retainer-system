from apify_client import ApifyClient
import os
from dotenv import load_dotenv
import json

load_dotenv()

token = os.getenv("APIFY_TOKEN")
client = ApifyClient(token)

RUN_ID = "tlkU6BhedFgUk5cCa"

print(f"🕵️ Inspecting Run: {RUN_ID}...")
run = client.run(RUN_ID).get()
dataset_id = run["defaultDatasetId"]
print(f"📂 Dataset ID: {dataset_id}")

items = client.dataset(dataset_id).list_items(limit=1).items
if items:
    print("✅ Got 1 item. Keys found:")
    print(list(items[0].keys()))
    with open("schema_sample.json", "w") as f:
        json.dump(items[0], f, indent=2)
    print("Saved to schema_sample.json")
else:
    print("⚠️ No items in dataset yet.")
