#!/usr/bin/env python3
"""
Test script to verify household size filtering for cast iron skillet
"""

import asyncio
import json
from contextual_search import contextual_search

async def test_household_filter():
    print("=" * 80)
    print("TEST: Cast Iron Skillet Search with Household Size Filter")
    print("=" * 80)

    # First, do a basic search
    print("\n1. Basic search for 'cast iron skillet'...")
    basic_results = await contextual_search("cast iron skillet")

    print(f"\n📊 Basic Search Results:")
    print(f"   Total products found: {len(basic_results.get('good_tier', [])) + len(basic_results.get('better_tier', [])) + len(basic_results.get('best_tier', []))}")
    print(f"   - GOOD tier: {len(basic_results.get('good_tier', []))} products")
    print(f"   - BETTER tier: {len(basic_results.get('better_tier', []))} products")
    print(f"   - BEST tier: {len(basic_results.get('best_tier', []))} products")

    # Show product names
    print("\n📋 Products found:")
    for tier_name in ['good_tier', 'better_tier', 'best_tier']:
        products = basic_results.get(tier_name, [])
        if products:
            print(f"\n{tier_name.upper().replace('_', ' ')}:")
            for i, product in enumerate(products, 1):
                print(f"   {i}. {product.get('name', 'Unknown')}")

    # Check if products have household_size metadata
    print("\n\n2. Checking if products have household_size metadata...")
    has_metadata = False
    for tier_name in ['good_tier', 'better_tier', 'best_tier']:
        for product in basic_results.get(tier_name, []):
            if 'household_size' in product.get('characteristics', {}):
                has_metadata = True
                print(f"   ✓ {product.get('name')}: household_size = {product.get('characteristics', {}).get('household_size')}")

    if not has_metadata:
        print("   ⚠️  No household_size metadata found in products!")
        print("   This is expected - household_size is a USER characteristic, not a product attribute")

    print("\n\n3. Understanding the characteristic vs filter distinction...")
    print("   • FILTER characteristics (SIZE, SURFACE, FEATURES): Product attributes we can filter by")
    print("   • USER characteristics (HOUSEHOLD_SIZE, COOKING_FREQUENCY): Used for recommendations, not filtering")
    print("   • HOUSEHOLD_SIZE tells us about the USER, not the product")
    print("   • We should recommend SIZE based on HOUSEHOLD_SIZE, but can't filter products by it")

    print("\n" + "=" * 80)
    print("CONCLUSION:")
    print("=" * 80)
    print("HOUSEHOLD_SIZE is a user characteristic that should influence SIZE recommendations,")
    print("but it cannot directly filter products because it's not a product attribute.")
    print("\nSolution: When user selects HOUSEHOLD_SIZE, we should:")
    print("  1. Auto-suggest appropriate SIZE filter (e.g., '1-2 people' → 8-10\" skillets)")
    print("  2. Or convert HOUSEHOLD_SIZE into a SIZE filter recommendation")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(test_household_filter())
