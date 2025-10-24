"""
Kenny Gem Finder - FastAPI Backend
AI-powered kitchen product search with Good/Better/Best tier system
"""
import os
import time
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from models import (
    SearchQuery,
    SearchResponse,
    HealthCheckResponse,
    ValueMetrics,
    ErrorResponse,
    TierResults,
    Product,
    TierLevel,
    WebSource
)
# from agent_service import get_agent  # Using simple_search instead for now
from simple_search import get_simple_search
from database_service import DatabaseService
from durability_scorer import get_durability_scorer, DurabilityScore as DurabilityScoreCalc

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Kenny Gem Finder API",
    description="AI-powered vertical search for kitchen products organized in Good/Better/Best tiers",
    version="0.1.0"
)

# Initialize database service
try:
    db_service = DatabaseService()
    print("✓ Database caching enabled")
except Exception as e:
    print(f"⚠️  Database caching disabled: {e}")
    db_service = None

# CORS middleware - configure for production later
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", response_model=HealthCheckResponse)
async def root():
    """Root endpoint - health check"""
    return HealthCheckResponse(
        status="healthy",
        version="0.1.0",
        environment=os.getenv("ENVIRONMENT", "development")
    )


@app.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """Health check endpoint"""
    return HealthCheckResponse(
        status="healthy",
        version="0.1.0",
        environment=os.getenv("ENVIRONMENT", "development")
    )


@app.get("/api/categories")
async def get_categories():
    """Return list of kitchen product categories"""
    return {
        "categories": [
            {
                "id": "knives",
                "name": "Knives & Cutting",
                "icon": "🔪",
                "description": "Chef's knives, paring knives, cutting boards, sharpeners"
            },
            {
                "id": "cookware",
                "name": "Cookware",
                "icon": "🍳",
                "description": "Skillets, pots, Dutch ovens, woks, roasting pans"
            },
            {
                "id": "bakeware",
                "name": "Bakeware",
                "icon": "🥖",
                "description": "Sheet pans, mixing bowls, measuring tools, rolling pins"
            },
            {
                "id": "tools",
                "name": "Kitchen Tools",
                "icon": "🥄",
                "description": "Peelers, tongs, spatulas, whisks, thermometers"
            },
            {
                "id": "storage",
                "name": "Storage",
                "icon": "📦",
                "description": "Containers, jars, organization systems"
            },
            {
                "id": "appliances",
                "name": "Small Appliances",
                "icon": "☕",
                "description": "Coffee makers, blenders, mixers, rice cookers"
            },
        ]
    }


@app.post("/api/calculate-value", response_model=ValueMetrics)
async def calculate_value(price: float, lifespan: float):
    """
    Calculate value metrics for a product

    Args:
        price: Product price in USD
        lifespan: Expected lifespan in years

    Returns:
        ValueMetrics with cost-per-year and cost-per-day calculations
    """
    try:
        return ValueMetrics.calculate(price, lifespan)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/search", response_model=SearchResponse)
