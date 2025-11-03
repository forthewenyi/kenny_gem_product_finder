#!/usr/bin/env python3
"""Quick test to check actual API response format"""
import requests
import json

# Make a simple search request
response = requests.post(
    "http://localhost:8000/api/search",
    json={"query": "chef knife", "context": {}}
)

data = response.json()

# Check one product from each tier
for tier in ["good", "better", "best"]:
    if data["results"][tier]:
        product = data["results"][tier][0]
        print(f"\n{'='*80}")
        print(f"{tier.upper()} TIER - First Product:")
        print(f"{'='*80}")
        print(f"Name: {product['name']}")
        print(f"\nMaterials type: {type(product.get('materials'))}")
        print(f"Materials value: {product.get('materials')}")
        print(f"Materials count: {len(product.get('materials', []))}")

        print(f"\nKey Features type: {type(product.get('key_features'))}")
        print(f"Key Features value: {product.get('key_features')[:100] if product.get('key_features') else None}")
        print(f"Key Features count: {len(product.get('key_features', []))}")

        print(f"\nCharacteristics type: {type(product.get('characteristics'))}")
        print(f"Characteristics value: {product.get('characteristics')}")
        break
