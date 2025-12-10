#!/usr/bin/env python3
"""
Unit tests for backend alignment verification
Tests the changes made to ensure agents output correctly aligns with parsing/database code
"""

import pytest
from models import Product, QualityData, PracticalMetrics, WebSource, SearchMetrics
from quality_scorer import QualityScorer


class TestProductModel:
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

        assert product.drawbacks == ["Heavy", "Expensive"]
        assert product.why_its_a_gem == "It's great!"
        assert product.category == "test category"

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
        assert not hasattr(product, 'trade_offs')

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
        assert product.name == "Test Knife"
        assert product.brand == "Test Brand"
        assert product.category == "chef's knife"
        assert product.materials == ["stainless steel"]
        assert len(product.key_features) == 2
        assert product.key_differentiator == "Best value"
        assert product.why_its_a_gem is not None
        assert len(product.maintenance_tasks) == 2
        assert product.learning_curve == "Easy to use"
        assert len(product.drawbacks) == 2
        assert len(product.professional_reviews) == 1
        assert product.best_for == "Home cooks"
        assert product.price == 79.99
        assert product.expected_lifespan_years == 15.0
        assert product.tier == "better"


class TestQualityScorer:
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
        assert result.total > 0
        assert result.longevity_score > 0
        assert result.material_score > 0

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
        assert score > 0
        assert data is not None

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
        assert result.total > 0


class TestFieldNaming:
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
        assert "drawbacks" in product_dict
        assert "why_its_a_gem" in product_dict
        assert "category" in product_dict

        # Verify old field names NOT present
        assert "trade_offs" not in product_dict
        assert "why_gem" not in product_dict


class TestBackwardCompatibility:
    """Test backward compatibility for cached data"""

    def test_product_handles_missing_optional_fields(self):
        """Test that Product handles missing optional fields gracefully"""
        # Minimal required fields
        product = Product(
            name="Test",
            brand="Brand",
            price=50.0,
            expected_lifespan_years=10.0,
            tier="good"
        )

        # Should have default values for optional fields
        assert product.drawbacks == []
        assert product.materials == []
        assert product.key_features == []


class TestValueFramework:
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
        assert hasattr(product, 'name')
        assert hasattr(product, 'brand')
        assert hasattr(product, 'category')
        assert hasattr(product, 'materials')
        assert hasattr(product, 'key_features')
        assert hasattr(product, 'why_its_a_gem')

        # SERVICE (3 fields)
        assert hasattr(product, 'maintenance_tasks')
        assert hasattr(product, 'learning_curve')
        assert hasattr(product, 'drawbacks')

        # EQUITY (2 fields)
        assert hasattr(product, 'professional_reviews')
        assert hasattr(product, 'best_for')

        # PRICE (2 fields)
        assert hasattr(product, 'price')
        assert hasattr(product, 'expected_lifespan_years')

        # ACTION (1 field)
        assert hasattr(product, 'purchase_links')

        # TIER (1 field)
        assert hasattr(product, 'tier')


class TestQualityData:
    """Test QualityData model"""

    def test_quality_data_creation(self):
        """Test QualityData model with proper structure"""
        quality = QualityData(
            total=85,
            longevity_score=35,
            failure_rate_score=20,
            repairability_score=18,
            material_score=12,
            longevity_data={"years": 20},
            failure_data={"rate": "5%"},
            repairability_data={"level": "Easy"},
            material_data={"materials": [{"material": "cast iron", "quality": "Premium"}]},
            data_sources=["expert reviews"]
        )

        assert quality.total == 85
        assert quality.material_score == 12


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
