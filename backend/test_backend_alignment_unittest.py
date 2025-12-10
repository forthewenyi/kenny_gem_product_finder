#!/usr/bin/env python3
"""
Unit tests for backend alignment verification using unittest
Tests the changes made to ensure agents output correctly aligns with parsing/database code
"""

import unittest
from models import Product, QualityData
from quality_scorer import QualityScorer


class TestProductModel(unittest.TestCase):
    """Test Product model with new field names"""

    def test_product_with_drawbacks(self):
        """Test that Product model accepts 'drawbacks' field"""
        product = Product(
            name="Test Product",
            brand="Test Brand",
            price=99.99,
            expected_lifespan_years=10.0,
            tier="better",
            drawbacks=["Heavy", "Expensive"],
            why_its_a_gem="It's great!",
            category="test category"
        )

        self.assertEqual(product.drawbacks, ["Heavy", "Expensive"])
        self.assertEqual(product.why_its_a_gem, "It's great!")
        self.assertEqual(product.category, "test category")
        print("✅ PASS: Product accepts 'drawbacks' field")

    def test_product_no_trade_offs_field(self):
        """Verify Product model does NOT have 'trade_offs' field"""
        product = Product(
            name="Test Product",
            brand="Test Brand",
            price=99.99,
            expected_lifespan_years=10.0,
            tier="better"
        )

        # Should not have trade_offs attribute
        self.assertFalse(hasattr(product, 'trade_offs'))
        print("✅ PASS: Product does NOT have 'trade_offs' field")

    def test_product_with_all_15_fields(self):
        """Test Product model with all 15 VALUE framework fields"""
        product = Product(
            name="Test Knife",
            brand="Test Brand",
            category="chef's knife",
            materials=["stainless steel"],
            key_features=["Sharp", "Durable"],
            key_differentiator="Best value",
            why_its_a_gem="Professional quality at budget price",
            maintenance_tasks=["Hand wash", "Hone regularly"],
            learning_curve="Easy to use",
            drawbacks=["Heavy", "Requires care"],
            professional_reviews=["Wirecutter Pick"],
            best_for="Home cooks",
            price=79.99,
            expected_lifespan_years=15.0,
            tier="better"
        )

        # Verify all 15 fields present
        self.assertEqual(product.name, "Test Knife")
        self.assertEqual(product.brand, "Test Brand")
        self.assertEqual(product.category, "chef's knife")
        self.assertEqual(product.materials, ["stainless steel"])
        self.assertEqual(len(product.key_features), 2)
        self.assertEqual(product.key_differentiator, "Best value")
        self.assertIsNotNone(product.why_its_a_gem)
        self.assertEqual(len(product.maintenance_tasks), 2)
        self.assertEqual(product.learning_curve, "Easy to use")
        self.assertEqual(len(product.drawbacks), 2)
        self.assertEqual(len(product.professional_reviews), 1)
        self.assertEqual(product.best_for, "Home cooks")
        self.assertEqual(product.price, 79.99)
        self.assertEqual(product.expected_lifespan_years, 15.0)
        self.assertEqual(product.tier, "better")
        print("✅ PASS: Product has all 15 VALUE framework fields")


class TestQualityScorer(unittest.TestCase):
    """Test QualityScorer with correct field names"""

    def test_quality_scorer_accepts_why_its_a_gem(self):
        """Test that QualityScorer accepts 'why_its_a_gem' not 'why_gem'"""
        scorer = QualityScorer()

        product_data = {
            "expected_lifespan_years": 20,
            "materials": ["cast iron"],
            "why_its_a_gem": "Professional-grade construction with lifetime warranty",
            "tier": "best",
            "maintenance_level": "Medium"
        }

        result = scorer.calculate_quality_score(product_data)

        # Should calculate successfully
        self.assertGreater(result.total, 0)
        self.assertGreater(result.longevity_score, 0)
        self.assertGreater(result.material_score, 0)
        print("✅ PASS: QualityScorer accepts 'why_its_a_gem'")

    def test_quality_scorer_material_quality_parameter(self):
        """Test that calculate_material_quality_score uses 'why_its_a_gem' parameter"""
        scorer = QualityScorer()

        # Call the material quality method directly
        score, data = scorer.calculate_material_quality_score(
            materials=["cast iron"],
            why_its_a_gem="Heirloom quality construction",
            tier="best"
        )

        # Should boost score for quality indicators
        self.assertGreater(score, 0)
        self.assertIsNotNone(data)
        print("✅ PASS: Material quality scorer uses 'why_its_a_gem' parameter")

    def test_quality_scorer_without_why_gem(self):
        """Verify quality scorer doesn't expect old 'why_gem' field"""
        scorer = QualityScorer()

        # This should work fine without why_gem
        product_data = {
            "expected_lifespan_years": 15,
            "materials": ["stainless steel"],
            "tier": "better"
        }

        result = scorer.calculate_quality_score(product_data)
        self.assertGreater(result.total, 0)
        print("✅ PASS: QualityScorer works without 'why_gem' field")


