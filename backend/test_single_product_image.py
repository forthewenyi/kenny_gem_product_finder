#!/usr/bin/env python3
"""
Test image URL extraction for a single product search
"""
import asyncio
import json
from google_search_service import get_google_search_service
from dotenv import load_dotenv

load_dotenv()


async def test_single_product():
    print("\n" + "="*80)
    print("🧪 SINGLE PRODUCT IMAGE URL TEST")
    print("="*80 + "\n")

    service = get_google_search_service()

    # Search for a specific product that should have images
    query = "Lodge 10.25 inch cast iron skillet amazon"
    print(f"🔍 Searching: {query}\n")

    # Get search results
    results = await service.async_search(query, num_results=3)

    print(f"✅ Got {len(results)} search results\n")

    # Check each result
    for i, result in enumerate(results, 1):
        print(f"{'─'*80}")
        print(f"Result {i}:")
        print(f"  Title: {result.get('title', 'N/A')[:70]}...")
        print(f"  URL: {result.get('url', 'N/A')[:70]}...")

        has_image = 'image_url' in result and result['image_url'] is not None
        if has_image:
            print(f"  ✅ image_url: {result['image_url'][:80]}...")
        else:
            print(f"  ❌ image_url: MISSING OR NULL")

        print(f"  All keys in result: {list(result.keys())}")
        print()

    # Show full JSON of first result
    if results:
        print("="*80)
        print("📋 FULL JSON OF FIRST RESULT")
        print("="*80)
        print(json.dumps(results[0], indent=2))

    # Summary
    image_count = sum(1 for r in results if r.get('image_url'))
    print("\n" + "="*80)
    print(f"📊 SUMMARY: {image_count}/{len(results)} results have image URLs")
    print("="*80 + "\n")

    if image_count == len(results):
        print("✅ All results have image URLs - Search service is working correctly!")
        return True
    elif image_count > 0:
        print(f"⚠️  Only {image_count}/{len(results)} have images - Some missing")
        return True
    else:
        print("❌ NO image URLs found - Search service may not be extracting images")
        return False


if __name__ == "__main__":
    success = asyncio.run(test_single_product())
    exit(0 if success else 1)
