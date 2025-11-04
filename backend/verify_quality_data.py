"""Verify quality_data column was added successfully"""
import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_ANON_KEY")
client = create_client(url, key)

print("🔍 Checking for quality_data column in products table...")

try:
    # Try to query the quality_data column
    result = client.table("products")\
        .select("id, name, quality_data")\
        .limit(1)\
        .execute()

    print("\n✅ SUCCESS: quality_data column exists!")

    if result.data:
        product = result.data[0]
        print(f"\nSample product: {product.get('name', 'Unknown')}")

        quality_data = product.get('quality_data')
        if quality_data:
            print(f"Has quality_data: YES")
            print(f"Keys: {list(quality_data.keys())}")
        else:
            print(f"Has quality_data: No (column exists but empty - will be populated on next search)")
    else:
        print("\nNo products in table yet (column exists and ready)")

except Exception as e:
    print(f"\n❌ ERROR: {e}")
    print("\nThe quality_data column might not exist yet.")
    print("Please run the SQL migration in Supabase SQL Editor.")
