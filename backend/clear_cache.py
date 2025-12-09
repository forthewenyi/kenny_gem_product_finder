"""Quick script to clear cache for specific queries"""
import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_ANON_KEY")
client = create_client(url, key)

# Delete ALL cached searches to test new agent logic
result = client.table("search_queries").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
print(f"Deleted {len(result.data)} cached entries (ALL)")

print("Cache cleared! Try searching again.")