class TestFieldNaming(unittest.TestCase):
    """Test that field naming is consistent"""

    def test_product_json_serialization(self):
        """Test that Product serializes with correct field names"""
        product = Product(
            name="Test",
            brand="Brand",
            price=50.0,
            expected_lifespan_years=10.0,
            tier="good",
            drawbacks=["Heavy"],
            why_its_a_gem="Great value",
            category="test"
        )

        # Convert to dict (as would happen in API response)
        product_dict = product.dict()

        # Verify correct field names in output
        self.assertIn("drawbacks", product_dict)
        self.assertIn("why_its_a_gem", product_dict)
        self.assertIn("category", product_dict)

        # Verify old field names NOT present
        self.assertNotIn("trade_offs", product_dict)
        self.assertNotIn("why_gem", product_dict)
        print("✅ PASS: Product serializes with correct field names")


class TestValueFramework(unittest.TestCase):
    """Test VALUE framework structure (15 fields organized)"""

    def test_value_framework_fields_present(self):
        """Verify all VALUE framework fields are in Product model"""
        product = Product(
            name="Test",
            brand="Brand",
            price=50.0,
            expected_lifespan_years=10.0,
            tier="good"
        )

        # PRODUCT (6 fields)
        self.assertTrue(hasattr(product, 'name'))
        self.assertTrue(hasattr(product, 'brand'))
        self.assertTrue(hasattr(product, 'category'))
        self.assertTrue(hasattr(product, 'materials'))
        self.assertTrue(hasattr(product, 'key_features'))
        self.assertTrue(hasattr(product, 'why_its_a_gem'))

        # SERVICE (3 fields)
        self.assertTrue(hasattr(product, 'maintenance_tasks'))
        self.assertTrue(hasattr(product, 'learning_curve'))
        self.assertTrue(hasattr(product, 'drawbacks'))

        # EQUITY (2 fields)
        self.assertTrue(hasattr(product, 'professional_reviews'))
        self.assertTrue(hasattr(product, 'best_for'))

        # PRICE (2 fields)
        self.assertTrue(hasattr(product, 'price'))
        self.assertTrue(hasattr(product, 'expected_lifespan_years'))

        # ACTION (1 field)
        self.assertTrue(hasattr(product, 'purchase_links'))

        # TIER (1 field)
        self.assertTrue(hasattr(product, 'tier'))
        print("✅ PASS: All VALUE framework fields present in Product model")


def run_tests():
    """Run all unit tests"""
    print("\n" + "="*80)
    print("🧪 BACKEND ALIGNMENT UNIT TESTS")
    print("="*80 + "\n")

    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestProductModel))
    suite.addTests(loader.loadTestsFromTestCase(TestQualityScorer))
    suite.addTests(loader.loadTestsFromTestCase(TestFieldNaming))
    suite.addTests(loader.loadTestsFromTestCase(TestValueFramework))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Summary
    print("\n" + "="*80)
    print("📊 TEST SUMMARY")
    print("="*80)
    print(f"✅ Tests run: {result.testsRun}")
    print(f"✅ Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"❌ Failures: {len(result.failures)}")
    print(f"❌ Errors: {len(result.errors)}")

    if result.wasSuccessful():
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ Backend alignment verified successfully")
        return 0
    else:
        print("\n⚠️  SOME TESTS FAILED")
        return 1


if __name__ == "__main__":
    exit(run_tests())
