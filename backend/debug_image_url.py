#!/usr/bin/env python3
"""
Quick debug script to check if agents are returning image_url
"""
import asyncio
import json
from adk_search import get_adk_search


async def main():
    print("\n🔍 Debugging image_url extraction...\n")

    # Run a quick search
    result = await get_adk_search(
        query="air fryer",
        max_price=200.0
    )

    # Check first product from each tier
    for tier_name in ["good_tier", "better_tier", "best_tier"]:
        products = result.get(tier_name, [])
        if products:
            product = products[0]
            print(f"\n{tier_name.upper()}:")
            print(f"  Name: {product.get('name')}")
            print(f"  Has image_url: {'image_url' in product}")
            print(f"  image_url value: {product.get('image_url', 'NOT FOUND')}")

            # Show all keys
            print(f"  All keys ({len(product.keys())}): {list(product.keys())}")


if __name__ == "__main__":
    asyncio.run(main())
