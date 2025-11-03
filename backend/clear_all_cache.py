"""
Clear ALL cached data to force fresh searches with new schema.
"""

import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

def clear_all_cache():
    """Clear all cached searches and products"""
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_ANON_KEY")

    if not url or not key:
        print("❌ SUPABASE_URL and SUPABASE_ANON_KEY must be set")
        return

    client = create_client(url, key)

    print("\n" + "="*60)
    print("🗑️  CLEARING ALL CACHE")
    print("="*60)

    try:
        # Get count before deletion
        search_count = client.table("search_queries").select("id", count="exact").execute()
        product_count = client.table("products").select("id", count="exact").execute()

        print(f"\n📊 Current cache state:")
        print(f"  Search queries: {search_count.count}")
        print(f"  Products: {product_count.count}")

        # Delete all search queries (cascade deletes product_search_results)
        print(f"\n🗑️  Deleting all search queries...")
        client.table("search_queries").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()

        # Delete all products
        print(f"🗑️  Deleting all products...")
        client.table("products").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()

        print(f"\n✅ Cache cleared!")
        print(f"   - All search queries deleted")
        print(f"   - All products deleted")
        print(f"   - Next search will fetch fresh data with new schema")

    except Exception as e:
        print(f"\n❌ Error clearing cache: {e}")

    print("\n" + "="*60)

if __name__ == "__main__":
    clear_all_cache()
