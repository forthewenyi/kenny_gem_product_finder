#!/usr/bin/env python3
"""Clear air fryer cache to force fresh search with new durability validation"""

from database_service import DatabaseService
from dotenv import load_dotenv

load_dotenv()

db = DatabaseService()

print("🗑️  Clearing 'air fryer' cache...\n")

# Get the search query ID
search_query = db.client.table("search_queries").select("id").eq("original_query", "air fryer").execute()

if search_query.data:
    search_id = search_query.data[0]["id"]
    print(f"Found search query: {search_id}")

    # Delete product-search links (CASCADE should handle this, but being explicit)
    try:
        db.client.table("product_search_results").delete().eq("search_query_id", search_id).execute()
        print("✓ Deleted product-search links")
    except Exception as e:
        print(f"⚠️  Error deleting links: {e}")

    # Delete the search query (this will cascade delete products if they're only linked to this search)
    try:
        db.client.table("search_queries").delete().eq("id", search_id).execute()
        print("✓ Deleted search query")
    except Exception as e:
        print(f"❌ Error deleting search query: {e}")

    # Optionally clean up orphaned products (products not linked to any search)
    try:
        # Get all product IDs
        all_products = db.client.table("products").select("id").execute()
        product_ids = [p["id"] for p in all_products.data]

        # Get product IDs that are linked to searches
        linked_products = db.client.table("product_search_results").select("product_id").execute()
        linked_ids = set(p["product_id"] for p in linked_products.data)

        # Delete orphaned products
        orphaned_ids = [pid for pid in product_ids if pid not in linked_ids]

        if orphaned_ids:
            for orphan_id in orphaned_ids:
                db.client.table("products").delete().eq("id", orphan_id).execute()
            print(f"✓ Cleaned up {len(orphaned_ids)} orphaned products")
        else:
            print("✓ No orphaned products to clean up")

    except Exception as e:
        print(f"⚠️  Error cleaning up products: {e}")

    print("\n" + "="*60)
    print("✅ CACHE CLEARED!")
    print("\nNext steps:")
    print("1. Go to http://localhost:3000")
    print("2. Search for 'air fryer' again")
    print("3. Wait ~30-40 seconds for fresh search")
    print("4. Check durability scores - should now show validated data")
    print("\nThe new search will use:")
    print("• 11 queries (including 3 durability-focused queries)")
    print("• Conservative lifespan estimates from research")
    print("• Source evidence for all durability claims")

else:
    print("❌ No 'air fryer' cache found")
    print("\nYou can search for 'air fryer' to create new cached data")
    print("with the improved durability validation.")
