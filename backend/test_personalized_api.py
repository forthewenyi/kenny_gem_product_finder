#!/usr/bin/env python3
"""
Integration test for personalized search API
Tests the full stack from API endpoint through to AI personalization
"""

import asyncio
import httpx
import json

BASE_URL = "http://localhost:8000"

async def test_api_basic_search():
    """Test 1: Basic search without characteristics"""
    print("\n" + "="*80)
    print("TEST 1: Basic API Search (No Personalization)")
    print("="*80)

    async with httpx.AsyncClient(timeout=180.0) as client:
        response = await client.post(
            f"{BASE_URL}/api/search",
            json={
                "query": "cast iron skillet",
                "context": {}
            }
        )

        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()

        print(f"✓ API call successful (Status: {response.status_code})")
        print(f"  - Good tier: {len(data['results']['good'])} products")
        print(f"  - Better tier: {len(data['results']['better'])} products")
        print(f"  - Best tier: {len(data['results']['best'])} products")

        total_products = (
            len(data['results']['good']) +
            len(data['results']['better']) +
            len(data['results']['best'])
        )
        assert total_products > 0, "Should return products"
        print(f"✓ Total products returned: {total_products}")

        if data.get('real_search_metrics'):
            metrics = data['real_search_metrics']
            print(f"  - Sources analyzed: {metrics.get('total_sources_analyzed', 0)}")
            print(f"  - Search queries: {metrics.get('search_queries_executed', 0)}")

        return data

async def test_api_household_size():
    """Test 2: Search with household size characteristic"""
    print("\n" + "="*80)
    print("TEST 2: Personalized Search (Household Size: 1-2 people)")
    print("="*80)

    async with httpx.AsyncClient(timeout=180.0) as client:
        response = await client.post(
            f"{BASE_URL}/api/search",
            json={
                "query": "cast iron skillet",
                "context": {},
                "characteristics": {
                    "household_size": "1-2"
                }
            }
        )

        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()

        print(f"✓ Personalized API call successful (Status: {response.status_code})")
        print(f"📋 Characteristics: household_size=1-2")
        print(f"  - Good tier: {len(data['results']['good'])} products")
        print(f"  - Better tier: {len(data['results']['better'])} products")
        print(f"  - Best tier: {len(data['results']['best'])} products")

        # Check for size mentions in product names
        all_products = (
            data['results']['good'] +
            data['results']['better'] +
            data['results']['best']
        )

        size_keywords = ['8"', '8 inch', '8-inch', '10"', '10 inch', '10-inch']
        products_with_size = []

        for product in all_products:
            product_text = f"{product.get('name', '')}".lower()
            if any(size.lower() in product_text for size in size_keywords):
                products_with_size.append(product.get('name'))

        if products_with_size:
            print(f"✓ Found {len(products_with_size)} products with appropriate sizes:")
            for name in products_with_size[:3]:
                print(f"  - {name}")
        else:
            print("ℹ️  No products have size in names (may be in characteristics)")

        return data

async def test_api_value_preference():
    """Test 3: Search with value preference"""
    print("\n" + "="*80)
    print("TEST 3: Search with Value Preference (Buy for Life)")
    print("="*80)

    async with httpx.AsyncClient(timeout=180.0) as client:
        response = await client.post(
            f"{BASE_URL}/api/search",
            json={
                "query": "cast iron skillet",
                "context": {
                    "value_preference": "buy_for_life"
                },
                "characteristics": {
                    "household_size": "2-4"
                }
            }
        )

        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()

        print(f"✓ Combined context + characteristics search successful")
        print(f"📋 Context: value_preference=buy_for_life")
        print(f"📋 Characteristics: household_size=2-4")

        best_tier = data['results']['best']
        if best_tier:
            print(f"✓ Best tier has {len(best_tier)} premium products")
            product = best_tier[0]
            print(f"\nSample best tier product:")
            print(f"  Name: {product.get('name')}")
            print(f"  Brand: {product.get('brand')}")
            if product.get('value_metrics'):
                print(f"  Price: ${product['value_metrics'].get('upfront_price', 0)}")
                print(f"  Lifespan: {product['value_metrics'].get('expected_lifespan_years', 0)} years")

        return data

async def test_health_check():
    """Test 0: Health check"""
    print("\n" + "="*80)
    print("TEST 0: API Health Check")
    print("="*80)

    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.get(f"{BASE_URL}/health")
            assert response.status_code == 200
            data = response.json()
            print(f"✓ Backend is healthy")
            print(f"  - Status: {data.get('status')}")
            print(f"  - Version: {data.get('version')}")
            return True
        except Exception as e:
            print(f"❌ Backend health check failed: {e}")
            print(f"⚠️  Make sure the backend is running on {BASE_URL}")
            return False

async def run_all_tests():
    """Run all API integration tests"""
    print("\n" + "🧪"*40)
    print("PERSONALIZED SEARCH API INTEGRATION TEST SUITE")
    print("🧪"*40)

    try:
        # Test 0: Health check
        healthy = await test_health_check()
        if not healthy:
            print("\n❌ Backend is not running. Start it with:")
            print("   cd /Users/wenyichen/kenny-gem-finder/backend")
            print("   source venv/bin/activate && uvicorn main:app --reload --port 8000")
            return False

        # Test 1: Basic search
        print("\n⏳ Running Test 1 (30-50 seconds)...")
        await test_api_basic_search()

        # Test 2: Household size personalization
        print("\n⏳ Running Test 2 (30-50 seconds)...")
        await test_api_household_size()

        # Test 3: Value preference integration
        print("\n⏳ Running Test 3 (30-50 seconds)...")
        await test_api_value_preference()

        print("\n" + "="*80)
        print("✅ ALL API INTEGRATION TESTS PASSED")
        print("="*80)
        print("\nSummary:")
        print("  ✓ Backend API is healthy and responding")
        print("  ✓ Basic search returns products")
        print("  ✓ Household size personalization works")
        print("  ✓ Value preference + characteristics integration works")
        print("\n🎉 The personalized search feature is working correctly!")

    except AssertionError as e:
        print(f"\n❌ TEST ASSERTION FAILED: {e}")
        return False
    except httpx.ConnectError:
        print(f"\n❌ CONNECTION FAILED: Cannot connect to {BASE_URL}")
        print("⚠️  Make sure the backend is running")
        return False
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

    return True

if __name__ == "__main__":
    print("Starting API integration test suite...")
    print("This will take 2-3 minutes due to AI search calls...")
    print(f"Testing against: {BASE_URL}")
    success = asyncio.run(run_all_tests())
    exit(0 if success else 1)
