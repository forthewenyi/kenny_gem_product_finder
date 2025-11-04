"""Run database migration to add real_search_metrics column"""
import os
from supabase import create_client

def run_migration():
    # Load Supabase credentials
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_ANON_KEY")

    if not url or not key:
        print("❌ Error: SUPABASE_URL and SUPABASE_ANON_KEY must be set")
        print("Make sure to load your .env file first")
        return False

    client = create_client(url, key)

    print("🔄 Running migration: add_real_search_metrics_column.sql")
    print()

    # Read the SQL migration file
    with open('add_real_search_metrics_column.sql', 'r') as f:
        sql = f.read()

    try:
        print("📋 Migration SQL:")
        print("=" * 60)
        print(sql)
        print("=" * 60)
        print()
        print("⚠️  NOTE: The Supabase Python client doesn't support direct SQL execution.")
        print()
        print("Please run this migration manually:")
        print("1. Go to https://supabase.com")
        print("2. Select your project")
        print("3. Go to SQL Editor")
        print("4. Paste the SQL above")
        print("5. Click 'Run'")
        print()
        print("After running the migration, existing cache entries will work fine.")
        print("New searches will start caching real_search_metrics automatically.")

        return True

    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False

if __name__ == "__main__":
    run_migration()
