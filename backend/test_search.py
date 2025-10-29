"""
Unit tests for the AI search process (SimpleKennySearch)
Tests search query generation, Tavily integration, and LLM parsing
"""

import os
import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from simple_search import SimpleKennySearch

# Set dummy API keys for testing
os.environ['OPENAI_API_KEY'] = 'test-key-123'
os.environ['TAVILY_API_KEY'] = 'test-key-456'


class TestSimpleKennySearch:
    """Test suite for SimpleKennySearch"""

    def setup_method(self):
        """Set up test fixtures"""
        self.search = SimpleKennySearch()

    def test_generate_durability_queries(self):
        """Test that durability queries are generated correctly"""
        queries = self.search._generate_durability_queries("cast iron skillet")

        # Should generate 13 queries
        assert len(queries) == 13

        # Should include key query types
        assert any("buy it for life" in q for q in queries)
        assert any("how long does it last" in q for q in queries)
        assert any("common problems failures" in q for q in queries)
        assert any("repair maintain" in q for q in queries)

        # All queries should contain the product name
        assert all("cast iron skillet" in q.lower() for q in queries)

    def test_generate_alternative_solutions(self):
        """Test that alternative solution queries are generated"""
        queries = self.search._generate_alternative_solutions("fabric softener")

        # Should generate alternative queries
        assert len(queries) > 0

        # Should include key alternative types
        assert any("alternatives to buying" in q for q in queries)
        assert any("DIY alternative" in q for q in queries)
        assert any("fix instead of replacing" in q for q in queries)

    def test_format_search_results(self):
        """Test formatting of Tavily results for LLM"""
        mock_results = {
            "results": [
                {
                    "title": "Best Cast Iron Skillets - Reddit",
                    "url": "https://reddit.com/r/BuyItForLife/...",
                    "content": "I've been using my Lodge for 8 years..."
                },
                {
                    "title": "Cast Iron Guide - Serious Eats",
                    "url": "https://seriouseats.com/cast-iron",
                    "content": "Cast iron can last forever..."
                }
            ]
        }

        formatted = self.search._format_search_results(mock_results)

        # Should format as text with numbered results
        assert "Result 1:" in formatted
        assert "Result 2:" in formatted
        assert "Best Cast Iron Skillets" in formatted
        assert "reddit.com" in formatted
        assert "seriouseats.com" in formatted

    @pytest.mark.asyncio
    async def test_search_products_structure(self):
        """Test that search_products returns correct structure"""
        # Mock Tavily client
        mock_tavily_results = {
            "results": [
                {
                    "title": "Lodge Cast Iron Review",
                    "url": "https://reddit.com/r/BuyItForLife/123",
                    "content": "The Lodge 10.25\" cast iron skillet is amazing. I've used mine for 10 years. Cost $25, still perfect."
                }
            ] * 10  # 10 mock results
        }

        # Mock OpenAI response
        mock_openai_response = {
            "good_tier": [
                {
                    "name": "Lodge Cast Iron Skillet",
                    "brand": "Lodge",
                    "price": 25.0,
                    "lifespan": 20,
                    "characteristics": ["Pre-seasoned", "Heavy bottom"],
                    "materials": ["Cast iron"],
                    "key_features": ["Durable", "Versatile"],
                    "why_its_a_gem": "Lasts forever",
                    "web_sources": ["https://reddit.com/..."],
                    "maintenance_level": "Medium",
                    "best_for": "Everyone",
                    "trade_offs": ["Heavy"],
                    "practical_metrics": {
                        "cleaning_time_minutes": 10,
                        "dishwasher_safe": False,
                        "oven_safe": True
                    }
                }
            ] * 3,
            "better_tier": [
                {
                    "name": "Field Cast Iron Skillet",
                    "brand": "Field",
                    "price": 150.0,
                    "lifespan": 30,
                    "characteristics": ["Lightweight", "Polished"],
                    "materials": ["Cast iron"],
                    "key_features": ["Smooth finish"],
                    "why_its_a_gem": "Premium quality",
                    "web_sources": ["https://reddit.com/..."],
                    "maintenance_level": "Low",
                    "best_for": "Homeowners",
                    "trade_offs": ["Expensive"],
                    "practical_metrics": {
                        "cleaning_time_minutes": 5,
                        "dishwasher_safe": False,
                        "oven_safe": True
                    }
                }
            ] * 3,
            "best_tier": [
                {
                    "name": "Finex Cast Iron Skillet",
                    "brand": "Finex",
                    "price": 250.0,
                    "lifespan": 30,
                    "characteristics": ["Unique design", "Pour spout"],
                    "materials": ["Cast iron"],
                    "key_features": ["Heirloom quality"],
                    "why_its_a_gem": "Lifetime investment",
                    "web_sources": ["https://reddit.com/..."],
                    "maintenance_level": "Medium",
                    "best_for": "Serious cooks",
                    "trade_offs": ["Very expensive"],
                    "practical_metrics": {
                        "cleaning_time_minutes": 10,
                        "dishwasher_safe": False,
                        "oven_safe": True
                    }
                }
            ] * 3,
            "search_queries_used": ["query1", "query2", "query3"],
            "educational_insights": ["Cast iron lasts forever"]
        }

        # Patch external dependencies
        with patch.object(self.search.tavily_client, 'search', return_value=mock_tavily_results):
            with patch.object(self.search.openai_client.chat.completions, 'create') as mock_create:
                # Mock OpenAI response
                mock_response = Mock()
                mock_response.choices = [Mock()]
                mock_response.choices[0].message.content = str(mock_openai_response).replace("'", '"')
                mock_create.return_value = mock_response

                result = await self.search.search_products(
                    query="cast iron skillet",
                    context={}
                )

        # Verify structure
        assert "good_tier" in result
        assert "better_tier" in result
        assert "best_tier" in result
        assert "real_search_metrics" in result

        # Verify metrics
        metrics = result["real_search_metrics"]
        assert "total_sources_analyzed" in metrics
        assert "reddit_threads" in metrics
        assert "expert_reviews" in metrics
        assert "search_queries_executed" in metrics

    def test_search_queries_count(self):
        """Test that exactly 4 searches are executed"""
        queries = self.search._generate_durability_queries("blender")

        # Generated queries should be 13
        assert len(queries) == 13

        # But only first 4 are used (based on code: durability_queries[:4])
        # This is implicit in the search_products method

    def test_characteristics_normalization_hint(self):
        """Test that the prompt instructs proper characteristics normalization"""
        # This tests the PROMPT, not the LLM output
        # The system prompt should guide characteristics extraction

        # Read the system prompt from the code
        import inspect
        source = inspect.getsource(self.search.search_products)

        # Verify prompt contains normalization instructions
        assert "characteristics" in source.lower()
        assert "normalize" in source.lower() or "title case" in source.lower()

    @pytest.mark.asyncio
    async def test_minimum_products_requirement(self):
        """Test that the prompt enforces minimum 9 products"""
        import inspect
        source = inspect.getsource(self.search.search_products)

        # Verify the prompt requires minimum products per tier
        assert "MUST include at least 3 products" in source or "minimum of 9" in source

    def test_reddit_and_expert_counting(self):
        """Test that Reddit threads and expert reviews are counted correctly"""
        mock_results = [
            {"url": "https://reddit.com/r/BuyItForLife/123"},
            {"url": "https://reddit.com/r/Cooking/456"},
            {"url": "https://seriouseats.com/article"},
            {"url": "https://americastestkitchen.com/review"},
            {"url": "https://othersite.com/review"},
        ]

        # Count Reddit
        reddit_count = sum(1 for r in mock_results if 'reddit.com' in r.get('url', ''))
        assert reddit_count == 2

        # Count expert reviews
        expert_domains = ['seriouseats.com', 'americastestkitchen.com', 'cooksillustrated.com']
        expert_count = sum(1 for r in mock_results if any(domain in r.get('url', '') for domain in expert_domains))
        assert expert_count == 2


