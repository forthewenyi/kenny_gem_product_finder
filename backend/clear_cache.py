"""Quick script to clear cache for specific queries"""
import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_ANON_KEY")
client = create_client(url, key)

# Delete all cached searches containing "air fryer"
result = client.table("search_queries").delete().ilike("normalized_query", "%air fryer%").execute()
print(f"Deleted {len(result.data)} cached entries for 'air fryer'")

print("Cache cleared! Try searching again.")
