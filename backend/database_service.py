"""
Database service for caching search results and products using Supabase.
This reduces API calls to Google Search and Gemini by caching previous searches.
"""

import os
import hashlib
import json
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta, timezone
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

        # Dynamic cache TTL based on query popularity
        self.cache_ttl_popular_hours = 168  # 1 week for popular searches (>5 accesses)
        self.cache_ttl_normal_hours = 24     # 24 hours for normal searches
        self.cache_ttl_niche_hours = 72      # 3 days for niche searches (1-2 accesses)

    def normalize_query(self, query: str) -> str:
        """Normalize query for better cache matching"""
        return query.lower().strip()

    def _get_dynamic_ttl(self, access_count: int) -> int:
        """
        Calculate dynamic cache TTL based on query popularity

        Args:
            access_count: Number of times this query has been accessed

        Returns:
            TTL in hours
        """
        if access_count >= 5:
            # Popular search - cache for 1 week
            return self.cache_ttl_popular_hours
        elif access_count >= 2:
            # Niche search - cache for 3 days
            return self.cache_ttl_niche_hours
        else:
            # Normal/new search - cache for 24 hours
            return self.cache_ttl_normal_hours

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
        Uses dynamic TTL based on query popularity.
        """
        try:
            normalized_query = self.normalize_query(query)

            # First, get all matching queries to determine TTL dynamically
            query_builder = (
                self.client.table("search_queries")
                .select("id, created_at, access_count, product_search_results(*, products(*))")
                .eq("normalized_query", normalized_query)
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
            access_count = cached_search.get("access_count", 0)

            # Calculate dynamic TTL based on popularity
            ttl_hours = self._get_dynamic_ttl(access_count)
            cache_cutoff = datetime.now(timezone.utc) - timedelta(hours=ttl_hours)

            # Check if cache is still valid
            created_at = datetime.fromisoformat(cached_search["created_at"].replace('Z', '+00:00'))
            if created_at < cache_cutoff:
                # Cache expired
                print(f"🕒 Cache expired for '{query}' (TTL: {ttl_hours}h, access_count: {access_count})")
                return None

            # Cache hit! Update access tracking
            new_access_count = access_count + 1
            self.client.table("search_queries").update({
                "last_accessed_at": datetime.now(timezone.utc).isoformat(),
                "access_count": new_access_count
            }).eq("id", cached_search["id"]).execute()

            print(f"✓ Cache hit for '{query}' (access #{new_access_count}, TTL: {ttl_hours}h)")

            # Transform cached data back to SearchResponse format
            return self._transform_cached_search(cached_search)

        except Exception as e:
            print(f"Error retrieving cached search: {e}")
            return None

    def _transform_cached_search(self, cached_search: Dict[str, Any]) -> SearchResponse:
        """Transform cached database result into SearchResponse"""
        from models import ValueMetrics, WebSource, TierResults, QualityData, PracticalMetrics

        # Group products by tier
        good_products = []
        better_products = []
        best_products = []

        for result in cached_search.get("product_search_results", []):
            tier = result["tier"]
            product_data = result["products"]

            # Reconstruct value_metrics
            value_metrics = ValueMetrics(
                upfront_price=float(product_data["price"]),
                expected_lifespan_years=float(product_data["expected_lifespan_years"]),
                cost_per_year=float(product_data.get("cost_per_year", 0)),
                cost_per_day=float(product_data.get("cost_per_day", 0))
            )

            # Reconstruct quality_data if present
            quality_data = None
            if product_data.get("quality_data"):
                dd = product_data["quality_data"]
                quality_data = QualityData(
                    score=dd.get("score", 0),
                    average_lifespan_years=dd.get("average_lifespan_years", 0.0),
                    still_working_after_5years_percent=dd.get("still_working_after_5years_percent", 0),
                    total_user_reports=dd.get("total_user_reports", 0),
                    common_failure_points=dd.get("common_failure_points", []),
                    repairability_score=dd.get("repairability_score", 0),
                    material_quality_indicators=dd.get("material_quality_indicators", []),
                    data_sources=dd.get("data_sources", [])
                )

            # Reconstruct practical_metrics if present
            practical_metrics = None
            if product_data.get("practical_metrics"):
                pm = product_data["practical_metrics"]
                practical_metrics = PracticalMetrics(
                    cleaning_time_minutes=pm.get("cleaning_time_minutes"),
                    cleaning_details=pm.get("cleaning_details", ""),
                    setup_time=pm.get("setup_time", "Ready"),
                    setup_details=pm.get("setup_details", ""),
                    learning_curve=pm.get("learning_curve", "Medium"),
                    learning_details=pm.get("learning_details", ""),
                    maintenance_level=pm.get("maintenance_level", "Medium"),
                    maintenance_details=pm.get("maintenance_details", ""),
                    weight_lbs=pm.get("weight_lbs"),
                    weight_notes=pm.get("weight_notes"),
                    dishwasher_safe=pm.get("dishwasher_safe", False),
                    oven_safe=pm.get("oven_safe", False),
                    oven_max_temp=pm.get("oven_max_temp")
                )

            # Reconstruct web_sources
            web_sources = []
            for source in product_data.get("web_sources", []):
                if isinstance(source, dict):
                    web_sources.append(WebSource(
                        url=source.get("url", ""),
                        title=source.get("title", ""),
                        snippet=source.get("snippet", ""),
                        relevance_score=source.get("relevance_score")
                    ))

            product = Product(
                name=product_data["name"],
                brand=product_data.get("brand", ""),
                tier=product_data["tier"],
                category=product_data.get("category", "general"),
                value_metrics=value_metrics,
                quality_data=quality_data,
                practical_metrics=practical_metrics,
                characteristics=product_data.get("characteristics", []),
                key_features=product_data.get("key_features", []),
                materials=product_data.get("materials", []),
                why_its_a_gem=product_data.get("why_its_a_gem", ""),
                web_sources=web_sources,
                maintenance_level=product_data.get("maintenance_level", "Medium"),
                best_for=product_data.get("best_for", ""),
                trade_offs=product_data.get("trade_offs", [])
            )

            if tier == "good":
                good_products.append(product)
            elif tier == "better":
                better_products.append(product)
            elif tier == "best":
                best_products.append(product)

        tier_results = TierResults(
            good=good_products,
            better=better_products,
            best=best_products
        )

        # Generate aggregated characteristics from all products
        from models import AggregatedCharacteristic
        from collections import Counter

        all_products = good_products + better_products + best_products
        characteristic_to_products = {}

        for product in all_products:
            for char in product.characteristics:
                if char not in characteristic_to_products:
                    characteristic_to_products[char] = []
                characteristic_to_products[char].append(product.name)

        aggregated_characteristics = [
            AggregatedCharacteristic(
                label=char,
                count=len(products),
                product_names=products
            )
            for char, products in sorted(characteristic_to_products.items(), key=lambda x: len(x[1]), reverse=True)
        ]

        # Reconstruct real_search_metrics if present
        from models import RealSearchMetrics
        real_search_metrics = None
        if cached_search.get("real_search_metrics"):
            rsm = cached_search["real_search_metrics"]
            real_search_metrics = RealSearchMetrics(
                total_sources_analyzed=rsm.get("total_sources_analyzed", 0),
                reddit_threads=rsm.get("reddit_threads", 0),
                expert_reviews=rsm.get("expert_reviews", 0),
                search_queries_executed=rsm.get("search_queries_executed", 0),
                search_queries=rsm.get("search_queries", []),
                unique_sources=rsm.get("unique_sources", 0)
            )

        return SearchResponse(
            results=tier_results,
            search_metadata={
                "sources_searched": cached_search.get("sources_searched", []),
                "search_queries_used": cached_search.get("search_queries_used", []),
                "cached": True,
                "cache_date": cached_search.get("created_at")
            },
            processing_time_seconds=0.0,  # Cached result, instant
            aggregated_characteristics=aggregated_characteristics,  # Add aggregated characteristics
            real_search_metrics=real_search_metrics  # Add real_search_metrics from cache
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

            # Serialize real_search_metrics if present
            real_search_metrics_json = None
            if search_response.real_search_metrics:
                rsm = search_response.real_search_metrics
                real_search_metrics_json = {
                    "total_sources_analyzed": rsm.total_sources_analyzed,
                    "reddit_threads": rsm.reddit_threads,
                    "expert_reviews": rsm.expert_reviews,
                    "search_queries_executed": rsm.search_queries_executed,
                    "search_queries": rsm.search_queries,
                    "unique_sources": rsm.unique_sources
                }

            # Insert search query
            search_data = {
                "original_query": query,
                "normalized_query": normalized_query,
                "tier_preference": tier_preference,
                "max_price": max_price,
                "context": context or {},
                "sources_searched": search_response.search_metadata.get("sources_searched", []),
                "search_queries_used": search_response.search_metadata.get("search_queries_used", []),
                "processing_time_seconds": search_response.processing_time_seconds,
                "real_search_metrics": real_search_metrics_json,  # Add real_search_metrics
                "access_count": 0  # Initialize access count for new cache entries
            }

            search_result = self.client.table("search_queries").insert(search_data).execute()

            if not search_result.data:
                return False

            search_id = search_result.data[0]["id"]

            # Get all products from all tiers
            all_products = []
            for tier_name in ["good", "better", "best"]:
                tier_products = getattr(search_response.results, tier_name, [])
                for product in tier_products:
                    all_products.append((tier_name, product))

            # Insert products and link to search
            for tier, product in all_products:
                # Check if product exists
                existing_product = (
                    self.client.table("products")
                    .select("id")
                    .eq("name", product.name)
                    .eq("brand", product.brand)
                    .execute()
                )

                if existing_product.data and len(existing_product.data) > 0:
                    product_id = existing_product.data[0]["id"]
                else:
                    # Serialize web_sources to JSON
                    web_sources_json = []
                    for source in product.web_sources:
                        web_sources_json.append({
                            "url": source.url,
                            "title": source.title,
                            "snippet": source.snippet,
                            "relevance_score": source.relevance_score
                        })

                    # Serialize quality_data if present
                    quality_data_json = None
                    if product.quality_data:
                        quality_data_json = {
                            "score": product.quality_data.score,
                            "average_lifespan_years": product.quality_data.average_lifespan_years,
                            "still_working_after_5years_percent": product.quality_data.still_working_after_5years_percent,
                            "total_user_reports": product.quality_data.total_user_reports,
                            "common_failure_points": product.quality_data.common_failure_points,
                            "repairability_score": product.quality_data.repairability_score,
                            "material_quality_indicators": product.quality_data.material_quality_indicators,
                            "data_sources": product.quality_data.data_sources
                        }

                    # Serialize practical_metrics if present
                    practical_metrics_json = None
                    if product.practical_metrics:
                        practical_metrics_json = {
                            "cleaning_time_minutes": product.practical_metrics.cleaning_time_minutes,
                            "cleaning_details": product.practical_metrics.cleaning_details,
                            "setup_time": product.practical_metrics.setup_time,
                            "setup_details": product.practical_metrics.setup_details,
                            "learning_curve": product.practical_metrics.learning_curve,
                            "learning_details": product.practical_metrics.learning_details,
                            "maintenance_level": product.practical_metrics.maintenance_level,
                            "maintenance_details": product.practical_metrics.maintenance_details,
                            "weight_lbs": product.practical_metrics.weight_lbs,
                            "weight_notes": product.practical_metrics.weight_notes,
                            "dishwasher_safe": product.practical_metrics.dishwasher_safe,
                            "oven_safe": product.practical_metrics.oven_safe,
                            "oven_max_temp": product.practical_metrics.oven_max_temp
                        }

                    # Insert new product
                    product_data = {
                        "name": product.name,
                        "brand": product.brand,
                        "price": float(product.value_metrics.upfront_price),
                        "expected_lifespan_years": float(product.value_metrics.expected_lifespan_years),
                        "tier": product.tier.value if hasattr(product.tier, 'value') else str(product.tier),
                        "cost_per_year": float(product.value_metrics.cost_per_year),
                        "cost_per_day": float(product.value_metrics.cost_per_day),
                        "why_its_a_gem": product.why_its_a_gem,
                        "key_features": product.key_features,
                        "materials": product.materials,
                        "characteristics": product.characteristics,
                        "trade_offs": product.trade_offs or [],
                        "best_for": product.best_for,
                        "web_sources": web_sources_json,
                        "maintenance_level": product.maintenance_level,
                        "category": product.category,
                        "quality_data": quality_data_json,
                        "practical_metrics": practical_metrics_json
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
            from models import ValueMetrics, WebSource

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
                # Reconstruct value_metrics
                value_metrics = ValueMetrics(
                    upfront_price=float(product_data["price"]),
                    expected_lifespan_years=float(product_data["expected_lifespan_years"]),
                    cost_per_year=float(product_data.get("cost_per_year", 0)),
                    cost_per_day=float(product_data.get("cost_per_day", 0))
                )

                # Reconstruct web_sources
                web_sources = []
                for source in product_data.get("web_sources", []):
                    if isinstance(source, dict):
                        web_sources.append(WebSource(
                            url=source.get("url", ""),
                            title=source.get("title", ""),
                            snippet=source.get("snippet", ""),
                            relevance_score=source.get("relevance_score")
                        ))

                product = Product(
                    name=product_data["name"],
                    brand=product_data.get("brand", ""),
                    tier=product_data["tier"],
                    category=product_data.get("category", "general"),
                    value_metrics=value_metrics,
                    characteristics=product_data.get("characteristics", []),
                    key_features=product_data.get("key_features", []),
                    materials=product_data.get("materials", []),
                    why_its_a_gem=product_data.get("why_its_a_gem", ""),
                    web_sources=web_sources,
                    maintenance_level=product_data.get("maintenance_level", "Medium"),
                    best_for=product_data.get("best_for", ""),
                    trade_offs=product_data.get("trade_offs", [])
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
