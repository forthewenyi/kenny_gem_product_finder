#!/usr/bin/env python3
"""
Quick test to verify Google Search Service extracts image URLs correctly
"""
import asyncio
from dotenv import load_dotenv
from google_search_service import get_google_search_service

# Load environment variables
load_dotenv()


async def test_image_extraction():
    """Test that search results include image_url field"""
    print("\n" + "="*80)
    print("🧪 GOOGLE SEARCH SERVICE - IMAGE URL EXTRACTION TEST")
    print("="*80 + "\n")

    service = get_google_search_service()

    test_query = "Lodge cast iron skillet amazon"
    print(f"🔍 Query: '{test_query}'")
    print(f"📦 Requesting: 5 results\n")

    try:
        # Use async search (same as agents use)
        results = await service.async_search(test_query, num_results=5)

        print(f"✅ Retrieved {len(results)} results\n")
        print("="*80)
        print("📊 IMAGE URL EXTRACTION ANALYSIS")
        print("="*80 + "\n")

        image_count = 0
        for i, result in enumerate(results, 1):
            has_image = result.get('image_url') is not None
            if has_image:
                image_count += 1

            print(f"Result {i}:")
            print(f"  Title: {result.get('title', 'N/A')[:60]}...")
            print(f"  URL: {result.get('url', 'N/A')[:70]}...")
            print(f"  Image URL: {'✅ ' + result.get('image_url', 'N/A')[:70] + '...' if has_image else '❌ None'}")
            print()

        # Summary
        print("="*80)
        print("📈 SUMMARY")
        print("="*80)

        if len(results) == 0:
            print("❌ No results returned - cannot test image extraction")
            print("\n💡 This usually means:")
            print("   1. Google Custom Search API not configured (check .env file)")
            print("   2. Fallback library rate-limited or blocked")
            return False

        print(f"✅ {image_count}/{len(results)} results have image URLs ({image_count/len(results)*100:.1f}%)")

        if image_count == len(results):
            print("\n🎉 SUCCESS! All search results include image URLs")
            print("✅ Image extraction is working correctly")
            print("✅ ADK agents will receive image URLs in search results")
            return True
        elif image_count > 0:
            print(f"\n⚠️  PARTIAL SUCCESS: {image_count}/{len(results)} results have images")
            print("   This is acceptable - not all web pages have image metadata")
            return True
        else:
            print("\n❌ FAILURE: No image URLs found")
            print("   Check that Google Custom Search API is configured")
            return False

    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(test_image_extraction())
    print("\n")
    exit(0 if success else 1)
