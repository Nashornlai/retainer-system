# Project Constitution (Gemini)

## 1. Data Schemas (The "Data-First" Rule)

### Raw Input (Search Parameters)
```json
{
  "keywords": ["fashion", "skincare"],
  "country_code": "DE",
  "platform": "facebook", 
  "max_results": 50
}
```

### Intermediate: Ad Library Entry (from Apify)
```json
{
  "page_name": "Brand Name",
  "page_profile_uri": "https://facebook.com/BrandName",
  "ad_creative_link_titles": ["Shop Now"],
  "ad_creative_body": "...",
  "snapshot_url": "..."
}
```

### Processed Output (The "Payload")
```json
[
  {
    "company_name": "Brand Name",
    "website_url": "https://brand.com",
    "email": "contact@brand.com",
    "ad_library_url": "https://www.facebook.com/ads/library/...",
    "facebook_page": "https://facebook.com/BrandName",
    "instagram_url": "https://instagram.com/BrandName",
    "source_keyword": "fashion"
  }
]
```

## 2. Behavioral Rules
- **AGENTS MUST SPEAK GERMAN TO THE USER.** (Agent soll mit dem User auf Deutsch sprechen).
- **Respect Robots.txt**: Attempt to respect scraping policies where possible.
- **Deterministic Extraction**: Use regex and DOM selectors for emails; do not "guess" using LLMs unless traversing complex navigation.
- **Rate Limiting**: Add delays between website visits to avoid IP bans.

## 3. Architectural Invariants
- Logic must be deterministic.
- No business logic in LLM prompts; use `tools/` for deterministic tasks.
- Layer 1 (SOPs) must be updated before Layer 3 (Code).

## 4. Maintenance Log
- [ ] Project Created.
- [ ] Schema Defined.
