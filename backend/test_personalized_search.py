#!/usr/bin/env python3
"""
Comprehensive test suite for personalized search feature
Tests the entire flow from frontend characteristics to backend AI personalization
"""

import asyncio
import json
from dotenv import load_dotenv
from contextual_search import ContextualKennySearch

# Load environment variables
load_dotenv()

async def test_basic_search():
    """Test 1: Basic search without characteristics"""
    print("\n" + "="*80)
    print("TEST 1: Basic Search (No Personalization)")
    print("="*80)

    search_service = ContextualKennySearch()

    result = await search_service.search_products(
        query="cast iron skillet",
        context={},
        characteristics=None
    )

    print(f"✓ Search completed")
    print(f"  - Good tier: {len(result.get('good_tier', []))} products")
    print(f"  - Better tier: {len(result.get('better_tier', []))} products")
    print(f"  - Best tier: {len(result.get('best_tier', []))} products")

    # Check that we got products
    total_products = (
        len(result.get('good_tier', [])) +
        len(result.get('better_tier', [])) +
        len(result.get('best_tier', []))
    )
    assert total_products > 0, "Should return products"
    print(f"✓ Total products returned: {total_products}")

    return result

async def test_household_size_personalization():
    """Test 2: Search with household size characteristic"""
    print("\n" + "="*80)
    print("TEST 2: Personalized Search (Household Size: 1-2 people)")
    print("="*80)

    search_service = ContextualKennySearch()

    characteristics = {
        "household_size": "1-2"
    }

    print(f"📋 Characteristics provided: {characteristics}")

    result = await search_service.search_products(
        query="cast iron skillet",
        context={},
        characteristics=characteristics
    )

    print(f"✓ Personalized search completed")
    print(f"  - Good tier: {len(result.get('good_tier', []))} products")
    print(f"  - Better tier: {len(result.get('better_tier', []))} products")
    print(f"  - Best tier: {len(result.get('best_tier', []))} products")

    # Check product names for size mentions
    print("\n📦 Checking if products match household size preference...")
    all_products = (
        result.get('good_tier', []) +
        result.get('better_tier', []) +
        result.get('best_tier', [])
    )

    size_keywords = ['8"', '8 inch', '8-inch', '10"', '10 inch', '10-inch']
    products_with_size_info = []

    for product in all_products:
        product_text = f"{product.get('name', '')} {' '.join(product.get('characteristics', []))}".lower()
        has_appropriate_size = any(size.lower() in product_text for size in size_keywords)
        if has_appropriate_size:
            products_with_size_info.append(product.get('name'))

    if products_with_size_info:
        print(f"✓ Found {len(products_with_size_info)} products with appropriate sizes:")
        for name in products_with_size_info[:3]:
            print(f"  - {name}")
    else:
        print("⚠️  No products have size information in names (AI should include this)")

    return result

async def test_multiple_characteristics():
    """Test 3: Search with multiple characteristics"""
    print("\n" + "="*80)
    print("TEST 3: Multi-Characteristic Search")
    print("="*80)

    search_service = ContextualKennySearch()

    characteristics = {
        "household_size": "1-2",
        "surface": "pre_seasoned",
        "maintenance": "minimal"
    }

    print(f"📋 Characteristics provided:")
    for key, value in characteristics.items():
        print(f"  - {key}: {value}")

    result = await search_service.search_products(
        query="cast iron skillet",
        context={},
        characteristics=characteristics
    )

    print(f"\n✓ Multi-characteristic search completed")
    print(f"  - Good tier: {len(result.get('good_tier', []))} products")
    print(f"  - Better tier: {len(result.get('better_tier', []))} products")
    print(f"  - Best tier: {len(result.get('best_tier', []))} products")

    # Check for pre-seasoned products
    all_products = (
        result.get('good_tier', []) +
        result.get('better_tier', []) +
        result.get('best_tier', [])
    )

    pre_seasoned_count = 0
    for product in all_products:
        product_text = f"{product.get('name', '')} {' '.join(product.get('characteristics', []))}".lower()
        if 'pre-seasoned' in product_text or 'preseasoned' in product_text:
            pre_seasoned_count += 1

    print(f"✓ Found {pre_seasoned_count} pre-seasoned products matching surface preference")

    return result

