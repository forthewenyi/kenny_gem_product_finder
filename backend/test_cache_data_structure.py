"""
Test script to inspect cached data structure and identify missing fields.
"""

import os
import asyncio
from database_service import DatabaseService
from dotenv import load_dotenv
import json

load_dotenv()

async def inspect_cache():
    """Inspect the cached data structure for air fryer"""
    db = DatabaseService()

    print("\n" + "="*80)
    print("🔍 INSPECTING CACHED DATA STRUCTURE")
    print("="*80)

    # Get cached search
    print("\n1️⃣  Getting cached search for 'air fryer'...")
    cached_result = await db.get_cached_search("air fryer")

    if cached_result:
        print("✅ Cache hit!")

        # Check if results exist
        if cached_result.results:
            print("\n2️⃣  Checking GOOD tier products...")
            for i, product in enumerate(cached_result.results.good, 1):
                print(f"\n   Product {i}: {product.name}")
                print(f"   - Characteristics: {product.characteristics}")
                print(f"   - Durability score: {getattr(product, 'durability_score', 'NOT FOUND')}")
                print(f"   - Has value_metrics: {product.value_metrics is not None}")
                if product.value_metrics:
                    print(f"   - Lifespan: {product.value_metrics.expected_lifespan_years} years")
                    print(f"   - Price: ${product.value_metrics.upfront_price}")
        else:
            print("❌ No results in cached data")
    else:
        print("❌ Cache miss")

    # Now check raw database structure
    print("\n" + "="*80)
    print("🗄️  CHECKING RAW DATABASE STRUCTURE")
    print("="*80)

    search_query = db.client.table("search_queries").select("*, product_search_results(*, products(*))").eq("original_query", "air fryer").limit(1).execute()

    if search_query.data:
        cached_search = search_query.data[0]
        print(f"\n✅ Found cached search (ID: {cached_search['id']})")

        if cached_search.get("product_search_results"):
            print(f"\n📦 Found {len(cached_search['product_search_results'])} product links")

            # Check first product
            first_result = cached_search["product_search_results"][0]
            product_data = first_result["products"]

            print(f"\n🔬 Inspecting first product: {product_data.get('name', 'UNKNOWN')}")
            print(f"\n   Fields in database:")
            for key, value in product_data.items():
                if isinstance(value, (list, dict)):
                    print(f"   - {key}: {type(value).__name__} (length: {len(value) if isinstance(value, list) else 'N/A'})")
                    if key == "characteristics" and isinstance(value, list):
                        print(f"      Contents: {value}")
                else:
                    print(f"   - {key}: {value}")
        else:
            print("❌ No product_search_results found")
    else:
        print("❌ No search query found in database")

if __name__ == "__main__":
    asyncio.run(inspect_cache())
