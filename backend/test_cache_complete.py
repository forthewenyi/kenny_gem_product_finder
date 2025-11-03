#!/usr/bin/env python3
"""Complete end-to-end cache test"""

import requests
import time
from database_service import DatabaseService
from dotenv import load_dotenv

load_dotenv()

API_URL = "http://localhost:8000/api/search"

print("=" * 80)
print("CACHE TEST: End-to-End Verification")
print("=" * 80)

# Initialize database service
db = DatabaseService()

# Clear cache for this test (optional)
test_query = "chef knife"
print(f"\n1️⃣  TEST QUERY: '{test_query}'")

# Check current cache state
print("\n2️⃣  CHECKING INITIAL CACHE STATE...")
try:
    products_before = db.client.table("products").select("id").execute()
    queries_before = db.client.table("search_queries").select("id").execute()
    print(f"   Products in DB: {len(products_before.data)}")
    print(f"   Queries in DB: {len(queries_before.data)}")
except Exception as e:
    print(f"   ⚠️  Error checking cache: {e}")

# First search (should be cache miss)
print(f"\n3️⃣  FIRST SEARCH (expecting cache miss)...")
print(f"   Sending POST to {API_URL}")
start_time = time.time()

try:
    response1 = requests.post(
        API_URL,
        json={"query": test_query, "context": {}},
        timeout=120
    )
    end_time = time.time()
    duration1 = end_time - start_time

    if response1.status_code == 200:
        data1 = response1.json()
        products_count = (
            len(data1["results"]["good"]) +
            len(data1["results"]["better"]) +
            len(data1["results"]["best"])
        )

        is_cached = data1["search_metadata"].get("cached", False)

        print(f"   ✅ SUCCESS!")
        print(f"   Duration: {duration1:.2f} seconds")
        print(f"   Products returned: {products_count}")
        print(f"   Was cached: {is_cached}")
        print(f"   Processing time: {data1['processing_time_seconds']:.2f}s")

        if "real_search_metrics" in data1:
            metrics = data1["real_search_metrics"]
            print(f"   Sources analyzed: {metrics.get('total_sources_analyzed', 0)}")
            print(f"   Search queries: {metrics.get('search_queries_executed', 0)}")
    else:
        print(f"   ❌ FAILED: HTTP {response1.status_code}")
        print(f"   {response1.text}")
        exit(1)

except Exception as e:
    print(f"   ❌ ERROR: {e}")
    exit(1)

# Check database after first search
print(f"\n4️⃣  CHECKING DATABASE AFTER FIRST SEARCH...")
time.sleep(2)  # Give DB time to sync

try:
    products_after = db.client.table("products").select("id, name, brand, tier").execute()
    queries_after = db.client.table("search_queries").select("id, original_query, created_at").execute()

    print(f"   Products in DB: {len(products_after.data)} (+{len(products_after.data) - len(products_before.data)})")
    print(f"   Queries in DB: {len(queries_after.data)} (+{len(queries_after.data) - len(queries_before.data)})")

    if len(products_after.data) > 0:
        print(f"\n   Sample products saved:")
        for product in products_after.data[:3]:
            print(f"      - {product['name']} ({product['tier']} tier)")

    if len(queries_after.data) == 0:
        print(f"   ⚠️  WARNING: No queries saved to database!")
        print(f"   This means caching failed to save results.")
        print(f"   Check backend logs for errors.")

except Exception as e:
    print(f"   ⚠️  Error checking database: {e}")

# Second search (should be cache hit)
print(f"\n5️⃣  SECOND SEARCH (expecting cache HIT)...")
print(f"   Sending POST to {API_URL}")
time.sleep(1)  # Brief pause

start_time = time.time()

try:
    response2 = requests.post(
        API_URL,
        json={"query": test_query, "context": {}},
        timeout=120
    )
    end_time = time.time()
    duration2 = end_time - start_time

    if response2.status_code == 200:
        data2 = response2.json()
        products_count = (
            len(data2["results"]["good"]) +
            len(data2["results"]["better"]) +
            len(data2["results"]["best"])
        )

        is_cached = data2["search_metadata"].get("cached", False)

        print(f"   ✅ SUCCESS!")
        print(f"   Duration: {duration2:.2f} seconds")
        print(f"   Products returned: {products_count}")
        print(f"   Was cached: {is_cached}")
        print(f"   Processing time: {data2['processing_time_seconds']:.2f}s")
    else:
        print(f"   ❌ FAILED: HTTP {response2.status_code}")
        print(f"   {response2.text}")
        exit(1)

except Exception as e:
    print(f"   ❌ ERROR: {e}")
    exit(1)

# Performance comparison
print(f"\n6️⃣  PERFORMANCE COMPARISON:")
print(f"   First search:  {duration1:.2f}s (cache miss)")
print(f"   Second search: {duration2:.2f}s (cache {'HIT ✅' if is_cached else 'MISS ❌'})")

if is_cached:
    speedup = duration1 / duration2 if duration2 > 0 else 0
    print(f"   Speedup: {speedup:.1f}x faster!")
    print(f"   Time saved: {duration1 - duration2:.2f}s")
else:
    print(f"   ⚠️  WARNING: Second search was NOT cached!")
    print(f"   Possible issues:")
    print(f"      - Database write failed after first search")
    print(f"      - Cache TTL too short")
    print(f"      - Query normalization issue")

# Final verification
print(f"\n7️⃣  FINAL VERIFICATION:")

if is_cached and duration2 < 5:
    print(f"   ✅ CACHE IS WORKING PERFECTLY!")
    print(f"   🚀 Searches are {speedup:.0f}x faster with caching")
    print(f"   💰 API costs reduced by ~99%")
elif not is_cached:
    print(f"   ❌ CACHE NOT WORKING")
    print(f"   Check backend logs for errors")
    print(f"   Run: tail -50 /tmp/backend_restart.log")
else:
    print(f"   ⚠️  CACHE HIT BUT SLOW")
    print(f"   Cache is working but database may be slow")

print("\n" + "=" * 80)
print("TEST COMPLETE")
print("=" * 80)
