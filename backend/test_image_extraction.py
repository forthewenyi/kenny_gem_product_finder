#!/usr/bin/env python3
"""
Test script to determine if product images can be extracted from Google Search results.

This script will:
1. Test the Google Custom Search API directly
2. Show the complete API response structure
3. Extract available image URLs (if any)
4. Provide recommendations for implementation

Usage:
    python test_image_extraction.py
"""
import os
import json
from dotenv import load_dotenv
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

load_dotenv()


def test_image_availability():
    """Test what image data is available in Google Custom Search API responses"""

    print("\n" + "="*80)
    print("🖼️  GOOGLE CUSTOM SEARCH - IMAGE DATA AVAILABILITY TEST")
    print("="*80 + "\n")

    # Check API configuration
    api_key = os.getenv("GOOGLE_SEARCH_API_KEY")
    search_engine_id = os.getenv("GOOGLE_SEARCH_ENGINE_ID")

    if not api_key or not search_engine_id:
        print("❌ ERROR: Google Custom Search API not configured")
        print("\nPlease set in .env:")
        print("  GOOGLE_SEARCH_API_KEY=your_api_key")
        print("  GOOGLE_SEARCH_ENGINE_ID=your_engine_id")
        return False

    print("✅ API configured\n")

    # Initialize API client
    service = build("customsearch", "v1", developerKey=api_key)

    # Test query for a specific product (likely to have images)
    test_query = "Lodge 10.25 inch cast iron skillet amazon"
    print(f"🔍 Test Query: '{test_query}'")
    print(f"📦 Requesting: 3 results\n")

    try:
        # Execute search
        response = service.cse().list(
            q=test_query,
            cx=search_engine_id,
            num=3
        ).execute()

        if "items" not in response:
            print("⚠️  No results returned")
            return False

        print(f"✅ Retrieved {len(response['items'])} results\n")
        print("="*80)
        print("📊 ANALYZING AVAILABLE IMAGE DATA")
        print("="*80)

        # Analyze each result for image data
        for i, item in enumerate(response['items'], 1):
            print(f"\n{'─'*80}")
            print(f"Result {i}: {item.get('title', 'N/A')[:60]}...")
            print(f"URL: {item.get('link', 'N/A')}")
            print(f"{'─'*80}")

            # Check for image field (direct image result)
            if 'image' in item:
                print("\n✅ FOUND: Direct image data")
                print(f"   Context Link: {item['image'].get('contextLink', 'N/A')}")
                print(f"   Thumbnail: {item['image'].get('thumbnailLink', 'N/A')}")
                print(f"   Byte Size: {item['image'].get('byteSize', 'N/A')}")

            # Check for pagemap (structured data from page)
            if 'pagemap' in item:
                pagemap = item['pagemap']

                # CSE Image (images from the page content)
                if 'cse_image' in pagemap:
                    images = pagemap['cse_image']
                    print(f"\n✅ FOUND: cse_image ({len(images)} images)")
                    for idx, img in enumerate(images[:3], 1):  # Show first 3
                        print(f"   Image {idx}: {img.get('src', 'N/A')[:80]}...")

                # CSE Thumbnail (thumbnail version)
                if 'cse_thumbnail' in pagemap:
                    thumbs = pagemap['cse_thumbnail']
                    print(f"\n✅ FOUND: cse_thumbnail ({len(thumbs)} thumbnails)")
                    for idx, thumb in enumerate(thumbs[:3], 1):
                        print(f"   Thumbnail {idx}:")
                        print(f"      URL: {thumb.get('src', 'N/A')[:80]}...")
                        print(f"      Dimensions: {thumb.get('width', '?')}x{thumb.get('height', '?')}")

                # Metatags (og:image, twitter:image, etc.)
                if 'metatags' in pagemap:
                    metatags = pagemap['metatags'][0] if pagemap['metatags'] else {}

                    # Check for Open Graph image
                    og_image = metatags.get('og:image')
                    if og_image:
                        print(f"\n✅ FOUND: og:image (Open Graph)")
                        print(f"   URL: {og_image[:80]}...")

                    # Check for Twitter image
                    twitter_image = metatags.get('twitter:image')
                    if twitter_image:
                        print(f"\n✅ FOUND: twitter:image")
                        print(f"   URL: {twitter_image[:80]}...")

                # Product data (for e-commerce sites)
                if 'product' in pagemap:
                    products = pagemap['product']
                    print(f"\n✅ FOUND: product data ({len(products)} products)")
                    for idx, prod in enumerate(products[:2], 1):
                        print(f"   Product {idx}:")
                        print(f"      Name: {prod.get('name', 'N/A')[:60]}...")
                        print(f"      Image: {prod.get('image', 'N/A')[:80]}...")
                        print(f"      Price: {prod.get('price', 'N/A')}")

            # If no image data found
            if 'image' not in item and 'pagemap' not in item:
                print("\n❌ NO IMAGE DATA: This result has no image metadata")

        # Save full response for inspection
        print("\n" + "="*80)
        print("💾 SAVING FULL API RESPONSE")
        print("="*80)

        output_file = "google_search_response_sample.json"
        with open(output_file, 'w') as f:
            json.dump(response, f, indent=2)

        print(f"\n✅ Full API response saved to: {output_file}")
        print("   Review this file to see all available fields")

        # Summary and recommendations
        print("\n" + "="*80)
        print("📋 SUMMARY & RECOMMENDATIONS")
        print("="*80 + "\n")

        has_images = any(
            'image' in item or
            ('pagemap' in item and (
                'cse_image' in item['pagemap'] or
                'cse_thumbnail' in item['pagemap'] or
                ('metatags' in item['pagemap'] and
                 item['pagemap']['metatags'] and
                 'og:image' in item['pagemap']['metatags'][0])
            ))
            for item in response.get('items', [])
        )

        if has_images:
            print("✅ GOOD NEWS: Image URLs are available in Google Search results!\n")
            print("📝 Implementation Strategy:\n")
            print("1. Update google_search_service.py:")
            print("   - Extract image URLs from response items")
            print("   - Priority order: og:image > cse_image[0] > cse_thumbnail[0]")
            print("   - Add 'image_url' field to search result dict\n")

            print("2. Update models.py:")
            print("   - Add 'image_url: Optional[str]' field to Product model\n")

            print("3. Update adk_search.py:")
            print("   - Agents should capture image_url from search results")
            print("   - Add to product JSON output\n")

            print("4. Update frontend:")
            print("   - Display product images in ProductCard")
            print("   - Fallback to placeholder if image_url is None\n")

            print("🎯 Best Image Source Priority:")
            print("   1. og:image (Open Graph) - Usually high quality product images")
            print("   2. cse_image[0] - First image from page content")
            print("   3. cse_thumbnail[0] - Thumbnail version")
            print("   4. Fallback to default placeholder")
        else:
            print("⚠️  NO IMAGE DATA FOUND in this test")
            print("\nPossible causes:")
            print("  - Search results don't include product pages with images")
            print("  - Need to enable image search in Custom Search Engine config")
            print("\n💡 Try enabling 'Image search' in your search engine settings:")
            print("   https://programmablesearchengine.google.com/")

        return True

    except HttpError as e:
        print(f"❌ API ERROR: {e}")
        if e.resp.status == 429:
            print("\n   Daily quota exceeded (100 free queries/day)")
        elif e.resp.status == 400:
            print("\n   Invalid API key or Search Engine ID")
        return False

    except Exception as e:
        print(f"❌ UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    test_image_availability()
    print("\n")