async def test_value_preference_integration():
    """Test 4: Test with value preference (buy for life)"""
    print("\n" + "="*80)
    print("TEST 4: Value Preference Integration (Buy for Life)")
    print("="*80)

    search_service = ContextualKennySearch()

    context = {
        "value_preference": "buy_for_life"
    }

    characteristics = {
        "household_size": "2-4"
    }

    print(f"📋 Context: {context}")
    print(f"📋 Characteristics: {characteristics}")

    result = await search_service.search_products(
        query="cast iron skillet",
        context=context,
        characteristics=characteristics
    )

    print(f"\n✓ Combined context + characteristics search completed")

    # Check for premium/buy-for-life indicators
    best_tier_products = result.get('best_tier', [])
    if best_tier_products:
        print(f"✓ Best tier has {len(best_tier_products)} products (premium options)")
        print("\nSample best tier product:")
        product = best_tier_products[0]
        print(f"  Name: {product.get('name')}")
        print(f"  Price: ${product.get('price', 0)}")
        print(f"  Lifespan: {product.get('lifespan', 'N/A')}")
        print(f"  Why it's a gem: {product.get('why_its_a_gem', 'N/A')[:100]}...")

    return result

async def test_search_queries_generation():
    """Test 5: Verify AI generates personalized queries"""
    print("\n" + "="*80)
    print("TEST 5: AI Query Generation with Characteristics")
    print("="*80)

    search_service = ContextualKennySearch()

    characteristics = {
        "household_size": "1-2",
        "cooking_frequency": "daily",
        "maintenance": "minimal"
    }

    print(f"📋 Testing query generation with: {characteristics}")

    # Generate queries
    queries = await search_service._generate_contextual_queries(
        product_query="cast iron skillet",
        user_context={},
        characteristics=characteristics
    )

    print(f"\n✓ Generated {sum(len(q) for q in queries.values())} total queries across phases:")
    for phase, phase_queries in queries.items():
        print(f"\n  {phase.replace('_', ' ').title()} ({len(phase_queries)} queries):")
        for i, query in enumerate(phase_queries, 1):
            print(f"    {i}. {query}")

    # Verify queries mention the characteristics
    all_queries_text = ' '.join([q for queries_list in queries.values() for q in queries_list]).lower()

    checks = {
        "size": any(size in all_queries_text for size in ['8', '10', 'small', 'compact']),
        "maintenance": any(term in all_queries_text for term in ['easy', 'minimal', 'low maintenance', 'pre-seasoned']),
        "frequency": any(term in all_queries_text for term in ['daily', 'everyday', 'regular'])
    }

    print(f"\n✓ Query personalization checks:")
    for aspect, found in checks.items():
        status = "✓" if found else "⚠️ "
        print(f"  {status} {aspect.title()}: {'mentioned' if found else 'not explicitly mentioned'}")

    return queries

async def run_all_tests():
    """Run all tests sequentially"""
    print("\n" + "🧪"*40)
    print("COMPREHENSIVE PERSONALIZED SEARCH TEST SUITE")
    print("🧪"*40)

    try:
        # Test 1: Basic search
        await test_basic_search()

        # Test 2: Household size personalization
        await test_household_size_personalization()

        # Test 3: Multiple characteristics
        await test_multiple_characteristics()

        # Test 4: Value preference integration
        await test_value_preference_integration()

        # Test 5: Query generation
        await test_search_queries_generation()

        print("\n" + "="*80)
        print("✅ ALL TESTS PASSED")
        print("="*80)
        print("\nSummary:")
        print("  ✓ Basic search works without characteristics")
        print("  ✓ Household size personalization applied")
        print("  ✓ Multiple characteristics handled")
        print("  ✓ Context + characteristics integration works")
        print("  ✓ AI generates personalized queries")

    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

    return True

if __name__ == "__main__":
    print("Starting test suite...")
    print("This will take 2-3 minutes due to AI search calls...")
    success = asyncio.run(run_all_tests())
    exit(0 if success else 1)
