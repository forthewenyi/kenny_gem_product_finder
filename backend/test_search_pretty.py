#!/usr/bin/env python3
"""
Standalone script to test and pretty-print contextual search results
No pytest required - just run: python test_search_pretty.py

USAGE:
1. Change the QUERY variable to test different products
2. (Optional) Uncomment TEST_CHARACTERISTICS to test personalized search
3. Run: python test_search_pretty.py

FEATURES TESTED:
- AI-driven contextual search with Google Gemini
- Multi-phase research (context, materials, products, frustrations, value)
- Durability validation from user reports
- Personalized search based on user characteristics
- Quality checks for product data completeness
"""

import asyncio
import json
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from contextual_search import get_contextual_search


# ========== CONFIGURE YOUR TEST HERE ==========
QUERY = "cast iron skillet"  # Change this to test different products

# Test with user characteristics (personalization)
TEST_CHARACTERISTICS = {
    # "household_size": "1-2",
    # "surface": "pre_seasoned",
    # "maintenance": "minimal"
}
# ===============================================


async def test_search():
    """Run a search and pretty print results"""

    search = get_contextual_search()

    print(f"\n{'='*80}")
    print(f"🔍 TESTING SEARCH FOR: {QUERY}")
    print(f"{'='*80}\n")
    print("⏳ Searching... (this takes 30-60 seconds)\n")

    result = await search.search_products(
        query=QUERY,
        context={"location": "US"},
        characteristics=TEST_CHARACTERISTICS if TEST_CHARACTERISTICS else None
    )

    # ========== METRICS ==========
    print(f"\n{'='*80}")
    print("📊 SEARCH METRICS")
    print(f"{'='*80}")
    print(f"✓ Search approach: {result.get('search_approach', 'N/A')}")
    print(f"✓ Total sources analyzed: {result.get('total_sources_analyzed', 0)}")
    print(f"✓ Total queries generated: {result.get('queries_generated', 0)}")
    print(f"✓ Total products researched: {result.get('total_products_researched', 0)}")
    print(f"✓ Total products displayed: {result.get('total_products_displayed', 9)}")

    if "sources_by_phase" in result:
        print(f"\n📚 Sources by research phase:")
        for phase, count in result["sources_by_phase"].items():
            print(f"  • {phase.replace('_', ' ').title()}: {count} sources")

    if "search_queries" in result:
        print(f"\n🔍 Research queries used:")
        for i, query_info in enumerate(result["search_queries"], 1):
            if isinstance(query_info, dict):
                print(f"  {i}. [{query_info.get('phase', 'N/A')}] {query_info.get('query', 'N/A')}")
            else:
                print(f"  {i}. {query_info}")

    # ========== PRODUCT COUNTS ==========
    good_count = len(result.get("good_tier", []))
    better_count = len(result.get("better_tier", []))
    best_count = len(result.get("best_tier", []))
    total_count = good_count + better_count + best_count

    print(f"\n{'='*80}")
    print(f"📦 PRODUCTS FOUND: {total_count} total")
    print(f"{'='*80}")
    print(f"  💚 GOOD tier: {good_count} products")
    print(f"  💛 BETTER tier: {better_count} products")
    print(f"  ❤️  BEST tier: {best_count} products")

    # ========== PRODUCT DETAILS ==========
    for tier_name, tier_key, emoji in [
        ("GOOD", "good_tier", "💚"),
        ("BETTER", "better_tier", "💛"),
        ("BEST", "best_tier", "❤️")
    ]:
        products = result.get(tier_key, [])
        if not products:
            continue

        print(f"\n{'='*80}")
        print(f"{emoji} {tier_name} TIER ({len(products)} products)")
        print(f"{'='*80}")

        for i, product in enumerate(products, 1):
            print(f"\n{'-'*80}")
            print(f"Product {i}: {product.get('name', 'Unknown')}")
            print(f"{'-'*80}")
            print(f"📦 Brand: {product.get('brand', 'N/A')}")
            print(f"💰 Price: ${product.get('price', 0)}")
            print(f"⏰ Lifespan: {product.get('lifespan', 'N/A')}")

            # Durability data (new in contextual_search)
            if 'durability_data' in product and product['durability_data']:
                dd = product['durability_data']
                print(f"\n🛡️  Durability Assessment:")
                print(f"   Score: {dd.get('score', 'N/A')}/100")
                print(f"   Avg lifespan: {dd.get('average_lifespan_years', 'N/A')} years")
                print(f"   Still working after 5 years: {dd.get('still_working_after_5years_percent', 'N/A')}%")
                print(f"   User reports analyzed: {dd.get('total_user_reports', 'N/A')}")
                print(f"   Repairability: {dd.get('repairability_score', 'N/A')}/100")
                if dd.get('common_failure_points'):
                    print(f"   Failure points: {', '.join(dd['common_failure_points'])}")

            # Calculate cost per year
            if product.get('price') and product.get('lifespan'):
                try:
                    # Handle both numeric and string lifespans
                    lifespan = product['lifespan']
                    if isinstance(lifespan, str):
                        # Extract first number from string like "3-5 years"
                        import re
                        match = re.search(r'(\d+)', lifespan)
                        if match:
                            lifespan = int(match.group(1))
                        else:
                            lifespan = None

                    if lifespan:
                        cpy = product['price'] / lifespan
                        print(f"💵 Cost/year: ${cpy:.2f}")
                except (ValueError, TypeError, ZeroDivisionError):
                    pass

            # Characteristics
            characteristics = product.get('characteristics', [])
            # Handle both string and list formats
            if isinstance(characteristics, str):
                characteristics = [characteristics] if characteristics else []
            print(f"\n🏷️  Characteristics ({len(characteristics)}):")
            if characteristics:
                for char in characteristics:
                    print(f"   • {char}")
            else:
                print("   ⚠️  NO CHARACTERISTICS EXTRACTED")

            # Materials
            materials = product.get('materials', [])
            # Handle both string and list formats
            if isinstance(materials, str):
                materials = [materials] if materials else []
            print(f"\n🔧 Materials ({len(materials)}):")
            if materials:
                for mat in materials:
                    print(f"   • {mat}")
            else:
                print("   ⚠️  NO MATERIALS EXTRACTED")

            # Key features
            features = product.get('key_features', [])
            # Handle both string and list formats
            if isinstance(features, str):
                features = [features] if features else []
            print(f"\n✨ Key Features:")
            if features:
                for feat in features:
                    print(f"   • {feat}")
            else:
                print("   No features listed")

            # Why it's a gem
            print(f"\n💎 Why It's a Gem:")
            print(f"   {product.get('why_its_a_gem', 'N/A')}")

            # Practical metrics
            if 'practical_metrics' in product and product['practical_metrics']:
                pm = product['practical_metrics']
                print(f"\n📋 Practical Metrics:")
                print(f"   🧼 Cleaning time: {pm.get('cleaning_time_minutes', '?')} min")
                print(f"      Details: {pm.get('cleaning_details', 'N/A')}")
                print(f"   ⚙️  Setup time: {pm.get('setup_time', 'N/A')}")
                print(f"   📚 Learning curve: {pm.get('learning_curve', 'N/A')}")
                print(f"   🔧 Maintenance: {pm.get('maintenance_level', 'N/A')}")
                print(f"   ⚖️  Weight: {pm.get('weight_lbs', '?')} lbs")
                print(f"   🚿 Dishwasher safe: {'✅' if pm.get('dishwasher_safe') else '❌'}")
                print(f"   🔥 Oven safe: {'✅' if pm.get('oven_safe') else '❌'}")
                if pm.get('oven_max_temp'):
                    print(f"      Max temp: {pm['oven_max_temp']}°F")
            else:
                print(f"\n⚠️  NO PRACTICAL METRICS")

            # Trade-offs
            tradeoffs = product.get('trade_offs', [])
            # Handle both string and list formats
            if isinstance(tradeoffs, str):
                tradeoffs = [tradeoffs] if tradeoffs else []
            if tradeoffs:
                print(f"\n⚠️  Trade-offs:")
                for tradeoff in tradeoffs:
                    print(f"   • {tradeoff}")

            # Best for
            print(f"\n👤 Best For: {product.get('best_for', 'N/A')}")

            # Web sources
            sources = product.get('web_sources', [])
            print(f"\n🔗 Web Sources ({len(sources)}):")
            for j, source in enumerate(sources[:3], 1):  # Show first 3
                if isinstance(source, str):
                    print(f"   {j}. {source}")
                elif isinstance(source, dict):
                    print(f"   {j}. {source.get('url', 'N/A')}")

    # ========== SAVE TO FILE ==========
    output_file = f"/tmp/kenny_search_{QUERY.replace(' ', '_')}.json"
    with open(output_file, 'w') as f:
        json.dump(result, f, indent=2)

    print(f"\n{'='*80}")
    print(f"💾 Full JSON saved to: {output_file}")
    print(f"{'='*80}")

    # ========== QUALITY CHECKS ==========
    print(f"\n{'='*80}")
    print("🔍 QUALITY CHECKS")
    print(f"{'='*80}")

    issues = []

    # Check product counts
    if total_count < 9:
        issues.append(f"❌ Only {total_count} products (expected 9+)")
    else:
        print(f"✅ Product count: {total_count} (expected 9+)")

    if good_count < 3:
        issues.append(f"❌ Only {good_count} GOOD products (expected 3+)")
    else:
        print(f"✅ GOOD tier: {good_count} products (expected 3+)")

    if better_count < 3:
        issues.append(f"❌ Only {better_count} BETTER products (expected 3+)")
    else:
        print(f"✅ BETTER tier: {better_count} products (expected 3+)")

    if best_count < 3:
        issues.append(f"❌ Only {best_count} BEST products (expected 3+)")
    else:
        print(f"✅ BEST tier: {best_count} products (expected 3+)")

    # Check characteristics
    all_products = (
        result.get("good_tier", []) +
        result.get("better_tier", []) +
        result.get("best_tier", [])
    )

    products_with_chars = sum(1 for p in all_products if p.get('characteristics'))
    products_with_materials = sum(1 for p in all_products if p.get('materials'))
    products_with_metrics = sum(1 for p in all_products if p.get('practical_metrics'))

    if products_with_chars < total_count:
        issues.append(f"⚠️  Only {products_with_chars}/{total_count} products have characteristics")
    else:
        print(f"✅ All {total_count} products have characteristics")

    if products_with_materials < total_count * 0.5:
        issues.append(f"⚠️  Only {products_with_materials}/{total_count} products have materials")
    else:
        print(f"✅ {products_with_materials}/{total_count} products have materials")

    if products_with_metrics < total_count:
        issues.append(f"⚠️  Only {products_with_metrics}/{total_count} products have practical metrics")
    else:
        print(f"✅ All {total_count} products have practical metrics")

    # Print issues
    if issues:
        print(f"\n{'='*80}")
        print("⚠️  ISSUES FOUND:")
        print(f"{'='*80}")
        for issue in issues:
            print(f"  {issue}")
        print(f"\n💡 Consider refining the prompt in simple_search.py")
    else:
        print(f"\n🎉 All quality checks passed!")

    print(f"\n{'='*80}\n")


if __name__ == "__main__":
    print("\n🔍 Kenny Gem Finder - Search Test Tool")
    print(f"Testing query: '{QUERY}'")
    print("Change the QUERY variable at the top of this file to test different products\n")

    try:
        asyncio.run(test_search())
    except KeyboardInterrupt:
        print("\n\n⚠️  Search cancelled")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
