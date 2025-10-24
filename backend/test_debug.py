"""
Debug test to see raw OpenAI output
"""
import asyncio
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from simple_search import SimpleKennySearch

async def test():
    search = SimpleKennySearch()

    print("Running AI search with debug output...")
    print("=" * 60)

    result = await search.search_products(
        "I need a cast iron skillet that won't rust easily",
        {"experience_level": "beginner"}
    )

    print("\n📊 RAW RESULT FROM AI:")
    print("=" * 60)
    import json
    print(json.dumps(result, indent=2))
    print("=" * 60)

    # Check structure
    print("\n🔍 STRUCTURE CHECK:")
    print(f"Type of result: {type(result)}")
    print(f"Keys: {result.keys()}")
    print(f"\nGood tier type: {type(result.get('good_tier', []))}")
    print(f"Good tier length: {len(result.get('good_tier', []))}")
    if result.get('good_tier'):
        print(f"First good tier item type: {type(result['good_tier'][0])}")
        print(f"First good tier item: {result['good_tier'][0]}")

if __name__ == "__main__":
    asyncio.run(test())
