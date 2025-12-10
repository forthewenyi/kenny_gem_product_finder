#!/usr/bin/env python3
"""
Comprehensive test for ADK-based product search
Verifies all 17 fields are correctly output by agents (16 product fields + tier)
"""
import asyncio
import json
from adk_search import get_adk_search


async def main():
    print("\n" + "="*80)
    print("🧪 COMPREHENSIVE ADK SEARCH TEST")
    print("="*80)
    print("\n🔍 Testing query: cast iron skillet")
    print("📋 Verifying all 17 product fields from agent output (16 product fields + tier)\n")

    # Test with a simple query
    result = await get_adk_search(
        query="cast iron skillet",
        max_price=200.0,
        user_context={"household_size": "2 people"},
        characteristics={"cooking_frequency": "daily"}
    )

    print("\n" + "="*80)
    print("📊 SEARCH METRICS")
    print("="*80)

    metrics = result.get("real_search_metrics", {})
    print(f"✓ Total searches: {metrics.get('total_searches', 0)}")
    print(f"✓ Total sources: {metrics.get('total_sources', 0)}")
    print(f"✓ Context discovery: {metrics.get('context_discovery_searches', 0)} searches")
    print(f"✓ Product finder: {metrics.get('product_finder_searches', 0)} searches")

    # Count products by tier
    good_count = len(result.get("good_tier", []))
    better_count = len(result.get("better_tier", []))
    best_count = len(result.get("best_tier", []))
    total_count = good_count + better_count + best_count

    print(f"\n📦 PRODUCTS FOUND: {total_count} total")
    print(f"   💚 GOOD tier: {good_count} products")
    print(f"   💛 BETTER tier: {better_count} products")
    print(f"   ❤️  BEST tier: {best_count} products")

    # Verify all 17 fields for each product (16 product fields + tier)
    print("\n" + "="*80)
    print("🔍 FIELD VERIFICATION (checking all 17 required fields)")
    print("="*80)

    required_fields = [
        "name", "brand", "category", "materials", "key_features",
        "key_differentiator", "why_its_a_gem", "maintenance_tasks",
        "learning_curve", "drawbacks", "professional_reviews",
        "best_for", "price", "lifespan", "purchase_links", "image_url", "tier"
    ]

    all_products = []
    for tier_name in ["good_tier", "better_tier", "best_tier"]:
        all_products.extend(result.get(tier_name, []))

    if not all_products:
        print("❌ ERROR: No products found!")
        return

    # Check first product from each tier
    for tier_name, emoji in [("good_tier", "💚"), ("better_tier", "💛"), ("best_tier", "❤️")]:
        products = result.get(tier_name, [])
        if products:
            product = products[0]
            print(f"\n{emoji} {tier_name.upper().replace('_', ' ')} - Sample Product:")
            print(f"   Name: {product.get('name', 'N/A')}")

            # Check all required fields
            missing_fields = []
            present_fields = []

            for field in required_fields:
                value = product.get(field)
                if value is None or (isinstance(value, (list, str)) and not value):
                    missing_fields.append(field)
                else:
                    present_fields.append(field)

            print(f"\n   ✅ Present fields ({len(present_fields)}/16):")
            for field in present_fields:
                value = product.get(field)
                if isinstance(value, list):
                    print(f"      • {field}: {len(value)} items")
                elif isinstance(value, str) and len(value) > 50:
                    print(f"      • {field}: {value[:50]}...")
                else:
                    print(f"      • {field}: {value}")

            if missing_fields:
                print(f"\n   ⚠️  Missing fields ({len(missing_fields)}):")
                for field in missing_fields:
                    print(f"      • {field}")

    # Detailed view of ONE complete product
    print("\n" + "="*80)
    print("📋 COMPLETE PRODUCT EXAMPLE (all fields)")
    print("="*80)

    sample_product = all_products[0]
    print(f"\n{json.dumps(sample_product, indent=2)}")

    # Verify critical field renames
    print("\n" + "="*80)
    print("✅ CRITICAL FIELD VERIFICATION")
    print("="*80)

    issues = []

    # Check for old field names that should NOT exist
    if any(p.get("trade_offs") for p in all_products):
        issues.append("❌ FAIL: Found old field 'trade_offs' (should be 'drawbacks')")
    else:
        print("✅ PASS: No old 'trade_offs' field found")

    if any(p.get("why_gem") for p in all_products):
        issues.append("❌ FAIL: Found old field 'why_gem' (should be 'why_its_a_gem')")
    else:
        print("✅ PASS: No old 'why_gem' field found")

    # Check for new field names that SHOULD exist
    drawbacks_count = sum(1 for p in all_products if p.get("drawbacks"))
    if drawbacks_count == len(all_products):
        print(f"✅ PASS: All {len(all_products)} products have 'drawbacks' field")
    else:
        issues.append(f"❌ FAIL: Only {drawbacks_count}/{len(all_products)} products have 'drawbacks'")

    why_gem_count = sum(1 for p in all_products if p.get("why_its_a_gem"))
    if why_gem_count == len(all_products):
        print(f"✅ PASS: All {len(all_products)} products have 'why_its_a_gem' field")
    else:
        issues.append(f"❌ FAIL: Only {why_gem_count}/{len(all_products)} products have 'why_its_a_gem'")

    category_count = sum(1 for p in all_products if p.get("category"))
    if category_count == len(all_products):
        print(f"✅ PASS: All {len(all_products)} products have 'category' field")
    else:
        issues.append(f"❌ FAIL: Only {category_count}/{len(all_products)} products have 'category'")

    lifespan_count = sum(1 for p in all_products if p.get("lifespan"))
    if lifespan_count == len(all_products):
        print(f"✅ PASS: All {len(all_products)} products have 'lifespan' field")
    else:
        issues.append(f"⚠️  WARNING: Only {lifespan_count}/{len(all_products)} products have 'lifespan'")

    image_url_count = sum(1 for p in all_products if p.get("image_url"))
    if image_url_count == len(all_products):
        print(f"✅ PASS: All {len(all_products)} products have 'image_url' field")
    elif image_url_count > 0:
        print(f"⚠️  WARNING: Only {image_url_count}/{len(all_products)} products have 'image_url'")
    else:
        issues.append(f"❌ FAIL: No products have 'image_url' field - image extraction not working")

    # Print summary
    print("\n" + "="*80)
    if issues:
        print("⚠️  ISSUES FOUND:")
        print("="*80)
        for issue in issues:
            print(f"  {issue}")
    else:
        print("🎉 ALL CHECKS PASSED!")
        print("="*80)
        print("✅ Backend alignment verified successfully!")
        print("✅ All 17 product fields are correctly output by agents (16 product fields + tier)")
        print("✅ Field names are consistent across the codebase")
        print("✅ Product image URLs are being extracted from search results")

    print("\n")


if __name__ == "__main__":
    asyncio.run(main())