async def search_products(query: SearchQuery):
    """
    AI-powered search using LangChain agent with Tavily tool.
    Returns products organized in Good/Better/Best tiers.
    Checks Supabase cache first to reduce API calls.
    """
    start_time = time.time()

    try:
        # Step 1: Check database cache first (TEMPORARILY DISABLED FOR TESTING)
        if False and db_service:  # Disabled temporarily
            print(f"🔍 Checking cache for query: '{query.query}'")
            cached_result = await db_service.get_cached_search(
                query=query.query,
                tier_preference=query.tier_preference,
                max_price=query.max_price
            )

            if cached_result:
                print("✓ Cache hit! Returning cached results")
                cached_result.search_metadata["cached"] = True
                return cached_result

            print("✗ Cache miss. Performing fresh search...")

        print("🔍 Cache disabled - performing fresh search...")

        # Step 2: No cache hit - perform fresh search
        # Get the search instance
        search = get_simple_search()

        # Search for products using AI
        agent_result = await search.search_products(
            query.query,
            query.context or {}
        )

        # Parse agent output into Product objects
        tier_results = _parse_tier_results(agent_result)

        # Parse before_you_buy section if present
        from models import BeforeYouBuy, AlternativeSolution
        before_you_buy = None
        if "before_you_buy" in agent_result and agent_result["before_you_buy"]:
            try:
                byb_data = agent_result["before_you_buy"]
                alternatives = []
                for alt in byb_data.get("alternatives", []):
                    alternatives.append(AlternativeSolution(
                        problem=alt.get("problem", ""),
                        consumer_solution=alt.get("consumer_solution", ""),
                        consumer_cost=float(alt.get("consumer_cost", 0)),
                        consumer_issues=alt.get("consumer_issues", []),
                        your_solution=alt.get("your_solution", ""),
                        your_cost=float(alt.get("your_cost", 0)),
                        why_better=alt.get("why_better", ""),
                        how_to=alt.get("how_to", ""),
                        savings_per_year=float(alt.get("savings_per_year", 0)),
                        when_to_buy_instead=alt.get("when_to_buy_instead")
                    ))

                before_you_buy = BeforeYouBuy(
                    title=byb_data.get("title", "Before You Buy..."),
                    subtitle=byb_data.get("subtitle", "Let's solve the problem first"),
                    alternatives=alternatives,
                    educational_insight=byb_data.get("educational_insight", "")
                )
            except Exception as e:
                print(f"⚠️  Failed to parse before_you_buy: {e}")

        # Calculate processing time
        processing_time = time.time() - start_time

        # Build response
        search_response = SearchResponse(
            before_you_buy=before_you_buy,
            results=tier_results,
            search_metadata={
                "sources_searched": agent_result.get("sources", []),
                "search_queries_used": agent_result.get("search_queries_used", []),
                "cached": False
            },
            processing_time_seconds=round(processing_time, 2),
            educational_insights=agent_result.get("educational_insights", [])
        )

        # Step 3: Cache the results for future queries
        if db_service:
            print("💾 Caching search results to database...")
            try:
                await db_service.cache_search_results(
                    query=query.query,
                    search_response=search_response,
                    tier_preference=query.tier_preference,
                    max_price=query.max_price,
                    context=query.context
                )
                print("✓ Results cached successfully")
            except Exception as cache_error:
                print(f"⚠️  Failed to cache results: {cache_error}")
                # Don't fail the request if caching fails

        return search_response

    except ValueError as e:
        # API key missing or configuration error
        raise HTTPException(
            status_code=500,
            detail=f"Configuration error: {str(e)}. Please check your API keys in .env file."
        )
    except Exception as e:
        # Other errors
        raise HTTPException(
            status_code=500,
            detail=f"Search failed: {str(e)}"
        )


