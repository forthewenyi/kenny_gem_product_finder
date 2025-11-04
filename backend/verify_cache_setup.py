"""
Verify cache setup and database schema for Kenny Gem Finder.
This script checks:
1. Database connection
2. Required tables exist
3. Required columns exist (including cache tracking fields)
4. Cache functionality works
"""

import asyncio
import os
from database_service import DatabaseService
from supabase import create_client

async def verify_cache_setup():
    print("=" * 60)
    print("CACHE SETUP VERIFICATION")
    print("=" * 60)

    # Step 1: Check database connection
    print("\n1️⃣  Checking database connection...")
    try:
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_ANON_KEY")

        if not url or not key:
            print("❌ SUPABASE_URL or SUPABASE_ANON_KEY not set in environment")
            return

        client = create_client(url, key)
        print("✓ Database connection successful")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return

    # Step 2: Check required tables exist
    print("\n2️⃣  Checking required tables...")
    required_tables = ['search_queries', 'products', 'product_search_results']

    for table in required_tables:
        try:
            # Try to query the table with a limit of 0 to just check existence
            result = client.table(table).select("*").limit(0).execute()
            print(f"✓ Table '{table}' exists")
        except Exception as e:
            print(f"❌ Table '{table}' missing or inaccessible: {e}")

    # Step 3: Check search_queries has access_count column
    print("\n3️⃣  Checking search_queries schema...")
    try:
        # Try to select access_count field
        result = client.table('search_queries').select('id, access_count').limit(1).execute()
        print("✓ Column 'access_count' exists in search_queries")
    except Exception as e:
        print(f"⚠️  Column 'access_count' missing from search_queries")
        print(f"   You need to run: backend/add_cache_tracking.sql")
        print(f"   Error: {e}")

    # Step 4: Check products has durability_data and practical_metrics columns
    print("\n4️⃣  Checking products schema...")
    try:
        result = client.table('products').select('id, durability_data, practical_metrics').limit(1).execute()
        print("✓ Columns 'durability_data' and 'practical_metrics' exist in products")
    except Exception as e:
        print(f"⚠️  Columns 'durability_data' or 'practical_metrics' missing from products")
        print(f"   You need to run: backend/add_durability_and_practical_metrics_simple.sql")
        print(f"   Error: {e}")

    # Step 5: Check DatabaseService initialization
    print("\n5️⃣  Checking DatabaseService...")
    try:
        db_service = DatabaseService()
        print("✓ DatabaseService initialized successfully")
        print(f"   Cache TTL settings:")
        print(f"   - Popular queries (5+ hits): {db_service.cache_ttl_popular_hours} hours")
        print(f"   - Niche queries (2-4 hits): {db_service.cache_ttl_niche_hours} hours")
        print(f"   - Normal queries (0-1 hits): {db_service.cache_ttl_normal_hours} hours")
    except Exception as e:
        print(f"❌ DatabaseService initialization failed: {e}")
        return

    # Step 6: Test cache read/write (dry run - don't actually cache)
    print("\n6️⃣  Testing cache functionality...")
    try:
        # Test cache read (should return None for non-existent query)
        test_query = "test_cache_verification_12345"
        cached = await db_service.get_cached_search(
            query=test_query,
            tier_preference=None,
            max_price=None
        )

        if cached is None:
            print("✓ Cache read test passed (no cache hit as expected)")
        else:
            print("⚠️  Unexpected cache hit for test query")

    except Exception as e:
        print(f"❌ Cache read test failed: {e}")

    # Step 7: Check existing cached queries
    print("\n7️⃣  Checking existing cache...")
    try:
        result = client.table('search_queries').select('id, original_query, access_count, created_at').order('created_at', desc=True).limit(5).execute()

        if result.data and len(result.data) > 0:
            print(f"✓ Found {len(result.data)} recent cached queries:")
            for query in result.data:
                access_count = query.get('access_count', 0)
                print(f"   - '{query['original_query']}' (accessed {access_count} times)")
        else:
            print("ℹ️  No cached queries found yet (this is normal for new setup)")
    except Exception as e:
        print(f"⚠️  Could not retrieve cached queries: {e}")

    print("\n" + "=" * 60)
    print("VERIFICATION COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(verify_cache_setup())
