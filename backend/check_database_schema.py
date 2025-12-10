#!/usr/bin/env python3
"""
Check if database schema needs migration
Verifies if trade_offs → drawbacks migration has been run
"""

from database_service import DatabaseService
from dotenv import load_dotenv
import sys

load_dotenv()

print("\n" + "="*80)
print("🔍 DATABASE SCHEMA VERIFICATION")
print("="*80 + "\n")

try:
    db = DatabaseService()

    # Check if products table exists and what columns it has
    print("📋 Checking products table schema...")

    # Try to get one product to see the column structure
    result = db.client.table("products").select("*").limit(1).execute()

    if result.data and len(result.data) > 0:
        product = result.data[0]
        columns = list(product.keys())

        print(f"\n✅ Found products table with {len(columns)} columns\n")

        # Check for old field names
        has_trade_offs = "trade_offs" in columns
        has_drawbacks = "drawbacks" in columns
        has_why_gem = "why_gem" in columns
        has_why_its_a_gem = "why_its_a_gem" in columns

        print("🔍 Field Name Check:")
        print("-" * 80)

        # Check trade_offs vs drawbacks
        if has_trade_offs and not has_drawbacks:
            print("❌ NEEDS MIGRATION: Found 'trade_offs' column (old name)")
            print("   → Need to rename to 'drawbacks'")
            needs_migration = True
        elif has_drawbacks and not has_trade_offs:
            print("✅ CORRECT: Found 'drawbacks' column (new name)")
            needs_migration = False
        elif has_trade_offs and has_drawbacks:
            print("⚠️  WARNING: Found BOTH 'trade_offs' and 'drawbacks' columns")
            print("   → Database may be in inconsistent state")
            needs_migration = True
        else:
            print("⚠️  WARNING: Neither 'trade_offs' nor 'drawbacks' found")
            needs_migration = True

        # Check why_gem vs why_its_a_gem
        print()
        if has_why_gem and not has_why_its_a_gem:
            print("⚠️  INFO: Found 'why_gem' column (database uses shorter name)")
            print("   → This is OK - backend code translates from 'why_its_a_gem'")
        elif has_why_its_a_gem:
            print("✅ CORRECT: Found 'why_its_a_gem' column")

        # Show all columns
        print("\n📝 All columns in products table:")
        print("-" * 80)
        for col in sorted(columns):
            marker = ""
            if col == "trade_offs":
                marker = " ⬅ OLD NAME (need to rename)"
            elif col == "drawbacks":
                marker = " ⬅ NEW NAME (correct)"
            print(f"   {col}{marker}")

        # Check if there's any cached data
        count_result = db.client.table("products").select("id", count="exact").execute()
        product_count = count_result.count if hasattr(count_result, 'count') else len(count_result.data)

        print(f"\n📊 Database Statistics:")
        print("-" * 80)
        print(f"   Total products cached: {product_count}")

        # Final recommendation
        print("\n" + "="*80)
        if needs_migration:
            print("⚠️  MIGRATION REQUIRED")
            print("="*80)
            print("\n📝 Action Required:")
            print("   1. Open your Supabase SQL Editor")
            print("   2. Run the migration script: rename_trade_offs_to_drawbacks.sql")
            print("   3. This will rename 'trade_offs' → 'drawbacks'")
            print("   4. Re-run this script to verify\n")
            sys.exit(1)
        else:
            print("✅ DATABASE SCHEMA IS UP TO DATE")
            print("="*80)
            print("\n✅ No migration needed!")
            print("✅ Database is aligned with backend code")
            print("✅ Field names are correct: 'drawbacks' (not 'trade_offs')\n")
            sys.exit(0)

    else:
        print("⚠️  No products found in database")
        print("   Database may be empty - schema check not possible")
        sys.exit(0)

except Exception as e:
    print(f"\n❌ Error checking database: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
