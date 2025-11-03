#!/usr/bin/env python3
"""Test Supabase database connection and schema"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

try:
    from database_service import DatabaseService

    print("🔍 Testing Supabase connection...")
    print(f"URL: {os.getenv('SUPABASE_URL')}")
    print(f"Key: {os.getenv('SUPABASE_ANON_KEY')[:20]}...")

    # Initialize database service
    db = DatabaseService()
    print("✅ DatabaseService initialized successfully!")

    # Try to query the products table to check if schema exists
    try:
        response = db.client.table("products").select("id").limit(1).execute()
        print(f"✅ Products table exists! Found {len(response.data)} products")
    except Exception as e:
        print(f"⚠️  Products table may not exist or schema mismatch: {e}")
        print("\n📋 To create the schema, run the following SQL in your Supabase SQL Editor:")
        print("   File: supabase_schema_migration.sql")

    # Try to query search_queries table
    try:
        response = db.client.table("search_queries").select("id").limit(1).execute()
        print(f"✅ Search queries table exists! Found {len(response.data)} queries")
    except Exception as e:
        print(f"⚠️  Search queries table may not exist: {e}")

    print("\n✅ Database connection test complete!")

except Exception as e:
    print(f"❌ Database connection failed: {e}")
    print("\nPlease ensure:")
    print("1. SUPABASE_URL is set in .env")
    print("2. SUPABASE_ANON_KEY is set in .env")
    print("3. Supabase project is active")
    print("4. Run the SQL migration in supabase_schema_migration.sql")
