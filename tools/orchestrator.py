import pandas as pd
from tools.meta_client import MetaClient
from tools.website_walker import WebsiteWalker
import time
import re

def extract_domain(text):
    """Simple regex to find a domain in text if no direct link exists."""
    if not text: return None
    match = re.search(r'(https?://[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', text)
    if match:
        return match.group(1)
    return None

def main(keywords=None, country="DE", max_results=20):
    print("🚀 Starting Lead Generation System...")
    
    # 1. Configuration if not provided (CLI Mode)
    if keywords is None:
        print("--- ⚙️ Konfiguration ---")
        keyword_input = input("Geben Sie ein Keyword ein (Default: skincare): ").strip()
        KEYWORDS = [keyword_input] if keyword_input else ["skincare"]
        
        country_input = input("Geben Sie den Ländercode ein (Default: DE): ").strip().upper()
        COUNTRY = country_input if country_input else "DE"
    else:
        # API/GUI Mode
        KEYWORDS = keywords if isinstance(keywords, list) else [keywords]
        COUNTRY = country
    
    # max_results is passed directly
    
    # 2. Initialize Tools
    # 3. Initialize Tools
    # Let exceptions propagate to app.py for UI feedback
    meta = MetaClient()
    walker = WebsiteWalker()
    
    # 3. Fetch Ads
    ads = meta.fetch_ads(KEYWORDS, country=COUNTRY, max_results=max_results)
    
    if not ads:
        print("⚠️ No ads found. Exiting.")
        return pd.DataFrame(), {}

    # 4. Process Leads
    leads = []
    processed_domains = set()
    stats = {
        "fetched": len(ads),
        "duplicates": 0,
        "no_website": 0,
        "processed": 0
    }
    
    print(f"🔄 Processing {len(ads)} raw ads...")
    
    for ad in ads:
        # Extract basic info (Adapting to Apify's schema)
        # Check for different possible keys from various scrapers
        snapshot = ad.get("snapshot", {})
        page_name = snapshot.get("pageName") or snapshot.get("page_name") or ad.get("pageName") or ad.get("page_name") or "Unknown"
        
        # Try to find the website URL
        # Priority 1: Direct Link URL (CTA) from snapshot
        website_url = snapshot.get("linkUrl") or snapshot.get("link_url")
        
        # Ad Image extraction (New)
        ad_image = None
        images = snapshot.get("images", [])
        if images and len(images) > 0:
             ad_image = images[0].get("original_image_url") or images[0].get("resized_image_url")
        
        if not ad_image:
             cards = snapshot.get("cards", [])
             if cards and len(cards) > 0:
                 ad_image = cards[0].get("original_image_url") or cards[0].get("resized_image_url")

        # Priority 2: Cards (Carousel links)
        if not website_url:
            cards = snapshot.get("cards", [])
            if cards and isinstance(cards, list) and len(cards) > 0:
                # Check first card for link
                website_url = cards[0].get("linkUrl") or cards[0].get("link_url")
        
        # Priority 3: Extract from body text
        if not website_url:
            body = snapshot.get("body", {})
            body_text = body.get("text", "") if isinstance(body, dict) else str(body)
            # Some scrapers put body directly as string in 'body' or 'title'
            if not body_text:
                 body_text = snapshot.get("title", "") or ad.get("ad_creative_body", "")
            website_url = extract_domain(body_text)
            
        # Clean URL and Deduplicate
        if website_url:
            # Remove query params for domain checking
            if not isinstance(website_url, str):
                 website_url = str(website_url)
            
            clean_domain = website_url.split("?")[0].replace("https://", "").replace("http://", "").split("/")[0]
            if clean_domain.lower() in ["facebook.com", "www.facebook.com", "instagram.com", "www.instagram.com"]:
                 stats["no_website"] += 1
                 continue 
                 
            if clean_domain in processed_domains:
                stats["duplicates"] += 1
                continue # Skip duplicates
            processed_domains.add(clean_domain)
        else:
            stats["no_website"] += 1
            continue # Skip ads without a website
            
        print(f"🔎 Analyzing: {page_name} ({website_url})")

        # 5. Find Email (The "Anti-Gravity" Step via WebsiteWalker)
        email = walker.find_email(website_url)
        
        processed_data = {
            "Company": page_name,
            "Website": website_url,
            "Email": email if email else "Not Found",
            "Ad URL": ad.get("ad_archive_url") or ad.get("adArchiveUrl") or ad.get("snapshotUrl") or ad.get("ad_library_url"),
            "Ad Image": ad_image, # New field
            "Keyword": KEYWORDS[0] 
        }
        
        leads.append(processed_data)
        stats["processed"] += 1
        print(f"   -> Found Email: {email}")

    # 6. Export to CSV
    if leads:
        df = pd.DataFrame(leads)
        filename = "leads.csv"
        df.to_csv(filename, index=False)
        print(f"✅ Saved {len(leads)} leads to {filename}")
        return df, stats # Returning Tuple now
    else:
        print("⚠️ No valid leads extracted.")
        return pd.DataFrame(), stats

if __name__ == "__main__":
    main()
