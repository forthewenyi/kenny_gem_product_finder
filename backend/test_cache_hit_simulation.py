"""
Test script to simulate cache hits and verify access_count increments.
"""

import os
import asyncio
from database_service import DatabaseService
from dotenv import load_dotenv

load_dotenv()

async def test_cache_hits():
    """Simulate multiple cache hits to test access_count tracking"""
    db = DatabaseService()

    print("\n" + "="*60)
    print("🧪 CACHE HIT SIMULATION TEST")
    print("="*60)

    query = "air fryer"

    print(f"\n📌 Testing cache hits for query: '{query}'")
    print("-" * 60)

    # Simulate 6 cache hits to see TTL progression
    for i in range(1, 7):
        print(f"\n🔍 Cache hit attempt #{i}:")
        result = await db.get_cached_search(query)

        if result:
            print(f"   ✅ Cache HIT!")
        else:
            print(f"   ❌ Cache MISS (or expired)")

    print("\n" + "="*60)
    print("📊 FINAL STATISTICS")
    print("="*60)

    # Show final statistics
    stats = db.client.table("cache_statistics").select("*").execute()
    if stats.data and len(stats.data) > 0:
        data = stats.data[0]
        print(f"\n✅ Cache Statistics:")
        print(f"  Total Cached Queries: {data.get('total_cached_queries', 0)}")
        print(f"  Total Cache Hits: {data.get('total_cache_hits') or 0}")

        avg_hits = data.get('avg_hits_per_query')
        if avg_hits is not None:
            print(f"  Average Hits Per Query: {float(avg_hits):.2f}")
        else:
            print(f"  Average Hits Per Query: 0.00")

        hit_rate = data.get('cache_hit_rate_percent')
        if hit_rate is not None:
            print(f"  Cache Hit Rate: {float(hit_rate):.2f}%")
        else:
            print(f"  Cache Hit Rate: 0.00%")

        print(f"\n📈 Query Distribution:")
        print(f"  Popular Queries (5+ accesses, 168h TTL): {data.get('popular_queries', 0)}")
        print(f"  Niche Queries (2-4 accesses, 72h TTL): {data.get('niche_queries', 0)}")
        print(f"  Normal Queries (0-1 accesses, 24h TTL): {data.get('normal_queries', 0)}")

    # Show the specific query details
    print(f"\n📋 Query Details for '{query}':")
    searches = (
        db.client.table("search_queries")
        .select("original_query, access_count, created_at, last_accessed_at")
        .eq("original_query", query)
        .order("last_accessed_at", desc=True)
        .limit(1)
        .execute()
    )

    if searches.data:
        search = searches.data[0]
        access_count = search.get("access_count", 0)

        # Determine TTL
        if access_count >= 5:
            ttl = "168h (1 week)"
            tier = "POPULAR"
        elif access_count >= 2:
            ttl = "72h (3 days)"
            tier = "NICHE"
        else:
            ttl = "24h"
            tier = "NORMAL"

        print(f"  Tier: {tier}")
        print(f"  Access Count: {access_count}")
        print(f"  TTL: {ttl}")
        print(f"  Created: {search.get('created_at', '')[:19]}")
        print(f"  Last Accessed: {search.get('last_accessed_at', '')[:19]}")

        # Show progression
        print(f"\n🎯 TTL Progression:")
        if access_count >= 5:
            print(f"  ✅ Hit #1-2: 24h TTL (NORMAL)")
            print(f"  ✅ Hit #3: Upgraded to 72h TTL (NICHE)")
            print(f"  ✅ Hit #6: Upgraded to 168h TTL (POPULAR) ← Current!")
        elif access_count >= 2:
            print(f"  ✅ Hit #1-2: 24h TTL (NORMAL)")
            print(f"  ✅ Hit #3+: 72h TTL (NICHE) ← Current!")
        else:
            print(f"  ⏳ Hit #1-2: 24h TTL (NORMAL) ← Current")
            print(f"  ⏳ Hit #3: Will upgrade to 72h TTL (NICHE)")
            print(f"  ⏳ Hit #6: Will upgrade to 168h TTL (POPULAR)")

    print("\n" + "="*60)

if __name__ == "__main__":
    asyncio.run(test_cache_hits())
