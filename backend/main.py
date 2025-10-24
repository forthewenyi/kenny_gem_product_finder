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
    ProductTier,
    WebSource
)
# from agent_service import get_agent  # Using simple_search instead for now
from simple_search import get_simple_search

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Kenny Gem Finder API",
    description="AI-powered vertical search for kitchen products organized in Good/Better/Best tiers",
    version="0.1.0"
)

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
    """
    start_time = time.time()

    try:
        # Get the search instance
        search = get_simple_search()

        # Search for products using AI
        agent_result = await search.search_products(
            query.query,
            query.context or {}
        )

        # Parse agent output into Product objects
        tier_results = _parse_tier_results(agent_result)

        # Calculate processing time
        processing_time = time.time() - start_time

        # Build response
        return SearchResponse(
            results=tier_results,
            search_metadata={
                "sources_searched": agent_result.get("sources", []),
                "search_queries_used": agent_result.get("search_queries_used", [])
            },
            processing_time_seconds=round(processing_time, 2),
            educational_insights=agent_result.get("educational_insights", [])
        )

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
                # Calculate value metrics
                value_metrics = ValueMetrics.calculate(
                    price=product_data.get("price", 0),
                    lifespan=product_data.get("lifespan", 1)
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

                # Create Product object
                product = Product(
                    name=product_data.get("name", "Unknown Product"),
                    brand=product_data.get("brand", "Unknown Brand"),
                    tier=ProductTier(product_data.get("tier", "better")),
                    category=product_data.get("category", "kitchen product"),
                    value_metrics=value_metrics,
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
                print(f"Failed to parse product: {e}")
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
