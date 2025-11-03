#!/usr/bin/env python3
"""Verify database schema has all required fields"""

from database_service import DatabaseService
from dotenv import load_dotenv

load_dotenv()

db = DatabaseService()

print("🔍 Checking products table schema...")

# Required fields in new schema
required_fields = [
    "id", "name", "brand", "tier", "category",
    "price", "expected_lifespan_years", "cost_per_year", "cost_per_day",
    "why_its_a_gem", "key_features", "materials", "characteristics",
    "trade_offs", "best_for", "web_sources", "maintenance_level",
    "created_at", "updated_at"
]

# Try to select all fields
try:
    result = db.client.table("products").select("*").limit(1).execute()

    if result.data and len(result.data) > 0:
        product = result.data[0]
        existing_fields = list(product.keys())

        print(f"\n✅ Found {len(existing_fields)} fields in products table:")
        for field in sorted(existing_fields):
            print(f"   - {field}")

        missing_fields = [f for f in required_fields if f not in existing_fields]
        extra_fields = [f for f in existing_fields if f not in required_fields and f != "id"]

        if missing_fields:
            print(f"\n⚠️  Missing fields (need to add):")
            for field in missing_fields:
                print(f"   - {field}")

        if extra_fields:
            print(f"\n📝 Extra fields (can keep or remove):")
            for field in extra_fields:
                print(f"   - {field}")

        if not missing_fields:
            print("\n✅ Schema is complete! All required fields present.")
        else:
            print("\n⚠️  Schema needs migration. Run supabase_schema_migration.sql")
    else:
        print("⚠️  Products table is empty, cannot verify schema structure")
        print("   This is okay - schema might be correct. Try a search to populate it.")

except Exception as e:
    print(f"❌ Error checking schema: {e}")
    print("\nThe products table might not exist or have a different schema.")
    print("Run supabase_schema_migration.sql in your Supabase SQL Editor")
