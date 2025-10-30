#!/usr/bin/env python3
"""
Test script for Google Custom Search API
Run this to verify your API keys are configured correctly.

Usage:
    python test_google_search.py
"""
import os
from dotenv import load_dotenv
from google_search_service import get_google_search_service

# Load environment variables
load_dotenv()


def test_search_api():
    """Test the Google Search API configuration"""

    print("\n" + "="*80)
    print("🔍 GOOGLE CUSTOM SEARCH API TEST")
    print("="*80 + "\n")

    # Initialize service
    service = get_google_search_service()

    # Show quota info
    print("📊 Configuration Status:")
    print("-" * 80)
    quota_info = service.get_quota_info()
    for key, value in quota_info.items():
        print(f"  {key}: {value}")

    print("\n" + "="*80)
    print("🧪 Running Test Search...")
    print("="*80 + "\n")

    # Test search query
    test_query = "best cast iron skillet reddit"
    print(f"Query: '{test_query}'")
    print(f"Requesting: 5 results\n")

    try:
        results = service.search(test_query, num_results=5)

        if len(results) > 0:
            print(f"✅ SUCCESS! Retrieved {len(results)} results\n")
            print("-" * 80)

            for i, result in enumerate(results, 1):
                print(f"\nResult {i}:")
                print(f"  Title: {result['title'][:60]}...")
                print(f"  URL: {result['url']}")
                print(f"  Snippet: {result['snippet'][:100]}...")

            print("\n" + "="*80)
            print("✅ Google Custom Search API is working correctly!")
            print("="*80 + "\n")

            # Provide guidance
            if service.use_official_api:
                print("✓ You are using the official Google Custom Search API")
                print("  - Reliable, no rate limiting")
                print("  - First 100 queries/day free")
                print("  - $5 per 1,000 queries after that")
            else:
                print("⚠️  You are using the fallback googlesearch-python library")
                print("  - May be rate-limited")
                print("  - To use the official API:")
                print("    1. See GOOGLE_SEARCH_SETUP.md for instructions")
                print("    2. Add GOOGLE_SEARCH_API_KEY and GOOGLE_SEARCH_ENGINE_ID to .env")

        else:
            print("⚠️  WARNING: Search returned 0 results")
            print("\nPossible causes:")
            print("  1. Rate limiting (if using fallback library)")
            print("  2. Network connectivity issues")
            print("  3. Invalid API credentials")

            if not service.use_official_api:
                print("\n💡 Recommendation:")
                print("  Set up Google Custom Search API for reliable results")
                print("  See GOOGLE_SEARCH_SETUP.md for step-by-step instructions")

    except Exception as e:
        print(f"❌ ERROR: {e}")
        print("\n🔧 Troubleshooting:")
        print("  1. Check your .env file has correct API keys")
        print("  2. Verify API is enabled in Google Cloud Console")
        print("  3. Check GOOGLE_SEARCH_SETUP.md for detailed setup")
        return False

    print("\n")
    return True


if __name__ == "__main__":
    test_search_api()
