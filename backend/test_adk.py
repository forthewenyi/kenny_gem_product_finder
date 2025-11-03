"""
Simple test for ADK-based product search
"""
import asyncio
from adk_search import get_adk_search


async def main():
    print("Testing ADK product search...\n")

    # Test with a simple query
    result = await get_adk_search(
        query="chef's knife",  # Change query to get fresh results
        max_price=150.0,
        user_context={"household_size": "2 people"},
        characteristics={"cooking_frequency": "daily"}
    )

    print("\n=== SEARCH RESULTS ===\n")

    # Print full result as JSON for debugging
    import json
    print("FULL RESULT:")
    print(json.dumps(result, indent=2)[:1000])  # First 1000 chars
    print("\n")

    # Print raw response if available
    if "raw_response" in result:
        print("RAW RESPONSE:")
        print(result["raw_response"][:500])  # First 500 chars
        print("\n")

    # Print full result structure for debugging
    print(f"Result keys: {list(result.keys())}\n")

    # Check if products array exists
    if "products" in result:
        print(f"Found {len(result['products'])} products:\n")
        for product in result['products']:
            print(f"  - {product.get('name', 'N/A')}")
            print(f"    Price: {product.get('price', 'N/A')}")
            print(f"    Durability: {product.get('durability_score', 'N/A')}")
            print(f"    Best for: {product.get('best_for', 'N/A')}\n")

    # Print tiers
    for tier in ["good_tier", "better_tier", "best_tier"]:
        products = result.get(tier, [])
        if products:
            print(f"\n{tier.upper().replace('_', ' ')}:")
            for product in products:
                print(f"  - {product.get('name', 'N/A')}")
                print(f"    Price: {product.get('price', 'N/A')}")
                print(f"    Durability: {product.get('durability_score', 'N/A')}")

    # Print insights
    insights = result.get("key_insights", [])
    if insights:
        print(f"\nKEY INSIGHTS:")
        for insight in insights:
            print(f"  - {insight}")

    # Print characteristics
    chars = result.get("aggregated_characteristics", [])
    if chars:
        print(f"\nCHARACTERISTICS:")
        for char in chars[:5]:  # Top 5
            print(f"  - {char.get('label')}: {char.get('count')} products")

    print("\n✅ Test completed!")


if __name__ == "__main__":
    asyncio.run(main())
