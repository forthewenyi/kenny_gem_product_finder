#!/usr/bin/env python3
"""Test cache hit for air fryer"""

import requests
import time

print("Testing cache hit for 'air fryer' query...")
print("-" * 60)

start = time.time()
response = requests.post(
    "http://localhost:8000/api/search",
    json={"query": "air fryer", "context": {}},
    timeout=10
)
duration = time.time() - start

if response.status_code == 200:
    data = response.json()
    is_cached = data["search_metadata"].get("cached", False)
    product_count = (
        len(data["results"]["good"]) +
        len(data["results"]["better"]) +
        len(data["results"]["best"])
    )

    print(f"\n✅ SUCCESS!")
    print(f"   Duration: {duration:.2f} seconds")
    print(f"   Cached: {is_cached}")
    print(f"   Products returned: {product_count}")
    print(f"   Processing time: {data['processing_time_seconds']:.2f}s")

    if is_cached and duration < 5:
        print(f"\n🚀 CACHE IS WORKING PERFECTLY!")
        print(f"   Search returned in {duration:.2f}s instead of ~30s")
        print(f"   That's approximately {30/duration:.0f}x faster!")
    elif is_cached:
        print(f"\n✅ Cache working but database is slow")
        print(f"   Still faster than fresh search though")
    else:
        print(f"\n⚠️  Cache miss - this should have been a cache hit")
else:
    print(f"❌ Failed: HTTP {response.status_code}")
    print(response.text)
