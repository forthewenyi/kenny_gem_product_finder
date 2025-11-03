"""
Debug script to see what's actually being returned from cache.
"""

import os
import asyncio
import json
from database_service import DatabaseService
from dotenv import load_dotenv

load_dotenv()

async def debug_cache_response():
    """Check what the cache returns for air fryer"""
    db = DatabaseService()

    print("\n" + "="*80)
    print("🔍 DEBUGGING CACHE RESPONSE FOR AIR FRYER")
    print("="*80)

    # Get cached search
    print("\n1️⃣  Retrieving cached search response...")
    cached_result = await db.get_cached_search("air fryer")

    if not cached_result:
        print("❌ No cache found for 'air fryer'")
        print("   Please search for 'air fryer' first to populate the cache")
        return

    print("✅ Cache hit!")

    # Check the results structure
    if not cached_result.results:
        print("❌ No results in cached response")
        return

    print(f"\n2️⃣  Checking GOOD tier products...")
    print(f"   Found {len(cached_result.results.good)} products in GOOD tier")

    for i, product in enumerate(cached_result.results.good, 1):
        print(f"\n   📦 Product {i}: {product.name}")
        print(f"      Brand: {product.brand}")
        print(f"      Tier: {product.tier}")

        # Check characteristics
        print(f"\n      🏷️  Characteristics:")
        if product.characteristics:
            print(f"         Type: {type(product.characteristics)}")
            print(f"         Length: {len(product.characteristics)}")
            print(f"         Contents: {product.characteristics}")
        else:
            print(f"         ❌ EMPTY or NULL!")

        # Check durability_data
        print(f"\n      💪 Durability Data:")
        if product.durability_data:
            print(f"         Score: {product.durability_data.score}")
            print(f"         Lifespan: {product.durability_data.average_lifespan_years} years")
        else:
            print(f"         ❌ MISSING!")

        # Check practical_metrics
        print(f"\n      🔧 Practical Metrics:")
        if product.practical_metrics:
            print(f"         Cleaning time: {product.practical_metrics.cleaning_time_minutes} min")
            print(f"         Weight: {product.practical_metrics.weight_lbs} lbs")
        else:
            print(f"         ❌ MISSING!")

        # Serialize to JSON to see what frontend receives
        print(f"\n      📤 JSON Serialization (what frontend sees):")
        try:
            product_dict = product.model_dump()
            print(f"         Characteristics in JSON: {product_dict.get('characteristics')}")
            print(f"         Durability data in JSON: {product_dict.get('durability_data') is not None}")
        except Exception as e:
            print(f"         ❌ Error serializing: {e}")

    print("\n" + "="*80)
    print("🔍 CHECKING RAW DATABASE DATA")
    print("="*80)

    # Check raw database
    search_query = db.client.table("search_queries").select("*, product_search_results(*, products(*))").eq("original_query", "air fryer").limit(1).execute()

    if search_query.data:
        cached_search = search_query.data[0]
        if cached_search.get("product_search_results"):
            first_result = cached_search["product_search_results"][0]
            product_data = first_result["products"]

            print(f"\n📊 Raw database product: {product_data.get('name')}")
            print(f"   Characteristics (raw): {product_data.get('characteristics')}")
            print(f"   Characteristics type: {type(product_data.get('characteristics'))}")
            print(f"   Durability data (raw): {product_data.get('durability_data') is not None}")
            print(f"   Practical metrics (raw): {product_data.get('practical_metrics') is not None}")

    print("\n" + "="*80)

if __name__ == "__main__":
    asyncio.run(debug_cache_response())
