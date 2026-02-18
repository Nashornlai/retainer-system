# Project Findings

## Research
- [x] Confirmed Apify as the most reliable source for Facebook Ads data.
- [x] Verified that direct scraping of Facebook Ad Library is blocked/unstable.

## Discoveries
- **Apify Schema**: The `apify/facebook-ads-scraper` actor requires `startUrls` with a fully constructed query URL (e.g., `facebook.com/ads/library/?q=...`) rather than just `searchTerms` for robust keyword searching.
- **JSON Structure**: The ad data is nested deep within `snapshot`. Key fields are `snapshot.pageName`, `snapshot.linkUrl` (CTA), and `snapshot.cards` (for Carousel ads).
- **Email Extraction**: Pure regex on the body text is not enough; crawling the website's `/impressum` and contact pages is essential for German companies.

## Constraints
- **Rate Limiting**: Website scraping must be polite (1s delay).
- **Apify Costs**: Computation units are consumed; efficient filtering by country/date is needed to save costs.
