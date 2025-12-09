"""
Service for managing popular search terms for dynamic navigation dropdowns
"""
import os
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from supabase import create_client, Client


class PopularSearchService:
    """Service for tracking and retrieving popular search terms"""

    def __init__(self):
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_ANON_KEY")

        if not url or not key:
            raise ValueError("SUPABASE_URL and SUPABASE_ANON_KEY must be set in environment")

        self.client: Client = create_client(url, key)
        self.cache: Dict[str, tuple[List[Dict], datetime]] = {}
        self.cache_ttl_minutes = 60  # Cache dropdown data for 1 hour

    def get_cached_popular_searches(self, category: str) -> Optional[List[Dict]]:
        """Get cached popular searches if available and not expired"""
        if category in self.cache:
            data, cached_at = self.cache[category]
            if datetime.now() - cached_at < timedelta(minutes=self.cache_ttl_minutes):
                return data
        return None

    def set_cached_popular_searches(self, category: str, data: List[Dict]):
        """Cache popular searches for a category"""
        self.cache[category] = (data, datetime.now())

    async def track_search(self, query_term: str, category: str) -> bool:
        """
        Track a search term - increment count or insert if new

        Args:
            query_term: The search term (e.g., "Cast Iron Skillet")
            category: Category (cookware, knives, bakeware, small_appliances, or kitchen_tools)

        Returns:
            bool: True if tracking succeeded
        """
        try:
            # Normalize query term
            query_term = query_term.strip()

            # Validate category
            if category not in ['cookware', 'knives', 'bakeware', 'small_appliances', 'kitchen_tools']:
                return False

            # Try to fetch existing record
            existing = self.client.table("popular_search_terms").select("*").eq(
                "query_term", query_term
            ).eq("category", category).execute()

            if existing.data and len(existing.data) > 0:
                # Update existing record
                record_id = existing.data[0]['id']
                current_count = existing.data[0]['search_count']

                self.client.table("popular_search_terms").update({
                    "search_count": current_count + 1,
                    "last_searched": datetime.now().isoformat()
                }).eq("id", record_id).execute()
            else:
                # Insert new record
                self.client.table("popular_search_terms").insert({
                    "query_term": query_term,
                    "category": category,
                    "search_count": 1,
                    "last_searched": datetime.now().isoformat(),
                    "created_at": datetime.now().isoformat()
                }).execute()

            # Invalidate cache for this category
            if category in self.cache:
                del self.cache[category]

            return True

        except Exception as e:
            print(f"Error tracking search: {e}")
            return False

    async def get_popular_searches(self, category: str, limit: int = 8) -> List[Dict]:
        """
        Get top N popular searches for a category

        Args:
            category: Category (cookware, knives, bakeware, small_appliances, or kitchen_tools)
            limit: Maximum number of results to return

        Returns:
            List of dicts with query_term and search_count
        """
        try:
            # Check cache first
            cached = self.get_cached_popular_searches(category)
            if cached is not None:
                return cached

            # Query database
            response = self.client.table("popular_search_terms").select(
                "query_term, search_count"
            ).eq("category", category).order(
                "search_count", desc=True
            ).limit(limit).execute()

            if not response.data:
                return []

            results = [
                {
                    "term": item["query_term"],
                    "count": item["search_count"]
                }
                for item in response.data
            ]

            # Cache the results
            self.set_cached_popular_searches(category, results)

            return results

        except Exception as e:
            print(f"Error fetching popular searches: {e}")
            return []


# Global instance
_popular_search_service_instance = None


def get_popular_search_service() -> PopularSearchService:
    """Get or create the global popular search service instance"""
    global _popular_search_service_instance
    if _popular_search_service_instance is None:
        _popular_search_service_instance = PopularSearchService()
    return _popular_search_service_instance
