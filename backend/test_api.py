"""
Test script for Kenny Gem Finder API
"""
import requests
import json

# Test AI search endpoint
print("Testing AI-powered search (this may take 10-30 seconds)...")
print("=" * 60)

search_data = {
    "query": "I need a cast iron skillet that won't rust easily",
    "context": {
        "experience_level": "beginner"
    }
}

try:
    response = requests.post(
        "http://localhost:8000/api/search",
        json=search_data,
        timeout=120
    )

    print(f"Status Code: {response.status_code}")
    print("=" * 60)

    if response.status_code == 200:
        result = response.json()
        print(json.dumps(result, indent=2))
        print("\n" + "=" * 60)
        print("SUCCESS! AI search is working!")
        print("=" * 60)
    else:
        print(f"Error: {response.text}")

except requests.exceptions.Timeout:
    print("Request timed out (> 120 seconds)")
except Exception as e:
    print(f"Error: {e}")
