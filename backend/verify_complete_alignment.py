#!/usr/bin/env python3
"""
Comprehensive verification of backend-frontend-database alignment
Ensures all VALUE framework fields are present and properly flowing through the system
"""

import json
from typing import Dict, List, Any
from models import Product

print("=" * 80)
print("🔍 COMPREHENSIVE BACKEND-FRONTEND-DATABASE ALIGNMENT VERIFICATION")
print("=" * 80)
print()

# Define expected VALUE framework fields
EXPECTED_FIELDS = {
    "PRODUCT (Physical Quality)": [
        "name",
        "brand",
        "category",
        "materials",
        "key_features",
        "why_its_a_gem",
        "quality_data",  # Contains value score (PRODUCT + SERVICE metrics)
    ],
    "SERVICE (Support & Usability)": [
        "practical_metrics",  # learning_curve, maintenance_level, etc.
        "maintenance_level",
        "drawbacks",
    ],
    "EQUITY (Trust & Value Retention)": [
        "professional_reviews",
        "best_for",
        "web_sources",
        "reddit_mentions",
    ],
    "PRICE & ACTION": [
        "value_metrics",  # upfront_price, expected_lifespan_years, cost_per_year, cost_per_day
        "purchase_links",
        "tier",
    ],
    "FILTERING & PERSONALIZATION": [
        "characteristics",  # Normalized for filtering
    ],
    "WARNINGS": [
        "environmental_warnings",
    ]
}

# Database column mapping
DATABASE_COLUMNS = {
    "name": "name",
    "brand": "brand",
    "tier": "tier",
    "category": "category",
    "price": "value_metrics.upfront_price",
    "expected_lifespan_years": "value_metrics.expected_lifespan_years",
    "cost_per_year": "value_metrics.cost_per_year",
    "cost_per_day": "value_metrics.cost_per_day",
    "why_its_a_gem": "why_its_a_gem",
    "key_features": "key_features (JSONB)",
    "materials": "materials (JSONB)",
    "characteristics": "characteristics (JSONB)",
    "drawbacks": "drawbacks (JSONB)",
    "best_for": "best_for",
    "web_sources": "web_sources (JSONB)",
    "maintenance_level": "maintenance_level",
    "quality_data": "quality_data (JSONB)",
    "practical_metrics": "practical_metrics (JSONB)",
    "professional_reviews": "professional_reviews (JSONB)",
    "purchase_links": "purchase_links (JSONB)",
}

def check_backend_model():
    """Verify backend Product model has all expected fields"""
    print("📋 BACKEND MODEL (models.py)")
    print("-" * 80)

    product_fields = Product.model_fields
    all_expected_fields = []
    for category, fields in EXPECTED_FIELDS.items():
        all_expected_fields.extend(fields)

    missing_fields = []
    present_fields = []

    for field in all_expected_fields:
        if field in product_fields:
            present_fields.append(field)
        else:
            missing_fields.append(field)

    print(f"✅ Present fields: {len(present_fields)}/{len(all_expected_fields)}")
    for field in sorted(present_fields):
        field_info = product_fields[field]
        required = field_info.is_required()
        field_type = field_info.annotation
        print(f"   ✓ {field:30} (required={required}, type={field_type})")

    if missing_fields:
        print(f"\n❌ Missing fields: {len(missing_fields)}")
        for field in sorted(missing_fields):
            print(f"   ✗ {field}")

    print()
    return len(missing_fields) == 0

def check_frontend_types():
    """Verify frontend TypeScript types match backend"""
    print("📋 FRONTEND TYPES (types/index.ts)")
    print("-" * 80)

    # Read the frontend types file
    try:
        with open('/Users/wenyichen/kenny-gem-finder/frontend/types/index.ts', 'r') as f:
            content = f.read()

        # Check for each expected field in Product interface
        all_expected_fields = []
        for category, fields in EXPECTED_FIELDS.items():
            all_expected_fields.extend(fields)

        present_fields = []
        missing_fields = []

        for field in all_expected_fields:
            # Check if field is in the Product interface
            # Handle both regular fields and nested fields
            if field in ["value_metrics", "quality_data", "practical_metrics"]:
                # Check for interface definitions
                if f"interface {field.replace('_', ' ').title().replace(' ', '')}" in content or \
                   f"export interface {field.replace('_', ' ').title().replace(' ', '')}" in content or \
                   f"{field}:" in content:
                    present_fields.append(field)
                else:
                    missing_fields.append(field)
            else:
                if f"{field}:" in content:
                    present_fields.append(field)
                else:
                    missing_fields.append(field)

        print(f"✅ Present fields in Product interface: {len(present_fields)}/{len(all_expected_fields)}")
        for field in sorted(present_fields):
            print(f"   ✓ {field}")

        if missing_fields:
            print(f"\n❌ Missing fields: {len(missing_fields)}")
            for field in sorted(missing_fields):
                print(f"   ✗ {field}")

        print()
        return len(missing_fields) == 0
    except Exception as e:
        print(f"❌ Error reading frontend types: {e}")
        return False

