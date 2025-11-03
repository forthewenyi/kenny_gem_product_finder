"""
Test the API endpoint with ADK search integration
"""
import requests
import json

# Test API endpoint
API_URL = "http://localhost:8000/api/search"

def test_adk_api():
    print("🧪 Testing ADK API integration...")
    print(f"📡 Sending request to {API_URL}\n")

    # Make search request
    response = requests.post(API_URL, json={
        "query": "cast iron skillet",
        "max_price": 100
    })

    print(f"📊 Status Code: {response.status_code}\n")

    if response.status_code == 200:
        data = response.json()

        print("✅ API Response Structure:")
        print(f"  - Results keys: {list(data.get('results', {}).keys())}")
        print(f"  - Good tier products: {len(data['results']['good'])}")
        print(f"  - Better tier products: {len(data['results']['better'])}")
        print(f"  - Best tier products: {len(data['results']['best'])}")
        print(f"  - Processing time: {data.get('processing_time_seconds')}s")
        print(f"  - Aggregated characteristics: {len(data.get('aggregated_characteristics', []))}")

        # Check first product from good tier
        if data['results']['good']:
            product = data['results']['good'][0]
            print(f"\n📦 Sample Product (Good Tier):")
            print(f"  - Name: {product.get('name')}")
            print(f"  - Brand: {product.get('brand')}")
            print(f"  - Price: ${product['value_metrics']['upfront_price']}")
            print(f"  - Lifespan: {product['value_metrics']['expected_lifespan_years']} years")
            print(f"  - Materials: {', '.join(product.get('materials', []))}")
            print(f"  - Key features: {len(product.get('key_features', []))} features")
            print(f"  - Characteristics: {len(product.get('characteristics', []))} characteristics")
            print(f"  - Why it's a gem: {product.get('why_its_a_gem', '')[:100]}...")

        print("\n✅ ADK API integration successful!")
        return True
    else:
        print(f"❌ API Error: {response.status_code}")
        print(response.text)
        return False


if __name__ == "__main__":
    test_adk_api()
