#!/usr/bin/env python3
"""
Test the actual API endpoint to verify complete data flow
"""

import asyncio
import httpx
import json

API_URL = "http://localhost:8000/api/search"

async def test_api_search():
    """Test actual API search endpoint"""

    print("=" * 80)
    print("🔍 TESTING API ENDPOINT DATA FLOW")
    print("=" * 80)
    print()

    search_query = {
        "query": "chef knife",
        "tier_preference": None,
        "max_price": None,
        "context": {},
        "characteristics": {}
    }

    print(f"📡 Sending request to: {API_URL}")
    print(f"📋 Query: {search_query['query']}")
    print()

    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(API_URL, json=search_query)

            if response.status_code != 200:
                print(f"❌ API returned status {response.status_code}")
                print(f"Response: {response.text[:500]}")
                return False

            data = response.json()

            print("✅ API Response received")
            print()

            # Check top-level structure
            print("📋 TOP-LEVEL STRUCTURE")
            print("-" * 80)
            for key in data.keys():
                print(f"   ✓ {key}")
            print()

            # Check if results exist
            if 'results' not in data:
                print("❌ No 'results' field in response")
                return False

            results = data['results']

            # Collect all products
            all_products = []
            for tier in ['good', 'better', 'best']:
                if tier in results:
                    products = results[tier]
                    all_products.extend(products)
                    print(f"   {tier.upper()}: {len(products)} products")

            print()

            if not all_products:
                print("❌ No products found in results")
                return False

            print(f"📦 Total products: {len(all_products)}")
            print()

            # Check first product for all VALUE framework fields
            product = all_products[0]

            print("📋 CHECKING PRODUCT FIELDS (VALUE Framework)")
            print("-" * 80)
            print(f"Product: {product.get('name', 'Unknown')}")
            print()

            # VALUE framework field checklist
            value_fields = {
                "PRODUCT": [
                    "name", "brand", "category", "materials",
                    "key_features", "why_its_a_gem", "quality_data"
                ],
                "SERVICE": [
                    "practical_metrics", "maintenance_level", "drawbacks"
                ],
                "EQUITY": [
                    "professional_reviews", "best_for", "web_sources", "reddit_mentions"
                ],
                "PRICE & ACTION": [
                    "value_metrics", "purchase_links", "tier"
                ],
                "FILTERING": [
                    "characteristics"
                ]
            }

            all_present = True

            for category, fields in value_fields.items():
                print(f"\n🔹 {category}")
                for field in fields:
                    if field in product:
                        value = product[field]
                        if isinstance(value, dict):
                            preview = f"dict with {len(value)} keys"
                        elif isinstance(value, list):
                            preview = f"list with {len(value)} items"
                        else:
                            preview = str(value)[:50] if value else "None"
                        print(f"   ✅ {field:25} = {preview}")
                    else:
                        print(f"   ❌ {field:25} = MISSING")
                        all_present = False

            print()

            # Check nested structures
            print("📋 CHECKING NESTED STRUCTURES")
            print("-" * 80)

            # value_metrics
            if 'value_metrics' in product:
                vm = product['value_metrics']
                print("\n💰 value_metrics:")
                for key in ['upfront_price', 'expected_lifespan_years', 'cost_per_year', 'cost_per_day']:
                    if key in vm:
                        print(f"   ✅ {key:30} = {vm[key]}")
                    else:
                        print(f"   ❌ {key:30} = MISSING")
                        all_present = False

            # quality_data
            if 'quality_data' in product and product['quality_data']:
                qd = product['quality_data']
                print("\n🎯 quality_data:")
                for key in ['score', 'average_lifespan_years', 'still_working_after_5years_percent', 'repairability_score']:
                    if key in qd:
                        print(f"   ✅ {key:40} = {qd[key]}")
                    else:
                        print(f"   ❌ {key:40} = MISSING")

            # practical_metrics
            if 'practical_metrics' in product and product['practical_metrics']:
                pm = product['practical_metrics']
                print("\n🛠️  practical_metrics:")
                for key in ['learning_curve', 'maintenance_level', 'cleaning_details', 'setup_time']:
                    if key in pm:
                        value = str(pm[key])[:50]
                        print(f"   ✅ {key:30} = {value}")
                    else:
                        print(f"   ❌ {key:30} = MISSING")

            print()
            print("=" * 80)

            if all_present:
                print("✅ ALL VALUE FRAMEWORK FIELDS PRESENT")
                print()
                print("🎉 BACKEND → FRONTEND DATA FLOW IS COMPLETE!")
            else:
                print("⚠️  SOME FIELDS MISSING")
                print()
                print("❌ DATA FLOW HAS GAPS")

            print("=" * 80)

            # Save sample for inspection
            with open('/tmp/api_response_sample.json', 'w') as f:
                json.dump({
                    'sample_product': product,
                    'total_products': len(all_products),
                    'tiers': {k: len(v) for k, v in results.items()}
                }, f, indent=2)

            print()
            print("💾 Sample saved to: /tmp/api_response_sample.json")
            print()

            return all_present

    except Exception as e:
        print(f"❌ Error testing API: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_api_search())
    import sys
    sys.exit(0 if success else 1)
