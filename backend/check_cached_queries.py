"""Check what parameters cached queries have"""
import os
from supabase import create_client

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_ANON_KEY")

if not url or not key:
    print("❌ Environment variables not set")
    exit(1)

client = create_client(url, key)

# Get recent cached queries with their parameters
result = client.table('search_queries').select(
    'id, original_query, tier_preference, max_price, access_count, created_at'
).order('created_at', desc=True).limit(10).execute()

if result.data:
    print(f"\nFound {len(result.data)} recent cached queries:\n")
    print(f"{'Query':<20} {'Tier Pref':<15} {'Max Price':<12} {'Access Count':<15} {'Created At':<30}")
    print("-" * 100)
    for query in result.data:
        tier_pref = query.get('tier_preference') or 'None'
        max_price = query.get('max_price') or 'None'
        access_count = query.get('access_count', 0)
        created_at = query.get('created_at', '')[:19]  # Truncate timestamp
        print(f"{query['original_query']:<20} {tier_pref:<15} {str(max_price):<12} {access_count:<15} {created_at:<30}")
else:
    print("No cached queries found")
