#!/usr/bin/env python3
"""Check what's in the cache"""

from database_service import DatabaseService
from dotenv import load_dotenv

load_dotenv()

db = DatabaseService()

print("=" * 80)
print("CACHED DATA REPORT")
print("=" * 80)

# Check search queries
print("\n📊 SEARCH QUERIES CACHED:")
try:
    queries = db.client.table("search_queries").select("*").execute()
    print(f"   Total queries: {len(queries.data)}")

    for query in queries.data:
        print(f"\n   Query: '{query['original_query']}'")
        print(f"   Created: {query['created_at']}")
        print(f"   Last accessed: {query.get('last_accessed_at', 'N/A')}")
        print(f"   Processing time: {query.get('processing_time_seconds', 'N/A')}s")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Check products
print("\n\n🎁 PRODUCTS CACHED:")
try:
    products = db.client.table("products").select("*").execute()
    print(f"   Total products: {len(products.data)}")

    # Group by tier
    by_tier = {"good": [], "better": [], "best": []}
    for product in products.data:
        tier = product.get("tier", "unknown")
        if tier in by_tier:
            by_tier[tier].append(product)

    for tier, tier_products in by_tier.items():
        if tier_products:
            print(f"\n   {tier.upper()} Tier ({len(tier_products)} products):")
            for product in tier_products[:3]:  # Show first 3
                print(f"      - {product['name']} by {product['brand']}")
                print(f"        ${product['price']} | {product['expected_lifespan_years']}yr lifespan | ${product['cost_per_year']}/yr")

except Exception as e:
    print(f"   ❌ Error: {e}")

# Check product-search links
print("\n\n🔗 PRODUCT-SEARCH LINKS:")
try:
    links = db.client.table("product_search_results").select("*").execute()
    print(f"   Total links: {len(links.data)}")
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n" + "=" * 80)

# Test if cache retrieval works
print("\n🧪 TESTING CACHE RETRIEVAL:")
if len(queries.data) > 0:
    test_query = queries.data[0]['original_query']
    print(f"   Testing query: '{test_query}'")

    try:
        cached_result = db.client.table("search_queries").select(
            "*, product_search_results(*, products(*))"
        ).eq("original_query", test_query).execute()

        if cached_result.data and len(cached_result.data) > 0:
            print(f"   ✅ Cache retrieval works!")
            print(f"   Found {len(cached_result.data)} matching searches")

            # Count products in result
            if "product_search_results" in cached_result.data[0]:
                product_count = len(cached_result.data[0]["product_search_results"])
                print(f"   Products in cache: {product_count}")
        else:
            print(f"   ⚠️  No cached results found")

    except Exception as e:
        print(f"   ❌ Cache retrieval failed: {e}")
else:
    print(f"   No queries to test")

print("\n" + "=" * 80)
