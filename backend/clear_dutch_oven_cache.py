"""Clear the bad 'dutch oven' cache entry"""
import os
from supabase import create_client

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_ANON_KEY")

if not url or not key:
    print("❌ Environment variables not set")
    exit(1)

client = create_client(url, key)

# Delete the dutch oven cache entry
try:
    # First, find the search_query id
    query_result = client.table('search_queries').select('id').eq('normalized_query', 'dutch oven').execute()

    if query_result.data:
        for query in query_result.data:
            query_id = query['id']
            print(f"Found query ID: {query_id}")

            # Delete related product_search_results first (foreign key constraint)
            client.table('product_search_results').delete().eq('search_query_id', query_id).execute()
            print(f"✓ Deleted product_search_results for query_id: {query_id}")

            # Delete the search_queries entry
            client.table('search_queries').delete().eq('id', query_id).execute()
            print(f"✓ Deleted search_queries entry for: dutch oven")
    else:
        print("No 'dutch oven' cache found")

    print("\n✓ Cache cleared successfully!")
except Exception as e:
    print(f"❌ Error clearing cache: {e}")
