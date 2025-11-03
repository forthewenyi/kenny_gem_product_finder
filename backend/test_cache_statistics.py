"""
Test script to view cache statistics and verify dynamic TTL is working.
"""

import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

def view_cache_statistics():
    """View cache statistics from the cache_statistics view"""
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_ANON_KEY")

    if not url or not key:
        print("❌ SUPABASE_URL and SUPABASE_ANON_KEY must be set")
        return

    client = create_client(url, key)

    print("\n" + "="*60)
    print("📊 CACHE STATISTICS")
    print("="*60)

    try:
        # Query cache_statistics view
        stats = client.table("cache_statistics").select("*").execute()

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
        else:
            print("⚠️  No cache statistics available (cache may be empty)")

    except Exception as e:
        print(f"❌ Error querying cache statistics: {e}")
        print("\n⚠️  Make sure you've run add_cache_tracking.sql in Supabase!")
        return

    print("\n" + "="*60)
    print("📋 RECENT SEARCHES")
    print("="*60)

    try:
        # Show recent searches with access counts
        searches = (
            client.table("search_queries")
            .select("original_query, access_count, created_at, last_accessed_at")
            .order("last_accessed_at", desc=True)
            .limit(10)
            .execute()
        )

        if searches.data:
            print("\nRecent searches (sorted by last access):\n")
            for search in searches.data:
                query = search.get("original_query", "")
                access_count = search.get("access_count", 0)
                created = search.get("created_at", "")[:10]
                accessed = search.get("last_accessed_at", "")[:10]

                # Determine TTL based on access count
                if access_count >= 5:
                    ttl = "168h (1 week)"
                    tier = "POPULAR"
                elif access_count >= 2:
                    ttl = "72h (3 days)"
                    tier = "NICHE"
                else:
                    ttl = "24h"
                    tier = "NORMAL"

                print(f"  [{tier}] \"{query}\"")
                print(f"    Access count: {access_count} | TTL: {ttl}")
                print(f"    Created: {created} | Last accessed: {accessed}")
                print()
        else:
            print("  No searches found in cache")

    except Exception as e:
        print(f"❌ Error querying recent searches: {e}")

    print("="*60)
    print("\n💡 TIP: Search the same query multiple times to see access_count increase!")
    print("   - First search (access_count=0): 24h TTL")
    print("   - Second search (access_count=1): 24h TTL")
    print("   - Third search (access_count=2): 72h TTL (niche)")
    print("   - Fifth+ search (access_count=5+): 168h TTL (popular)")
    print()

if __name__ == "__main__":
    view_cache_statistics()