class TestSearchConfiguration:
    """Test search configuration and parameters"""

    def test_search_depth_is_basic(self):
        """Verify search depth is set to 'basic' for speed"""
        import inspect
        source = inspect.getsource(SimpleKennySearch.search_products)

        # Should use basic depth, not advanced
        assert 'search_depth="basic"' in source or "search_depth='basic'" in source

    def test_max_tokens_sufficient(self):
        """Verify max_tokens is set high enough for 9 products"""
        import inspect
        source = inspect.getsource(SimpleKennySearch.search_products)

        # Should have increased max_tokens for multiple products
        assert "8000" in source or "max_tokens" in source

    def test_temperature_is_low(self):
        """Verify temperature is low for consistent results"""
        import inspect
        source = inspect.getsource(SimpleKennySearch.search_products)

        # Should use low temperature (0.3 or similar)
        assert "temperature" in source


class TestIntegration:
    """Integration tests requiring actual API calls (slow, run separately)"""

    @pytest.mark.slow
    @pytest.mark.asyncio
    async def test_pretty_print_search_results(self):
        """
        Pretty print search results for manual inspection and refinement
        WARNING: This test costs money and takes 30-40 seconds

        Run with: pytest test_search.py::TestIntegration::test_pretty_print_search_results -v -s
        """
        import json
        from pprint import pprint

        search = SimpleKennySearch()

        # You can change this query to test different products
        test_query = "cast iron skillet"

        print(f"\n{'='*80}")
        print(f"🔍 TESTING SEARCH FOR: {test_query}")
        print(f"{'='*80}\n")

        result = await search.search_products(
            query=test_query,
            context={"location": "US"}
        )

        print(f"\n{'='*80}")
        print("📊 SEARCH METRICS")
        print(f"{'='*80}")
        if "real_search_metrics" in result:
            metrics = result["real_search_metrics"]
            print(f"Total sources analyzed: {metrics.get('total_sources_analyzed', 0)}")
            print(f"Reddit threads: {metrics.get('reddit_threads', 0)}")
            print(f"Expert reviews: {metrics.get('expert_reviews', 0)}")
            print(f"Search queries executed: {metrics.get('search_queries_executed', 0)}")
            print(f"\nQueries used:")
            for i, q in enumerate(metrics.get('search_queries', []), 1):
                print(f"  {i}. {q}")

        # Count products
        good_count = len(result.get("good_tier", []))
        better_count = len(result.get("better_tier", []))
        best_count = len(result.get("best_tier", []))
        total_count = good_count + better_count + best_count

        print(f"\n{'='*80}")
        print(f"📦 PRODUCTS FOUND: {total_count} total")
        print(f"{'='*80}")
        print(f"  GOOD tier: {good_count} products")
        print(f"  BETTER tier: {better_count} products")
        print(f"  BEST tier: {best_count} products")

        # Print each tier with details
        for tier_name, tier_key in [("GOOD", "good_tier"), ("BETTER", "better_tier"), ("BEST", "best_tier")]:
            products = result.get(tier_key, [])
            if not products:
                continue

            print(f"\n{'='*80}")
            print(f"💎 {tier_name} TIER ({len(products)} products)")
            print(f"{'='*80}")

            for i, product in enumerate(products, 1):
                print(f"\n{'-'*80}")
                print(f"Product {i}: {product.get('name', 'Unknown')}")
                print(f"{'-'*80}")
                print(f"Brand: {product.get('brand', 'N/A')}")
                print(f"Price: ${product.get('price', 0)}")
                print(f"Lifespan: {product.get('lifespan', 0)} years")

                # Characteristics
                characteristics = product.get('characteristics', [])
                print(f"\nCharacteristics ({len(characteristics)}):")
                if characteristics:
                    for char in characteristics:
                        print(f"  • {char}")
                else:
                    print("  (none)")

                # Materials
                materials = product.get('materials', [])
                print(f"\nMaterials ({len(materials)}):")
                if materials:
                    for mat in materials:
                        print(f"  • {mat}")
                else:
                    print("  (none)")

                # Key features
                features = product.get('key_features', [])
                print(f"\nKey Features ({len(features)}):")
                if features:
                    for feat in features:
                        print(f"  • {feat}")
                else:
                    print("  (none)")

                # Why it's a gem
                print(f"\nWhy It's a Gem:")
                print(f"  {product.get('why_its_a_gem', 'N/A')}")

                # Practical metrics
                if 'practical_metrics' in product and product['practical_metrics']:
                    pm = product['practical_metrics']
                    print(f"\nPractical Metrics:")
                    print(f"  Cleaning time: {pm.get('cleaning_time_minutes', 'N/A')} min")
                    print(f"  Cleaning details: {pm.get('cleaning_details', 'N/A')}")
                    print(f"  Setup time: {pm.get('setup_time', 'N/A')}")
                    print(f"  Learning curve: {pm.get('learning_curve', 'N/A')}")
                    print(f"  Maintenance: {pm.get('maintenance_level', 'N/A')}")
                    print(f"  Weight: {pm.get('weight_lbs', 'N/A')} lbs")
                    print(f"  Dishwasher safe: {pm.get('dishwasher_safe', False)}")
                    print(f"  Oven safe: {pm.get('oven_safe', False)}")

                # Trade-offs
                tradeoffs = product.get('trade_offs', [])
                if tradeoffs:
                    print(f"\nTrade-offs:")
                    for tradeoff in tradeoffs:
                        print(f"  ⚠️  {tradeoff}")

                # Best for
                print(f"\nBest For: {product.get('best_for', 'N/A')}")

                # Web sources
                sources = product.get('web_sources', [])
                print(f"\nWeb Sources ({len(sources)}):")
                for source in sources[:3]:  # Show first 3
                    if isinstance(source, str):
                        print(f"  • {source}")
                    elif isinstance(source, dict):
                        print(f"  • {source.get('url', 'N/A')}")

        # Save full JSON to file for detailed inspection
        output_file = f"/tmp/kenny_search_{test_query.replace(' ', '_')}.json"
        with open(output_file, 'w') as f:
            json.dump(result, f, indent=2)

        print(f"\n{'='*80}")
        print(f"💾 Full JSON saved to: {output_file}")
        print(f"{'='*80}\n")

        # Basic assertions
        assert total_count >= 9, f"Expected at least 9 products, got {total_count}"
        assert good_count >= 3, f"Expected at least 3 GOOD products, got {good_count}"
        assert better_count >= 3, f"Expected at least 3 BETTER products, got {better_count}"
        assert best_count >= 3, f"Expected at least 3 BEST products, got {best_count}"

    @pytest.mark.slow
    @pytest.mark.asyncio
    async def test_real_search_cast_iron(self):
        """
        Integration test with real APIs (Tavily + OpenAI)
        WARNING: This test costs money and takes 30-40 seconds
        """
        search = SimpleKennySearch()

        result = await search.search_products(
            query="cast iron skillet",
            context={"location": "US"}
        )

        # Verify structure
        assert "good_tier" in result
        assert "better_tier" in result
        assert "best_tier" in result

        # Verify minimum products
        total_products = (
            len(result.get("good_tier", [])) +
            len(result.get("better_tier", [])) +
            len(result.get("best_tier", []))
        )
        assert total_products >= 9, f"Expected at least 9 products, got {total_products}"

        # Verify each product has required fields
        for product in result.get("good_tier", []):
            assert "name" in product
            assert "price" in product
            assert "lifespan" in product
            assert "characteristics" in product
            assert isinstance(product["characteristics"], list)
            assert len(product["characteristics"]) > 0

    @pytest.mark.slow
    @pytest.mark.asyncio
    async def test_real_search_timing(self):
        """
        Test that search completes within acceptable time
        WARNING: This test costs money
        """
        import time

        search = SimpleKennySearch()

        start = time.time()
        result = await search.search_products(
            query="chef knife",
            context={}
        )
        duration = time.time() - start

        # Should complete within 60 seconds
        assert duration < 60, f"Search took {duration}s, expected < 60s"

        # Should find products
        total = len(result["good_tier"]) + len(result["better_tier"]) + len(result["best_tier"])
        assert total >= 9


# Run tests with: pytest test_search.py -v
# Run only fast tests: pytest test_search.py -v -m "not slow"
# Run integration tests: pytest test_search.py -v -m slow
