#!/usr/bin/env python3
"""Check air fryer cached data"""

from database_service import DatabaseService
from dotenv import load_dotenv

load_dotenv()

db = DatabaseService()

print("🔍 Checking 'air fryer' cached data...")

# Get the cached search
result = db.client.table("search_queries").select(
    "*, product_search_results(*, products(*))"
).eq("original_query", "air fryer").execute()

if result.data:
    search = result.data[0]
    print(f"\n✅ Found cached search from: {search['created_at']}")

    products = []
    for psr in search.get("product_search_results", []):
        product = psr.get("products", {})
        products.append(product)

    print(f"\n📦 Products cached: {len(products)}")

    for i, product in enumerate(products[:3], 1):
        print(f"\n{i}. {product.get('name')}")
        print(f"   Lifespan: {product.get('expected_lifespan_years')} years")
        print(f"   Price: ${product.get('price')}")
        print(f"   Cost/year: ${product.get('cost_per_year')}")

        # Check if this is the old data format
        if product.get('expected_lifespan_years') in [None, 0, 3.0, 4.0]:
            print(f"   ⚠️  This is OLD DATA (before durability validation)")

    print("\n" + "="*60)
    print("RECOMMENDATION:")
    print("This is cached data from BEFORE durability validation was added.")
    print("To test the new validation, either:")
    print("1. Delete this cache entry (run: python clear_air_fryer_cache.py)")
    print("2. Search for a different product (e.g., 'cast iron skillet')")
    print("3. Wait 24 hours for cache to expire")
else:
    print("❌ No cached data found for 'air fryer'")