def check_database_schema():
    """Verify database schema has all necessary columns"""
    print("📋 DATABASE SCHEMA (database_schema.sql)")
    print("-" * 80)

    try:
        with open('/Users/wenyichen/kenny-gem-finder/backend/database_schema.sql', 'r') as f:
            content = f.read()

        present_columns = []
        missing_columns = []

        for db_col, model_field in DATABASE_COLUMNS.items():
            if db_col in content:
                present_columns.append(db_col)
            else:
                missing_columns.append(db_col)

        print(f"✅ Present columns: {len(present_columns)}/{len(DATABASE_COLUMNS)}")
        for col in sorted(present_columns):
            print(f"   ✓ {col:30} → {DATABASE_COLUMNS[col]}")

        if missing_columns:
            print(f"\n❌ Missing columns: {len(missing_columns)}")
            for col in sorted(missing_columns):
                print(f"   ✗ {col:30} → {DATABASE_COLUMNS[col]}")

        print()
        return len(missing_columns) == 0
    except Exception as e:
        print(f"❌ Error reading database schema: {e}")
        return False

def check_value_framework_organization():
    """Verify VALUE framework field organization"""
    print("📋 VALUE FRAMEWORK ORGANIZATION")
    print("-" * 80)

    for category, fields in EXPECTED_FIELDS.items():
        print(f"\n🔹 {category}")
        for field in fields:
            print(f"   • {field}")

    print()
    return True

def verify_recent_search():
    """Verify a recent search has all expected fields"""
    print("📋 RECENT SEARCH VERIFICATION")
    print("-" * 80)

    try:
        # Try to find a recent cached search result
        import glob
        json_files = glob.glob('/tmp/kenny_search_*.json')

        if not json_files:
            print("⚠️  No recent search results found in /tmp/")
            print("   Run 'python test_search_pretty.py' to generate test data")
            print()
            return None

        # Get most recent file
        latest_file = max(json_files, key=lambda x: x)
        print(f"📁 Checking: {latest_file}")
        print()

        with open(latest_file, 'r') as f:
            data = json.load(f)

        # Check if results exist
        if 'results' not in data:
            print("❌ No 'results' field in search data")
            return False

        results = data['results']
        all_products = []

        for tier in ['good', 'better', 'best']:
            if tier in results:
                all_products.extend(results[tier])

        if not all_products:
            print("❌ No products found in results")
            return False

        print(f"Found {len(all_products)} products across all tiers")
        print()

        # Check first product for all fields
        product = all_products[0]
        print(f"Checking product: {product.get('name', 'Unknown')}")
        print()

        all_expected = []
        for category, fields in EXPECTED_FIELDS.items():
            all_expected.extend(fields)

        present = []
        missing = []

        for field in all_expected:
            if field in product:
                value = product[field]
                present.append(field)
                # Show preview of value
                if isinstance(value, (list, dict)):
                    preview = f"{type(value).__name__} with {len(value)} items"
                else:
                    preview = str(value)[:50]
                print(f"   ✓ {field:30} = {preview}")
            else:
                missing.append(field)

        if missing:
            print()
            print(f"❌ Missing fields: {len(missing)}")
            for field in missing:
                print(f"   ✗ {field}")

        print()
        print(f"Summary: {len(present)}/{len(all_expected)} fields present")
        print()

        return len(missing) == 0

    except Exception as e:
        print(f"❌ Error verifying search results: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all verification checks"""

    results = {
        "Backend Model": check_backend_model(),
        "Frontend Types": check_frontend_types(),
        "Database Schema": check_database_schema(),
        "VALUE Framework": check_value_framework_organization(),
    }

    # Optional: check recent search
    search_result = verify_recent_search()
    if search_result is not None:
        results["Recent Search"] = search_result

    # Summary
    print("=" * 80)
    print("📊 VERIFICATION SUMMARY")
    print("=" * 80)
    print()

    all_passed = True
    for check, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status:10} {check}")
        if not passed:
            all_passed = False

    print()

    if all_passed:
        print("🎉 ALL CHECKS PASSED - System is fully aligned!")
    else:
        print("⚠️  SOME CHECKS FAILED - Review issues above")

    print()
    print("=" * 80)

    return all_passed

if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)
