#!/usr/bin/env python3
"""
Test the new contextual AI-driven search approach
"""

import asyncio
import json
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from contextual_search import get_contextual_search


async def test_contextual_search(query: str):
    """Test contextual search with a specific query"""

    print(f"\n{'='*80}")
    print(f"🧪 TESTING CONTEXTUAL AI-DRIVEN SEARCH")
    print(f"{'='*80}\n")
    print(f"Query: {query}\n")

    search = get_contextual_search()

    result = await search.search_products(
        query=query,
        context={"location": "US"}
    )

    # Display results
    print(f"\n\n{'='*80}")
    print(f"📊 RESULTS SUMMARY")
    print(f"{'='*80}\n")

    # Context insights
    if "context_insights" in result:
        insights = result["context_insights"]
        print(f"🎯 CONTEXT ANALYSIS:")
        print(f"  Use Case: {insights.get('use_case_summary', 'N/A')}")
        print(f"  Key Constraints: {', '.join(insights.get('key_constraints', []))}")
        print(f"  Optimal Materials: {', '.join(insights.get('optimal_materials', []))}")
        print(f"  Material Reasoning: {insights.get('material_reasoning', 'N/A')}\n")

    # Product counts
    good_count = len(result.get("good_tier", []))
    better_count = len(result.get("better_tier", []))
    best_count = len(result.get("best_tier", []))

    print(f"📦 PRODUCTS FOUND:")
    print(f"  💚 GOOD: {good_count} products")
    print(f"  💛 BETTER: {better_count} products")
    print(f"  ❤️ BEST: {best_count} products")
    print(f"  📊 TOTAL: {good_count + better_count + best_count} products\n")

    # Common frustrations
    if "common_frustrations" in result and result["common_frustrations"]:
        print(f"⚠️  COMMON FRUSTRATIONS:")
        for frustration in result["common_frustrations"][:3]:
            print(f"  • {frustration.get('issue', 'N/A')}")
            print(f"    Why: {frustration.get('why_it_matters', 'N/A')}")
            print(f"    Avoid by: {frustration.get('how_to_avoid', 'N/A')}\n")

    # Unnecessary features
    if "unnecessary_features" in result and result["unnecessary_features"]:
        print(f"🚫 UNNECESSARY FEATURES (Marketing Gimmicks):")
        for feature in result["unnecessary_features"][:3]:
            print(f"  • {feature}")
        print()

    # Sample product from each tier
    print(f"\n{'='*80}")
    print(f"📦 SAMPLE PRODUCTS (ONE FROM EACH TIER)")
    print(f"{'='*80}\n")

    for tier_name, tier_key, emoji in [
        ("GOOD", "good_tier", "💚"),
        ("BETTER", "better_tier", "💛"),
        ("BEST", "best_tier", "❤️")
    ]:
        products = result.get(tier_key, [])
        if products:
            product = products[0]
            print(f"{emoji} {tier_name} TIER - {product.get('name', 'Unknown')}")
            print(f"  Brand: {product.get('brand', 'N/A')}")
            print(f"  Price: ${product.get('price', 0)}")
            print(f"  Lifespan: {product.get('lifespan', 0)} years")
            print(f"  Materials: {', '.join(product.get('materials', []))}")
            print(f"  Context Fit: {product.get('context_fit', 'N/A')}")
            print(f"  Why: {product.get('why_its_a_gem', 'N/A')[:100]}...")
            print()

    # Metadata
    print(f"\n{'='*80}")
    print(f"📊 SEARCH METADATA")
    print(f"{'='*80}\n")
    print(f"  Approach: {result.get('search_approach', 'N/A')}")
    print(f"  Queries Generated: {result.get('queries_generated', 0)}")
    print(f"  Research Phases: {', '.join(result.get('research_phases', []))}")

    # Save to file
    output_file = f"/tmp/contextual_search_{query.replace(' ', '_')}.json"
    with open(output_file, 'w') as f:
        json.dump(result, f, indent=2)

    print(f"\n💾 Full results saved to: {output_file}\n")
    print(f"{'='*80}\n")


if __name__ == "__main__":
    query = sys.argv[1] if len(sys.argv) > 1 else "cast iron skillet"

    print(f"\n🔍 Kenny Gem Finder - Contextual AI Search Test")
    print(f"Query: '{query}'")
    print(f"Usage: python test_contextual_search.py 'your search query'\n")

    try:
        asyncio.run(test_contextual_search(query))
    except KeyboardInterrupt:
        print("\n\n⚠️  Search cancelled")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
