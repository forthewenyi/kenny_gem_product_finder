"""
Google Custom Search API Service for Kenny Gem Finder
Provides reliable web search with proper rate limiting and error handling.

Setup Instructions:
1. Get API Key: https://console.cloud.google.com/apis/credentials
   - Create project → Enable Custom Search API → Create API Key

2. Create Search Engine: https://programmablesearchengine.google.com/
   - Create new search engine
   - Search entire web: Yes
   - Copy Search Engine ID (cx parameter)

3. Add to .env:
   GOOGLE_SEARCH_API_KEY=your_api_key_here
   GOOGLE_SEARCH_ENGINE_ID=your_engine_id_here

Cost: $5 per 1,000 queries (first 100/day free)
"""
import os
from typing import List, Dict, Optional
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import time


class GoogleSearchService:
    """
    Wrapper for Google Custom Search API with error handling and rate limiting.
    """

    def __init__(self):
        self.api_key = os.getenv("GOOGLE_SEARCH_API_KEY")
        self.search_engine_id = os.getenv("GOOGLE_SEARCH_ENGINE_ID")

        # Check if we should use the API or fallback to free library
        self.use_official_api = bool(self.api_key and self.search_engine_id)

        if self.use_official_api:
            print("✓ Using Google Custom Search API (reliable)")
            self.service = build("customsearch", "v1", developerKey=self.api_key)
        else:
            print("⚠️  Google Custom Search API not configured")
            print("   Will attempt fallback to googlesearch-python (may be rate-limited)")
            print("   See google_search_service.py for setup instructions")
            self.service = None

    def search(
        self,
        query: str,
        num_results: int = 10,
        safe_search: str = "off"
    ) -> List[Dict[str, str]]:
        """
        Search using Google Custom Search API.

        Args:
            query: Search query string
            num_results: Number of results to return (max 10 per request)
            safe_search: "off", "medium", or "high"

        Returns:
            List of dicts with keys: url, title, snippet
        """
        if not self.use_official_api:
            return self._fallback_search(query, num_results)

        try:
            results = []

            # Google Custom Search API returns max 10 results per request
            # We can paginate for more, but that uses more quota
            num_results = min(num_results, 10)

            # Execute search
            response = self.service.cse().list(
                q=query,
                cx=self.search_engine_id,
                num=num_results,
                safe=safe_search
            ).execute()

            # Parse results
            if "items" in response:
                for item in response["items"]:
                    results.append({
                        "url": item.get("link", ""),
                        "title": item.get("title", ""),
                        "snippet": item.get("snippet", ""),
                        "display_link": item.get("displayLink", "")
                    })

            return results

        except HttpError as e:
            error_details = e.error_details if hasattr(e, 'error_details') else str(e)
            print(f"⚠️  Google Custom Search API error: {error_details}")

            # Check for quota exceeded
            if e.resp.status == 429:
                print("   Daily quota exceeded. Consider upgrading or using fallback.")
            elif e.resp.status == 400:
                print("   Invalid API key or Search Engine ID. Check .env configuration.")

            # Fallback to free library
            return self._fallback_search(query, num_results)

        except Exception as e:
            print(f"⚠️  Unexpected error in Google search: {e}")
            return self._fallback_search(query, num_results)

    def _fallback_search(self, query: str, num_results: int) -> List[Dict[str, str]]:
        """
        Fallback to free googlesearch-python library.
        This may be rate-limited but provides a backup option.
        """
        try:
            from googlesearch import search as google_search

            results = []

            # Add delay to avoid rate limiting
            time.sleep(1)

            # Fetch URLs
            for url in google_search(query, num_results=num_results, sleep_interval=2, lang='en'):
                results.append({
                    "url": url,
                    "title": url.split('/')[2] if '/' in url else url,
                    "snippet": f"Result from {url}",
                    "display_link": url.split('/')[2] if '/' in url else url
                })

                if len(results) >= num_results:
                    break

            return results

        except Exception as e:
            print(f"⚠️  Fallback search also failed: {e}")
            return []

    def get_quota_info(self) -> Dict[str, any]:
        """
        Get information about API quota usage.

        Returns:
            Dict with quota information
        """
        if not self.use_official_api:
            return {
                "using_official_api": False,
                "free_daily_quota": 100,
                "cost_per_1000": 5.0,
                "setup_url": "https://console.cloud.google.com/apis/credentials"
            }

        return {
            "using_official_api": True,
            "api_key_configured": bool(self.api_key),
            "search_engine_configured": bool(self.search_engine_id),
            "free_daily_quota": 100,
            "cost_per_1000_after_free": 5.0,
            "note": "First 100 queries per day are free"
        }


# Singleton instance
_google_search_service = None


def get_google_search_service() -> GoogleSearchService:
    """Get or create the global Google Search service instance"""
    global _google_search_service
    if _google_search_service is None:
        _google_search_service = GoogleSearchService()
    return _google_search_service
