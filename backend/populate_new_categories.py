#!/usr/bin/env python3
"""
Populate new categories (small appliances and kitchen tools) with popular searches
"""

import asyncio
import httpx
import json
from typing import List

BASE_URL = "http://localhost:8000"

# Popular search terms for each category
SMALL_APPLIANCES = [
    "stand mixer",
    "food processor",
    "blender",
    "coffee maker",
    "toaster",
    "air fryer",
    "slow cooker",
    "instant pot",
    "hand mixer",
    "rice cooker"
]

KITCHEN_TOOLS = [
    "chef knife",
    "cutting board",
    "measuring cups",
    "mixing bowls",
    "can opener",
    "peeler",
    "whisk",
    "spatula",
    "tongs",
    "kitchen shears"
]

async def track_search(term: str, category: str, client: httpx.AsyncClient):
    """Track a search term for a category"""
    try:
        response = await client.post(
            f"{BASE_URL}/api/track-search",
            params={
                "query": term,
                "category": category
            }
        )

        if response.status_code == 200:
            return True, term
        else:
            return False, f"{term} (status {response.status_code})"
    except Exception as e:
        return False, f"{term} (error: {e})"

async def populate_category(category: str, search_terms: List[str]):
    """Populate a category with search terms"""
    print(f"\n{'='*80}")
    print(f"POPULATING: {category.upper().replace('_', ' ')}")
    print(f"{'='*80}\n")

    async with httpx.AsyncClient(timeout=10.0) as client:
        results = {
            'success': [],
            'failed': []
        }

        for term in search_terms:
            success, message = await track_search(term, category, client)
            if success:
                results['success'].append(term)
                print(f"✓ Tracked: {term}")
            else:
                results['failed'].append(message)
                print(f"✗ Failed: {message}")

            # Small delay to avoid overwhelming the server
            await asyncio.sleep(0.2)

        print(f"\n{'='*80}")
        print(f"Summary for {category}:")
        print(f"  ✓ Success: {len(results['success'])} terms")
        print(f"  ✗ Failed: {len(results['failed'])} terms")
        print(f"{'='*80}")

        return results

async def verify_popular_searches(category: str):
    """Verify that popular searches are showing up"""
    print(f"\n{'='*80}")
    print(f"VERIFYING: {category.upper().replace('_', ' ')}")
    print(f"{'='*80}\n")

    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.get(
                f"{BASE_URL}/api/popular-searches",
                params={"category": category}
            )

            if response.status_code == 200:
                data = response.json()
                items = data.get('items', [])

                print(f"Found {len(items)} popular searches:")
                for i, item in enumerate(items[:10], 1):
                    print(f"  {i}. {item['term']} (count: {item['count']})")

                return True
            else:
                print(f"✗ Failed to fetch (status {response.status_code})")
                return False
        except Exception as e:
            print(f"✗ Error: {e}")
            return False

async def main():
    print("\n" + "🔨" * 40)
    print("POPULATE NEW CATEGORIES WITH POPULAR SEARCHES")
    print("🔨" * 40)

    # Check if backend is running
    print("\nChecking backend health...")
    async with httpx.AsyncClient(timeout=5.0) as client:
        try:
            response = await client.get(f"{BASE_URL}/health")
            if response.status_code != 200:
                print("✗ Backend is not healthy")
                return False
            print("✓ Backend is healthy\n")
        except Exception as e:
            print(f"✗ Cannot connect to backend: {e}")
            print(f"  Make sure backend is running on {BASE_URL}")
            return False

    # Populate small appliances
    await populate_category("small_appliances", SMALL_APPLIANCES)

    # Populate kitchen tools
    await populate_category("kitchen_tools", KITCHEN_TOOLS)

    # Verify the data
    print("\n" + "="*80)
    print("VERIFICATION")
    print("="*80)

    await verify_popular_searches("small_appliances")
    await verify_popular_searches("kitchen_tools")

    print("\n" + "="*80)
    print("✅ POPULATION COMPLETE")
    print("="*80)
    print("\nThe new categories now have popular searches!")
    print("Refresh http://localhost:3000 and hover over:")
    print("  - SMALL APPLIANCES")
    print("  - KITCHEN TOOLS")
    print("\nYou should see the popular items in the dropdowns.")

    return True

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)