def _parse_tier_results(agent_data: dict) -> TierResults:
    """
    Parse agent output into TierResults with Product objects

    Args:
        agent_data: Raw data from agent with good_tier, better_tier, best_tier

    Returns:
        TierResults object with parsed Product objects
    """
    def parse_product_list(products_data: list) -> list:
        """Parse a list of product dictionaries into Product objects"""
        parsed_products = []

        for product_data in products_data:
            try:
                # Calculate value metrics (convert to float in case AI returns strings)
                price = product_data.get("price", 0)
                lifespan = product_data.get("lifespan", 1)

                print(f"DEBUG: Parsing product '{product_data.get('name', 'unknown')}'")
                print(f"  price type: {type(price)}, value: {price}")
                print(f"  lifespan type: {type(lifespan)}, value: {lifespan}")

                # Convert to float if they're strings
                if isinstance(price, str):
                    price = float(price.replace("$", "").replace(",", ""))
                if isinstance(lifespan, str):
                    lifespan = float(lifespan)

                value_metrics = ValueMetrics.calculate(
                    price=float(price),
                    lifespan=float(lifespan)
                )

                # Parse web sources (handle both string URLs and dict objects)
                web_sources = []
                for source in product_data.get("web_sources", []):
                    if isinstance(source, str):
                        # If source is a URL string, create WebSource with just URL
                        web_sources.append(WebSource(
                            url=source,
                            title="Source",
                            snippet=""
                        ))
                    elif isinstance(source, dict):
                        # If source is a dict, parse it normally
                        web_sources.append(WebSource(
                            url=source.get("url", ""),
                            title=source.get("title", ""),
                            snippet=source.get("snippet", ""),
                            relevance_score=source.get("relevance_score")
                        ))

                # Handle trade_offs (might be string or list)
                trade_offs_raw = product_data.get("trade_offs", [])
                if isinstance(trade_offs_raw, str):
                    trade_offs = [trade_offs_raw] if trade_offs_raw else []
                else:
                    trade_offs = trade_offs_raw

                # Import DurabilityData model
                from models import DurabilityData

                # Check if agent has already extracted durability data
                if 'durability_data_extracted' in product_data:
                    # Use agent-extracted durability data (preferred)
                    extracted = product_data['durability_data_extracted']
                    durability_data = DurabilityData(
                        score=extracted.get('score', 75),
                        average_lifespan_years=float(extracted.get('average_lifespan_years', value_metrics.expected_lifespan_years)),
                        still_working_after_5years_percent=extracted.get('still_working_after_5years_percent', 75),
                        total_user_reports=extracted.get('total_user_reports', 0),
                        common_failure_points=extracted.get('common_failure_points', []),
                        repairability_score=extracted.get('repairability_score', 50),
                        material_quality_indicators=extracted.get('material_quality_indicators', []),
                        data_sources=extracted.get('data_sources', [])
                    )
                else:
                    # Fallback: Calculate durability score using durability_scorer
                    durability_scorer = get_durability_scorer()
                    durability_calc = durability_scorer.calculate_durability_score({
                        "expected_lifespan_years": product_data.get("lifespan", value_metrics.expected_lifespan_years),
                        "failure_percentage": product_data.get("failure_percentage"),
                        "reddit_mentions": product_data.get("reddit_mentions"),
                        "repairability_info": product_data.get("repairability_info"),
                        "maintenance_level": product_data.get("maintenance_level", "Medium"),
                        "materials": product_data.get("materials", []),
                        "why_gem": product_data.get("why_its_a_gem", ""),
                        "tier": product_data.get("tier", "better")
                    })

                    # Extract material quality indicators
                    material_indicators = [
                        mat.get("material", "") for mat in durability_calc.material_data.get("materials", [])
                    ]

                    # Build data sources list
                    data_sources = ["AI-analyzed Reddit discussions", "Product review aggregation"]

                    durability_data = DurabilityData(
                        score=durability_calc.total,
                        average_lifespan_years=float(durability_calc.longevity_data.get("expected_years", value_metrics.expected_lifespan_years)),
                        still_working_after_5years_percent=int((durability_calc.failure_rate_score / 25) * 100),
                        total_user_reports=durability_calc.failure_data.get("reddit_mentions", 0) or 0,
                        common_failure_points=[],  # Will be populated from AI analysis in future
                        repairability_score=int((durability_calc.repairability_score / 20) * 100),
                        material_quality_indicators=material_indicators,
                        data_sources=data_sources
                    )

                # Create Product object
                product = Product(
                    name=product_data.get("name", "Unknown Product"),
                    brand=product_data.get("brand", "Unknown Brand"),
                    tier=TierLevel(product_data.get("tier", "better")),
                    category=product_data.get("category", "kitchen product"),
                    value_metrics=value_metrics,
                    durability_data=durability_data,
                    key_features=product_data.get("key_features", []),
                    materials=product_data.get("materials", []),
                    why_its_a_gem=product_data.get("why_its_a_gem", ""),
                    web_sources=web_sources,
                    reddit_mentions=product_data.get("reddit_mentions"),
                    professional_reviews=product_data.get("professional_reviews", []),
                    maintenance_level=product_data.get("maintenance_level", "Medium"),
                    purchase_links=product_data.get("purchase_links", []),
                    environmental_warnings=product_data.get("environmental_warnings"),
                    best_for=product_data.get("best_for", ""),
                    trade_offs=trade_offs
                )

                parsed_products.append(product)

            except Exception as e:
                # Skip products that fail to parse
                import traceback
                print(f"Failed to parse product: {e}")
                print(f"Full traceback:")
                traceback.print_exc()
                print(f"Product data: {product_data}")
                continue

        return parsed_products

    # Parse each tier
    return TierResults(
        good=parse_product_list(agent_data.get("good_tier", [])),
        better=parse_product_list(agent_data.get("better_tier", [])),
        best=parse_product_list(agent_data.get("best_tier", []))
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
