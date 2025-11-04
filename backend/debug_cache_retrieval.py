"""Debug cache retrieval to see what's stored vs what's returned"""
import os
from supabase import create_client
from dotenv import load_dotenv
import json

load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_ANON_KEY")
client = create_client(url, key)

# Get the most recent "test pan" cache entry
print("🔍 Checking cache for 'test pan'...")
result = client.table("search_queries")\
    .select("*")\
    .ilike("normalized_query", "%pan%")\
    .order("created_at", desc=True)\
    .limit(1)\
    .execute()

if result.data:
    cache_entry = result.data[0]
    search_id = cache_entry["id"]

    print(f"\n✓ Found cache entry: {search_id}")
    print(f"  Query: {cache_entry['normalized_query']}")
    print(f"  Created: {cache_entry['created_at']}")
    print(f"  Access count: {cache_entry.get('access_count', 0)}")

    # Get linked products
    print(f"\n📦 Checking linked products...")
    products_result = client.table("product_search_results")\
        .select("*")\
        .eq("search_query_id", search_id)\
        .execute()

    print(f"  Found {len(products_result.data)} linked products in product_search_results table")

    if products_result.data:
        print("\n  First 3 products:")
        for i, prod in enumerate(products_result.data[:3]):
            product_data = prod.get("product_data", {})
            print(f"    {i+1}. {product_data.get('name', 'Unknown')}")
            print(f"       Tier: {prod.get('tier', 'N/A')}")
            print(f"       Price: ${product_data.get('price', 'N/A')}")
    else:
        print("  ⚠️  NO PRODUCTS LINKED!")
        print("\n  This is the bug - products were not saved to product_search_results table")
else:
    print("❌ No cache entry found for 'test pan'")
