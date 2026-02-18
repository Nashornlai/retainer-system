import os
from apify_client import ApifyClient
from dotenv import load_dotenv
import urllib.parse

load_dotenv()

class MetaClient:
    def __init__(self):
        token = os.getenv("APIFY_TOKEN")
        if not token:
            raise ValueError("APIFY_TOKEN not found in .env")
        self.client = ApifyClient(token)

    def fetch_ads(self, keywords, country="DE", max_results=50):
        """
        Fetches ads from Meta Ad Library using Apify.
        Constructs a direct URL to satisfy 'startUrls' requirement.
        """
        print(f"🔍 Searching Meta Ads for keywords: {keywords} in {country}...")
        
        start_urls = []
        for keyword in keywords:
            # Construct the Ad Library URL
            params = {
                "active_status": "active", # Only active ads for lead gen
                "ad_type": "all",
                "country": country,
                "q": keyword,
                "sort_data[direction]": "desc",
                "sort_data[mode]": "relevance_monthly_grouped",
                "search_type": "keyword_unordered",
                "media_type": "all"
            }
            query_string = urllib.parse.urlencode(params)
            url = f"https://www.facebook.com/ads/library/?{query_string}"
            start_urls.append({"url": url})
            print(f"🔗 Generated URL: {url}")

        # Input for curious_coder/facebook-ads-library-scraper
        # Schema: { "urls": [ { "url": "..." } ], "count": int }
        run_input = {
            "urls": start_urls,
            "count": max_results,
        }

        # Run the actor
        # Note: Using 'curious_coder/facebook-ads-library-scraper' (Cheaper: ~$0.75-1.25/1000)
        print("🚀 Sending request to Apify (Curious Coder)...")
        run = self.client.actor("curious_coder/facebook-ads-library-scraper").call(run_input=run_input)

        if not run:
            print("❌ Apify run failed to start.")
            return []

        # UI link to the run
        print(f"RUN URL: https://console.apify.com/view/runs/{run['id']}")

        # Fetch results
        dataset_items = []
        for item in self.client.dataset(run["defaultDatasetId"]).iterate_items():
            dataset_items.append(item)
        
        print(f"✅ Found {len(dataset_items)} ads.")
        return dataset_items

if __name__ == "__main__":
    # Remove one keyword to save credits/time during test
    client = MetaClient()
    # Test with a very specific keyword to limit results if possible, but max_results handles that
    ads = client.fetch_ads(["skincare"], max_results=5)
    
    if ads:
        print("--- Sample Ad Data ---")
        print(ads[0])
        import json
        with open("sample_ad.json", "w") as f:
            json.dump(ads[0], f, indent=2)
        print("--- Saved sample_ad.json ---")
    else:
        print("⚠️ No ads found.")
