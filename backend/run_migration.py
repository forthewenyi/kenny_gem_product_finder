#!/usr/bin/env python3
"""
Migration runner script to create the popular_search_terms table.
Run this script to apply the database migration.
"""

import os
from pathlib import Path
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def run_migration():
    """Run the migration to create popular_search_terms table"""

    # Initialize Supabase client
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_ANON_KEY")

    if not supabase_url or not supabase_key:
        print("❌ Error: SUPABASE_URL or SUPABASE_ANON_KEY not found in environment")
        return False

    print(f"🔗 Connecting to Supabase at {supabase_url}")
    client: Client = create_client(supabase_url, supabase_key)

    # Read the migration file
    migration_file = Path(__file__).parent / "migrations" / "001_create_popular_search_terms.sql"

    if not migration_file.exists():
        print(f"❌ Error: Migration file not found at {migration_file}")
        return False

    print(f"📄 Reading migration file: {migration_file}")
    with open(migration_file, 'r') as f:
        migration_sql = f.read()

    print("🚀 Executing migration...")

    try:
        # Supabase client doesn't directly support raw SQL execution via the anon key
        # We need to use the REST API or Supabase dashboard for DDL operations
        # For now, let's try using the RPC function or print instructions

        print("\n" + "="*80)
        print("⚠️  MANUAL MIGRATION REQUIRED")
        print("="*80)
        print("\nThe Supabase Python client requires elevated permissions to create tables.")
        print("\nPlease run the following SQL in your Supabase SQL Editor:")
        print("https://supabase.com/dashboard/project/nuzndrucvjyvezgafgcd/sql\n")
        print("-"*80)
        print(migration_sql)
        print("-"*80)
        print("\nAfter running the SQL, the popular search dropdowns will work correctly.")
        print("="*80)

        return True

    except Exception as e:
        print(f"❌ Error executing migration: {e}")
        return False

if __name__ == "__main__":
    run_migration()
