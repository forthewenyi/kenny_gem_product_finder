"""
Verify that durability_data and practical_metrics columns were added successfully.
"""

import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

def verify_schema():
    """Verify the database schema has the new columns"""
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_ANON_KEY")

    if not url or not key:
        print("❌ SUPABASE_URL and SUPABASE_ANON_KEY must be set")
        return

    client = create_client(url, key)

    print("\n" + "="*60)
    print("✅ VERIFYING DATABASE SCHEMA")
    print("="*60)

    try:
        # Insert a test product with the new fields
        test_product = {
            "name": "Test Product Schema Verification",
            "brand": "Test Brand",
            "tier": "good",
            "category": "test",
            "price": 100.0,
            "expected_lifespan_years": 5.0,
            "cost_per_year": 20.0,
            "cost_per_day": 0.05,
            "why_its_a_gem": "Test product",
            "key_features": ["Feature 1"],
            "characteristics": ["Characteristic 1"],
            "durability_data": {
                "score": 75,
                "average_lifespan_years": 5.0,
                "still_working_after_5years_percent": 80,
                "total_user_reports": 100,
                "common_failure_points": ["test failure"],
                "repairability_score": 70,
                "material_quality_indicators": ["good quality"],
                "data_sources": ["https://example.com"]
            },
            "practical_metrics": {
                "cleaning_time_minutes": 10,
                "cleaning_details": "Easy to clean",
                "setup_time": "Ready",
                "setup_details": "No setup needed",
                "learning_curve": "Low",
                "learning_details": "Easy to use",
                "maintenance_level": "Low",
                "maintenance_details": "Minimal maintenance",
                "weight_lbs": 5.0,
                "weight_notes": "Lightweight",
                "dishwasher_safe": True,
                "oven_safe": False,
                "oven_max_temp": None
            }
        }

        print("\n1️⃣  Inserting test product with durability_data and practical_metrics...")
        result = client.table("products").insert(test_product).execute()

        if result.data and len(result.data) > 0:
            print("   ✅ Test product inserted successfully!")
            test_id = result.data[0]["id"]

            # Retrieve the test product
            print("\n2️⃣  Retrieving test product...")
            retrieved = client.table("products").select("*").eq("id", test_id).execute()

            if retrieved.data and len(retrieved.data) > 0:
                product = retrieved.data[0]
                print("   ✅ Test product retrieved successfully!")

                # Check durability_data
                if product.get("durability_data"):
                    dd = product["durability_data"]
                    print(f"\n   ✅ durability_data column exists:")
                    print(f"      - score: {dd.get('score')}")
                    print(f"      - average_lifespan_years: {dd.get('average_lifespan_years')}")
                    print(f"      - repairability_score: {dd.get('repairability_score')}")
                else:
                    print("   ❌ durability_data column missing or NULL")

                # Check practical_metrics
                if product.get("practical_metrics"):
                    pm = product["practical_metrics"]
                    print(f"\n   ✅ practical_metrics column exists:")
                    print(f"      - cleaning_time_minutes: {pm.get('cleaning_time_minutes')}")
                    print(f"      - weight_lbs: {pm.get('weight_lbs')}")
                    print(f"      - dishwasher_safe: {pm.get('dishwasher_safe')}")
                else:
                    print("   ❌ practical_metrics column missing or NULL")

            # Clean up test product
            print("\n3️⃣  Cleaning up test product...")
            client.table("products").delete().eq("id", test_id).execute()
            print("   ✅ Test product deleted")

            print("\n" + "="*60)
            print("🎉 SCHEMA VERIFICATION SUCCESSFUL!")
            print("="*60)
            print("\nThe database is ready to store:")
            print("  ✅ durability_data (score, lifespan, failure points, etc.)")
            print("  ✅ practical_metrics (cleaning, setup, weight, etc.)")
            print("\nYou can now search for products and cache will work correctly!")

        else:
            print("   ❌ Failed to insert test product")

    except Exception as e:
        print(f"\n❌ Schema verification failed: {e}")
        print("\nMake sure you ran the SQL migration:")
        print("  add_durability_and_practical_metrics_simple.sql")

    print("\n" + "="*60)

if __name__ == "__main__":
    verify_schema()
