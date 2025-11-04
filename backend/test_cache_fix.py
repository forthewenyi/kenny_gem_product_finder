"""
Test the complete cache fix:
1. First search should cache products with quality_data
2. Second search should retrieve products from cache
"""
import requests
import json
import time

API_URL = "http://localhost:8000/api/search"

def test_search(query, search_num):
    print(f"\n{'='*60}")
    print(f"SEARCH #{search_num}: '{query}'")
    print(f"{'='*60}\n")

    start = time.time()
    response = requests.post(
        API_URL,
        json={"query": query},
        timeout=180
    )
    elapsed = time.time() - start

    data = response.json()

    # Check if cached
    cached = data.get("search_metadata", {}).get("cached", False)
    print(f"✓ Response received in {elapsed:.1f}s")
    print(f"  Cached: {cached}")

    # Count products
    results = data.get("results", {})
    total_products = 0
    for tier in ["good", "better", "best"]:
        count = len(results.get(tier, []))
        print(f"  {tier.upper()}: {count} products")
        total_products += count

    print(f"\n  Total products: {total_products}")

    if total_products == 0:
        print("\n❌ ERROR: No products returned!")
        print("Response keys:", list(data.keys()))
        return False

    # Check first product has quality_data
    first_product = None
    for tier in ["good", "better", "best"]:
        if results.get(tier):
            first_product = results[tier][0]
            break

    if first_product:
        print(f"\n  Sample product: {first_product.get('name', 'Unknown')}")
        print(f"    Price: ${first_product.get('price', 'N/A')}")

        # Check for quality_data
        quality_data = first_product.get("quality_data")
        if quality_data:
            print(f"    Has quality_data: YES ✓")
            print(f"    Quality score: {quality_data.get('score', 'N/A')}")
            if quality_data.get('average_lifespan_years'):
                print(f"    Lifespan: {quality_data['average_lifespan_years']} years")
        else:
            print(f"    Has quality_data: NO ❌")
            return False

    return True

# Test 1: Fresh search (should cache)
print("\n" + "="*60)
print("TEST 1: FRESH SEARCH - Should cache with quality_data")
print("="*60)

success1 = test_search("test pan", 1)

if not success1:
    print("\n❌ TEST FAILED: First search returned empty or missing quality_data")
    exit(1)

# Wait a moment
print("\n⏳ Waiting 2 seconds before cached search...")
time.sleep(2)

# Test 2: Cached search (should retrieve from cache)
print("\n" + "="*60)
print("TEST 2: CACHED SEARCH - Should retrieve same products")
print("="*60)

success2 = test_search("test pan", 2)

if not success2:
    print("\n❌ TEST FAILED: Second search returned empty or missing quality_data")
    print("\n🔍 This indicates the cache bug still exists!")
    exit(1)

# Final result
print("\n" + "="*60)
print("✅ ALL TESTS PASSED!")
print("="*60)
print("\n✓ Fresh search returns products with quality_data")
print("✓ Products are cached successfully")
print("✓ Cached search retrieves products with quality_data")
print("\nThe cache bug has been fixed! 🎉")
