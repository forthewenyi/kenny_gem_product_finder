#!/usr/bin/env python3
"""
Update the popular_search_terms table category constraint to include new categories
"""
import os
from supabase import create_client

def main():
    # Connect to Supabase
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY") or os.getenv("SUPABASE_ANON_KEY")

    if not url or not key:
        print("Error: SUPABASE_URL and SUPABASE_KEY environment variables must be set")
        return False

    client = create_client(url, key)

    # Drop the old constraint and add the new one
    sql = """
    -- Drop the old constraint
    ALTER TABLE popular_search_terms
    DROP CONSTRAINT IF EXISTS popular_search_terms_category_check;

    -- Add new constraint with all 5 categories
    ALTER TABLE popular_search_terms
    ADD CONSTRAINT popular_search_terms_category_check
    CHECK (category IN ('cookware', 'knives', 'bakeware', 'small_appliances', 'kitchen_tools'));
    """

    try:
        print("Updating category constraint...")
        # Execute the SQL
        result = client.rpc('exec_sql', {'query': sql}).execute()
        print("✅ Constraint updated successfully!")
        return True
    except Exception as e:
        # If RPC doesn't work, try direct approach
        print(f"Note: {e}")
        print("\nPlease run this SQL manually in Supabase SQL Editor:")
        print("="*80)
        print(sql)
        print("="*80)
        return False

if __name__ == "__main__":
    main()
