#!/usr/bin/env python3
"""Test script for Dutch Oven search"""

import httpx
import asyncio
import json

async def test_dutch_oven_search():
    """Test the /api/search endpoint with Dutch Oven query"""
    url = "http://localhost:8000/api/search"

    payload = {
        "query": "dutch oven",
        "max_price": 500,
        "context": {
            "location": "United States"
        },
        "characteristics": {}
    }

    print("🔍 Testing Dutch Oven search...")
    print(f"📋 Request payload: {json.dumps(payload, indent=2)}")
    print("\n⏳ Sending request to backend...\n")

    async with httpx.AsyncClient(timeout=300.0) as client:
        try:
            response = await client.post(url, json=payload)
            response.raise_for_status()

            result = response.json()

            print("✅ Search completed successfully!")
            print(f"\n📊 Results Summary:")
            print(f"   - Good tier: {len(result.get('results', {}).get('good', []))} products")
            print(f"   - Better tier: {len(result.get('results', {}).get('better', []))} products")
            print(f"   - Best tier: {len(result.get('results', {}).get('best', []))} products")
            print(f"   - Total queries: {result.get('queries_generated', 0)}")
            print(f"   - Sources analyzed: {result.get('total_sources_analyzed', 0)}")
            print(f"   - Processing time: {result.get('processing_time_seconds', 0):.2f}s")
            print(f"   - From cache: {result.get('from_cache', False)}")

            # Show first product from each tier to verify new fields
            print("\n📦 Sample Products (checking new fields):")
            for tier_name in ['good', 'better', 'best']:
                tier_products = result.get('results', {}).get(tier_name, [])
                if tier_products:
                    product = tier_products[0]
                    print(f"\n   {tier_name.upper()} tier sample:")
                    print(f"      Name: {product.get('name', 'N/A')}")
                    print(f"      Brand: {product.get('brand', 'N/A')}")
                    print(f"      Price: ${product.get('value_metrics', {}).get('upfront_price', 'N/A')}")
                    print(f"      Materials: {product.get('materials', [])}")
                    print(f"      Key Differentiator: {product.get('key_differentiator', 'N/A')[:50]}...")
                    print(f"      Maintenance Tasks: {product.get('maintenance_tasks', [])}")
                    print(f"      Learning Curve: {product.get('learning_curve', 'N/A')[:50]}...")
                    print(f"      Drawbacks: {product.get('drawbacks', [])}")

            # Show search queries by phase
            print("\n🔎 Search Queries Executed:")
            search_queries = result.get('search_queries', [])
            if search_queries:
                phases = {}
                for sq in search_queries:
                    phase = sq.get('phase', 'Unknown')
                    if phase not in phases:
                        phases[phase] = []
                    phases[phase].append(sq.get('query', ''))

                for phase, queries in phases.items():
                    print(f"\n   {phase} ({len(queries)} queries):")
                    for q in queries[:3]:  # Show first 3
                        print(f"      - {q}")
                    if len(queries) > 3:
                        print(f"      ... and {len(queries) - 3} more")

            return result

        except httpx.HTTPError as e:
            print(f"❌ HTTP Error: {e}")
            if hasattr(e, 'response') and e.response:
                print(f"Response: {e.response.text}")
            return None
        except Exception as e:
            print(f"❌ Error: {e}")
            return None

if __name__ == "__main__":
    asyncio.run(test_dutch_oven_search())
