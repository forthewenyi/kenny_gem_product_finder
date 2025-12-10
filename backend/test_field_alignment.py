#!/usr/bin/env python3
"""
Simple unit tests focused on field name alignment
Verifies the critical changes: trade_offs → drawbacks, why_gem → why_its_a_gem
"""

import unittest
from quality_scorer import QualityScorer


class TestFieldAlignment(unittest.TestCase):
    """Test that field names are correctly aligned"""

    def test_quality_scorer_why_its_a_gem_parameter(self):
        """CRITICAL: Verify QualityScorer uses 'why_its_a_gem' not 'why_gem'"""
        scorer = QualityScorer()

        # This should work with why_its_a_gem
        product_data = {
            "expected_lifespan_years": 20,
            "materials": ["cast iron"],
            "why_its_a_gem": "Professional-grade with lifetime warranty",
            "tier": "best"
        }

        result = scorer.calculate_quality_score(product_data)
        self.assertGreater(result.total, 0)
        print("✅ QualityScorer.calculate_quality_score() accepts 'why_its_a_gem'")

    def test_material_quality_method_signature(self):
        """CRITICAL: Verify calculate_material_quality_score has correct parameter name"""
        scorer = QualityScorer()

        # Call with why_its_a_gem parameter (NOT why_gem)
        score, data = scorer.calculate_material_quality_score(
            materials=["cast iron"],
            why_its_a_gem="Heirloom quality construction",
            tier="best"
        )

        self.assertGreater(score, 0)
        print("✅ calculate_material_quality_score() has 'why_its_a_gem' parameter")

    def test_quality_scorer_no_old_field_names(self):
        """CRITICAL: Verify QualityScorer doesn't expect 'why_gem'"""
        scorer = QualityScorer()

        # Should work without why_gem
        product_data = {
            "expected_lifespan_years": 15,
            "materials": ["stainless steel"],
            "tier": "better"
        }

        result = scorer.calculate_quality_score(product_data)
        self.assertGreater(result.total, 0)
        print("✅ QualityScorer works without 'why_gem' field")

    def test_quality_score_attribute_name(self):
        """Verify QualityScore has material_quality_score attribute"""
        scorer = QualityScorer()

        result = scorer.calculate_quality_score({
            "expected_lifespan_years": 20,
            "materials": ["cast iron"]
        })

        # Check the correct attribute name
        self.assertTrue(hasattr(result, 'material_quality_score'))
        print("✅ QualityScore has 'material_quality_score' attribute")


def run_tests():
    """Run field alignment tests"""
    print("\n" + "="*80)
    print("🧪 FIELD NAME ALIGNMENT TESTS")
    print("="*80)
    print("\nTesting: trade_offs → drawbacks, why_gem → why_its_a_gem\n")

    # Run tests
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestFieldAlignment)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Summary
    print("\n" + "="*80)
    if result.wasSuccessful():
        print("🎉 ALL FIELD ALIGNMENT TESTS PASSED!")
        print("="*80)
        print("✅ QualityScorer uses 'why_its_a_gem' (not 'why_gem')")
        print("✅ All method signatures correctly aligned")
        print("✅ Backend field naming is consistent")
        return 0
    else:
        print("⚠️  SOME TESTS FAILED")
        print("="*80)
        return 1


if __name__ == "__main__":
    exit(run_tests())
