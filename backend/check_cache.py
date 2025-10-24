"""Check what's in the cache"""
import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_ANON_KEY")
client = create_client(url, key)

# Get all cached searches
result = client.table("search_queries").select("*").execute()
print(f"Found {len(result.data)} cached queries:")
for item in result.data:
    print(f"  - {item.get('normalized_query')} (id: {item.get('id')})")
