"""
Database service for caching search results and products using Supabase.
This reduces API calls to Google Search and Gemini by caching previous searches.
"""

import os
import hashlib
import json
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from supabase import create_client, Client
from models import Product, SearchResponse

class DatabaseService:
    """Service for caching products and search queries in Supabase"""

    def __init__(self):
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_ANON_KEY")

        if not url or not key:
            raise ValueError("SUPABASE_URL and SUPABASE_ANON_KEY must be set in environment")

        self.client: Client = create_client(url, key)
        self.cache_ttl_hours = 24  # Cache results for 24 hours

    def normalize_query(self, query: str) -> str:
        """Normalize query for better cache matching"""
        return query.lower().strip()

    def get_query_hash(self, query: str, tier_preference: Optional[str] = None,
                       max_price: Optional[float] = None) -> str:
        """Generate a hash for the query parameters"""
        query_params = {
            "query": self.normalize_query(query),
            "tier_preference": tier_preference,
            "max_price": max_price
        }
        query_string = json.dumps(query_params, sort_keys=True)
        return hashlib.md5(query_string.encode()).hexdigest()

    async def get_cached_search(self, query: str, tier_preference: Optional[str] = None,
                                max_price: Optional[float] = None) -> Optional[SearchResponse]:
        """
        Check if we have a cached search result for this query.
        Returns None if no cache hit or cache is expired.
        """
        try:
            normalized_query = self.normalize_query(query)

            # Calculate cache expiration time
            cache_cutoff = datetime.now() - timedelta(hours=self.cache_ttl_hours)

            # Query for matching searches
            query_builder = (
                self.client.table("search_queries")
                .select("*, product_search_results(*, products(*))")
                .eq("normalized_query", normalized_query)
                .gte("created_at", cache_cutoff.isoformat())
            )

            if tier_preference:
                query_builder = query_builder.eq("tier_preference", tier_preference)

            if max_price:
                query_builder = query_builder.lte("max_price", max_price)

            response = query_builder.execute()

            if not response.data or len(response.data) == 0:
                return None

            # Get the most recent search
            cached_search = response.data[0]

            # Update last_accessed_at
            self.client.table("search_queries").update({
                "last_accessed_at": datetime.now().isoformat()
            }).eq("id", cached_search["id"]).execute()

            # Transform cached data back to SearchResponse format
            return self._transform_cached_search(cached_search)

        except Exception as e:
            print(f"Error retrieving cached search: {e}")
            return None

    def _transform_cached_search(self, cached_search: Dict[str, Any]) -> SearchResponse:
        """Transform cached database result into SearchResponse"""
        # Group products by tier
        results_by_tier = {"good": [], "better": [], "best": []}

        for result in cached_search.get("product_search_results", []):
            tier = result["tier"]
            product_data = result["products"]

            product = Product(
                product_name=product_data["product_name"],
                brand=product_data.get("brand"),
                price=float(product_data["price"]),
                expected_lifespan_years=product_data["expected_lifespan_years"],
                tier=product_data["tier"],
                cost_per_year=float(product_data.get("cost_per_year", 0)),
                cost_per_day=float(product_data.get("cost_per_day", 0)),
                why_gem=product_data.get("why_gem"),
                key_features=product_data.get("key_features", []),
                trade_offs=product_data.get("trade_offs"),
                best_for=product_data.get("best_for"),
                web_sources=product_data.get("web_sources", []),
                maintenance_level=product_data.get("maintenance_level")
            )

            if tier in results_by_tier:
                results_by_tier[tier].append(product)

        return SearchResponse(
            results=results_by_tier,
            search_metadata={
                "sources_searched": cached_search.get("sources_searched", []),
                "search_queries_used": cached_search.get("search_queries_used", []),
                "cached": True,
                "cache_date": cached_search.get("created_at")
            },
            processing_time_seconds=0.0,  # Cached result, instant
            educational_insights=cached_search.get("educational_insights", [])
        )

    async def cache_search_results(self, query: str, search_response: SearchResponse,
                                   tier_preference: Optional[str] = None,
                                   max_price: Optional[float] = None,
                                   context: Optional[Dict[str, str]] = None) -> bool:
        """
        Cache a search query and its results to the database.
        Returns True if successful, False otherwise.
        """
        try:
            normalized_query = self.normalize_query(query)

            # Insert search query
            search_data = {
                "original_query": query,
                "normalized_query": normalized_query,
                "tier_preference": tier_preference,
                "max_price": max_price,
                "context": context or {},
                "sources_searched": search_response.search_metadata.get("sources_searched", []),
                "search_queries_used": search_response.search_metadata.get("search_queries_used", []),
                "educational_insights": search_response.educational_insights,
                "processing_time_seconds": search_response.processing_time_seconds
            }

            search_result = self.client.table("search_queries").insert(search_data).execute()

            if not search_result.data:
                return False

            search_id = search_result.data[0]["id"]

            # Insert products and link to search
            for tier, products in search_response.results.items():
                for product in products:
                    # Check if product exists
                    existing_product = (
                        self.client.table("products")
                        .select("id")
                        .eq("product_name", product.product_name)
                        .eq("brand", product.brand)
                        .execute()
                    )

                    if existing_product.data and len(existing_product.data) > 0:
                        product_id = existing_product.data[0]["id"]
                    else:
                        # Insert new product
                        product_data = {
                            "product_name": product.product_name,
                            "brand": product.brand,
                            "price": float(product.price),
                            "expected_lifespan_years": product.expected_lifespan_years,
                            "tier": product.tier,
                            "cost_per_year": float(product.cost_per_year),
                            "cost_per_day": float(product.cost_per_day),
                            "why_gem": product.why_gem,
                            "key_features": product.key_features,
                            "trade_offs": product.trade_offs,
                            "best_for": product.best_for,
                            "web_sources": product.web_sources,
                            "maintenance_level": product.maintenance_level,
                            "category": self._extract_category(query)
                        }

                        product_result = self.client.table("products").insert(product_data).execute()

                        if not product_result.data:
                            continue

                        product_id = product_result.data[0]["id"]

                    # Link product to search
                    link_data = {
                        "product_id": product_id,
                        "search_query_id": search_id,
                        "tier": tier
                    }

                    # Insert link (ignore duplicates)
                    try:
                        self.client.table("product_search_results").insert(link_data).execute()
                    except Exception as e:
                        # Ignore duplicate key errors
                        if "duplicate" not in str(e).lower():
                            print(f"Error linking product to search: {e}")

            return True

        except Exception as e:
            print(f"Error caching search results: {e}")
            return False

    def _extract_category(self, query: str) -> str:
        """Extract product category from query"""
        query_lower = query.lower()

        categories = {
            "cookware": ["pan", "pot", "skillet", "dutch oven", "wok", "saucepan"],
            "knives": ["knife", "chef's knife", "cleaver", "santoku"],
            "bakeware": ["baking sheet", "cake pan", "muffin tin", "loaf pan"],
            "utensils": ["spatula", "whisk", "tongs", "ladle", "spoon"],
            "appliances": ["blender", "mixer", "food processor", "toaster"],
            "storage": ["container", "jar", "canister", "storage"]
        }

        for category, keywords in categories.items():
            if any(keyword in query_lower for keyword in keywords):
                return category

        return "general"

    async def get_products_by_price_range(self, min_price: float, max_price: float,
                                         tier: Optional[str] = None) -> List[Product]:
        """Get cached products within a price range"""
        try:
            query_builder = (
                self.client.table("products")
                .select("*")
                .gte("price", min_price)
                .lte("price", max_price)
            )

            if tier:
                query_builder = query_builder.eq("tier", tier)

            response = query_builder.execute()

            products = []
            for product_data in response.data:
                product = Product(
                    product_name=product_data["product_name"],
                    brand=product_data.get("brand"),
                    price=float(product_data["price"]),
                    expected_lifespan_years=product_data["expected_lifespan_years"],
                    tier=product_data["tier"],
                    cost_per_year=float(product_data.get("cost_per_year", 0)),
                    cost_per_day=float(product_data.get("cost_per_day", 0)),
                    why_gem=product_data.get("why_gem"),
                    key_features=product_data.get("key_features", []),
                    trade_offs=product_data.get("trade_offs"),
                    best_for=product_data.get("best_for"),
                    web_sources=product_data.get("web_sources", []),
                    maintenance_level=product_data.get("maintenance_level")
                )
                products.append(product)

            return products

        except Exception as e:
            print(f"Error getting products by price range: {e}")
            return []

    async def save_comparison(self, product_ids: List[str], session_id: Optional[str] = None) -> bool:
        """Save a product comparison session"""
        try:
            comparison_data = {
                "product_ids": product_ids,
                "session_id": session_id
            }

            self.client.table("user_comparisons").insert(comparison_data).execute()
            return True

        except Exception as e:
            print(f"Error saving comparison: {e}")
            return False
