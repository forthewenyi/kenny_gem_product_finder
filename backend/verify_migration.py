"""Verify that the real_search_metrics column exists in search_queries table"""
import os
from supabase import create_client
from dotenv import load_dotenv

def verify_migration():
    # Load environment variables from .env file
    load_dotenv()

    # Load Supabase credentials
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_ANON_KEY")

    if not url or not key:
        print("❌ Error: SUPABASE_URL and SUPABASE_ANON_KEY must be set")
        return False

    client = create_client(url, key)

    print("🔍 Checking if real_search_metrics column exists...")
    print()

    try:
        # Try to query the column - if it doesn't exist, this will fail
        result = client.table("search_queries").select("id, real_search_metrics").limit(1).execute()

        print("✅ SUCCESS: real_search_metrics column exists!")
        print()

        if result.data:
            print(f"Found {len(result.data)} search query in database")
            if result.data[0].get("real_search_metrics"):
                print("✅ Column has data:", result.data[0]["real_search_metrics"])
            else:
                print("⚠️  Column exists but is NULL (expected for old cache entries)")
        else:
            print("📋 No search queries in database yet")

        print()
        print("✅ Migration was successfully applied!")
        return True

    except Exception as e:
        error_msg = str(e)
        if "does not exist" in error_msg or "column" in error_msg.lower():
            print("❌ MIGRATION NOT RUN: real_search_metrics column does not exist")
            print()
            print("Please run the migration in Supabase SQL Editor:")
            print("1. Go to https://supabase.com")
            print("2. Select your project")
            print("3. Go to SQL Editor")
            print("4. Paste the SQL from add_real_search_metrics_column.sql")
            print("5. Click 'Run'")
        else:
            print(f"❌ Error checking column: {e}")
        return False

if __name__ == "__main__":
    verify_migration()
