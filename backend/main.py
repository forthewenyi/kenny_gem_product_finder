"""
Kenny Gem Finder - FastAPI Backend
AI-powered kitchen product search with Good/Better/Best tier system
"""
import os
import time
import asyncio
import uuid
from typing import Dict
from pathlib import Path
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
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
    WebSource,
    QualityData
)
from adk_search import get_adk_search  # ADK-powered multi-agent search with Google Agent Development Kit
from database_service import DatabaseService
from quality_scorer import get_quality_scorer, QualityScore as QualityScoreCalc
from characteristic_generator import get_characteristic_generator
from popular_search_service import get_popular_search_service
from auth_middleware import (
    verify_password,
    create_access_token,
    get_current_user,
    get_optional_user
)

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Kenny Gem Finder API",
    description="AI-powered vertical search for kitchen products organized in Good/Better/Best tiers",
    version="0.1.0"
)

# Initialize database service
# Database schema updated to match current Product model
# TEMPORARILY DISABLED for testing new agent logic
# try:
#     db_service = DatabaseService()
#     print("✅ Database caching enabled")
# except Exception as e:
#     print(f"⚠️  Database caching disabled: {e}")
#     db_service = None

db_service = None
print("🔍 Cache DISABLED for testing")

# Progress tracking for WebSocket real-time updates
# Maps search_id -> callback function to emit progress events
progress_callbacks: Dict[str, callable] = {}

# CORS middleware - configure for production later
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# STATIC FILE SERVING (Frontend)
# ============================================================================

# Path to frontend build output
FRONTEND_BUILD_DIR = Path(__file__).parent / "static"

# Mount static files (Next.js _next directory with JS bundles, CSS, etc.)
if (FRONTEND_BUILD_DIR / "_next").exists():
    app.mount("/_next", StaticFiles(directory=str(FRONTEND_BUILD_DIR / "_next")), name="next-static")
    print("✅ Serving frontend static files from /static/_next")

# Serve other static assets
if FRONTEND_BUILD_DIR.exists():
    app.mount("/static-assets", StaticFiles(directory=str(FRONTEND_BUILD_DIR)), name="static-assets")
    print(f"✅ Frontend build directory: {FRONTEND_BUILD_DIR}")
else:
    print(f"⚠️  Frontend build directory not found: {FRONTEND_BUILD_DIR}")
    print("   Run 'npm run build' in frontend directory and copy output to backend/static")


@app.get("/")
async def serve_frontend():
    """Serve the frontend index.html"""
    index_path = FRONTEND_BUILD_DIR / "index.html"
    if index_path.exists():
        return FileResponse(index_path)
    else:
        # Fallback health check if frontend not built
        return {
            "status": "healthy",
            "version": "0.1.0",
            "environment": os.getenv("ENVIRONMENT", "development"),
            "message": "Frontend not built. Run build-frontend.sh to include frontend."
        }


@app.websocket("/ws/search-progress")
async def websocket_search_progress(websocket: WebSocket, token: str = None):
    """
    WebSocket endpoint for real-time search progress updates.

    The client sends a search query, receives a search_id, then gets progress updates
    as the ADK agents research and find products.

    Requires authentication token as query parameter: /ws/search-progress?token=<jwt_token>
    """
    # Verify authentication token
    from auth_middleware import verify_token
    if not token or not verify_token(token):
        await websocket.close(code=1008, reason="Unauthorized")
        return

    await websocket.accept()
    search_id = str(uuid.uuid4())

    print(f"🔌 WebSocket connected: search_id={search_id}")

    try:
        # Wait for the search query from client
        data = await websocket.receive_json()
        query = data.get("query")
        max_price = data.get("max_price")
        context = data.get("context")
        characteristics = data.get("characteristics")

        # Send search_id to client
        await websocket.send_json({
            "type": "search_started",
            "search_id": search_id,
            "query": query
        })

        # Define progress callback that sends updates to WebSocket
        async def send_progress(event_type: str, message: str, data: dict = None):
            try:
                await websocket.send_json({
                    "type": event_type,
                    "message": message,
                    "data": data or {},
                    "timestamp": time.time()
                })
            except Exception as e:
                print(f"⚠️  Error sending WebSocket message: {e}")

        # Register callback
        progress_callbacks[search_id] = send_progress

        # Start the search with progress tracking
        await send_progress("agent_start", "Starting research...", {"agent": "context_discovery"})

        # Run the ADK search with progress callback
        agent_result = await get_adk_search(
            query=query,
            max_price=max_price,
            user_context=context,
            characteristics=characteristics,
            progress_callback=send_progress
        )

        # Send completion
        await send_progress("search_complete", "Research complete!", {
            "products_found": len(agent_result.get("good_tier", [])) +
                             len(agent_result.get("better_tier", [])) +
                             len(agent_result.get("best_tier", []))
        })

    except WebSocketDisconnect:
        print(f"🔌 WebSocket disconnected: search_id={search_id}")
    except Exception as e:
        print(f"❌ WebSocket error: {e}")
        try:
            await websocket.send_json({
                "type": "error",
                "message": str(e)
            })
        except:
            pass
    finally:
        # Cleanup
        if search_id in progress_callbacks:
            del progress_callbacks[search_id]


@app.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """Health check endpoint"""
    return HealthCheckResponse(
        status="healthy",
        version="0.1.0",
        environment=os.getenv("ENVIRONMENT", "development")
    )


@app.get("/debug/env")
async def debug_env():
    """DEBUG ENDPOINT: Check if environment variables are loaded (remove after debugging)"""
    password = os.getenv("PORTFOLIO_ACCESS_PASSWORD")
    jwt_secret = os.getenv("JWT_SECRET_KEY")

    return {
        "portfolio_password_set": password is not None,
        "portfolio_password_length": len(password) if password else 0,
        "portfolio_password_first3": password[:3] if password else None,
        "jwt_secret_set": jwt_secret is not None,
        "jwt_secret_length": len(jwt_secret) if jwt_secret else 0,
        "environment": os.getenv("ENVIRONMENT"),
        "all_env_vars": list(os.environ.keys())
    }


# ============================================================================
# AUTHENTICATION ENDPOINTS (for password-protected portfolio access)
# ============================================================================

class LoginRequest(BaseModel):
    """Request model for login endpoint"""
    password: str


class LoginResponse(BaseModel):
    """Response model for successful login"""
    access_token: str
    token_type: str = "bearer"
    message: str = "Access granted"


@app.post("/api/auth/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """
    Verify access password and return JWT token.
    This protects the portfolio project from public access.
    """
    if not verify_password(request.password):
        raise HTTPException(
            status_code=401,
            detail="Incorrect access code. Please contact portfolio owner for access."
        )

    # Create access token
    access_token = create_access_token(data={"access": "granted"})

    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        message="Access granted. Welcome to Kenny Gem Finder!"
    )


@app.get("/api/auth/verify")
async def verify_auth(current_user: dict = Depends(get_current_user)):
    """
    Verify if current token is valid.
    Protected endpoints use this dependency.
    """
    return {"authenticated": True, "access": "granted"}


# ============================================================================
# PUBLIC ENDPOINTS
# ============================================================================

@app.get("/api/categories")
async def get_categories(current_user: dict = Depends(get_current_user)):
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


@app.post("/api/generate-characteristics")
async def generate_characteristics(query: str, location: str = "US"):
    """
    Generate 5 buying characteristics for a product search query

    Args:
        query: Product search query (e.g., "cast iron skillet", "chef's knife")
        location: User location (e.g., "Austin, TX", "Seattle, WA")

    Returns:
        List of 5 characteristics with label, reason, explanation, and image_keyword
    """
    try:
        generator = get_characteristic_generator()
        characteristics = generator.generate_characteristics(query, location)
        return {"characteristics": characteristics}
    except ValueError as e:
        raise HTTPException(status_code=500, detail=f"Configuration error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate characteristics: {str(e)}")


@app.get("/api/popular-searches/{category}")
async def get_popular_searches(category: str, limit: int = 8, current_user: dict = Depends(get_current_user)):
    """
    Get top N most searched items for a category (for dropdown menus)

    Args:
        category: One of 'cookware', 'knives', 'bakeware'
        limit: Maximum number of results to return (default 8)

    Returns:
        List of popular search terms with counts
    """
    try:
        # Validate category
        if category not in ['cookware', 'knives', 'bakeware', 'small_appliances', 'kitchen_tools']:
            raise HTTPException(status_code=400, detail="Invalid category. Must be one of: cookware, knives, bakeware, small_appliances, kitchen_tools")

        search_service = get_popular_search_service()
        results = await search_service.get_popular_searches(category, limit)

        return {
            "category": category,
            "items": results
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch popular searches: {str(e)}")


@app.post("/api/track-search")
async def track_search(query: str, category: str):
    """
    Track a search term to update popular searches (fire-and-forget from frontend)

    Args:
        query: The search term (e.g., "Cast Iron Skillet")
        category: One of 'cookware', 'knives', 'bakeware'

    Returns:
        Success status
    """
    try:
        # Validate category
        if category not in ['cookware', 'knives', 'bakeware', 'small_appliances', 'kitchen_tools']:
            raise HTTPException(status_code=400, detail="Invalid category. Must be one of: cookware, knives, bakeware, small_appliances, kitchen_tools")

        search_service = get_popular_search_service()
        success = await search_service.track_search(query, category)

        return {"success": success, "query": query, "category": category}
    except HTTPException:
        raise
    except Exception as e:
        # Don't fail on tracking errors - just log and return success=false
        print(f"Error tracking search: {e}")
        return {"success": False, "query": query, "category": category}


@app.post("/api/search", response_model=SearchResponse)
async def search_products(query: SearchQuery, current_user: dict = Depends(get_current_user)):
    """
    AI-powered search using Google Gemini 2.0 Flash + Google Search.
    Uses contextual AI-driven query generation with 5-phase research framework.
    Returns products organized in Good/Better/Best tiers.
    Checks Supabase cache first to reduce API calls.
    """
    start_time = time.time()

    try:
        # Step 1: Check database cache first
        if db_service:  # Caching enabled - checks Supabase cache
            print(f"🔍 Checking cache for query: '{query.query}'")
            cached_result = await db_service.get_cached_search(
                query=query.query,
                tier_preference=query.tier_preference,
                max_price=query.max_price
            )

            if cached_result:
                print("✓ Cache hit! Returning cached results")
                cached_result.search_metadata["cached"] = True

                # Handle old cache entries that don't have new fields
                if not hasattr(cached_result, 'aggregated_characteristics') or cached_result.aggregated_characteristics is None:
                    # Regenerate aggregated characteristics from products
                    from collections import Counter
                    from models import AggregatedCharacteristic

                    all_products = cached_result.results.good + cached_result.results.better + cached_result.results.best
                    characteristic_counts = Counter()
                    characteristic_products = {}

                    for product in all_products:
                        if hasattr(product, 'characteristics') and product.characteristics:
                            for char in product.characteristics:
                                characteristic_counts[char] += 1
                                if char not in characteristic_products:
                                    characteristic_products[char] = []
                                characteristic_products[char].append(product.name)

                    cached_result.aggregated_characteristics = [
                        AggregatedCharacteristic(
                            label=char,
                            count=count,
                            product_names=characteristic_products[char]
                        )
                        for char, count in characteristic_counts.most_common(10)
                    ]

                # Handle old cache entries without real_search_metrics
                if not hasattr(cached_result, 'real_search_metrics') or cached_result.real_search_metrics is None:
                    from models import RealSearchMetrics
                    # Provide placeholder metrics for cached results
                    cached_result.real_search_metrics = RealSearchMetrics(
                        total_sources_analyzed=0,
                        reddit_threads=0,
                        expert_reviews=0,
                        search_queries_executed=0,
                        search_queries=[],
                        unique_sources=0
                    )

                return cached_result

            print("✗ Cache miss. Performing fresh search...")
        else:
            print("🔍 Cache disabled - performing fresh search...")

        # Step 2: No cache hit - perform fresh search
        # Use ADK-powered multi-agent search

        # Log personalized search if characteristics provided
        if query.characteristics:
            print(f"🎯 Personalized search with characteristics: {query.characteristics}")

        # Search for products using ADK agents
        agent_result = await get_adk_search(
            query=query.query,
            max_price=query.max_price,
            location="United States",
            user_context=query.context or {},
            characteristics=query.characteristics or {}
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

        # Aggregate characteristics from all products
        from collections import Counter
        from models import AggregatedCharacteristic, RealSearchMetrics

        all_products = tier_results.good + tier_results.better + tier_results.best
        characteristic_counts = Counter()
        characteristic_products = {}  # Track which products have each characteristic

        for product in all_products:
            for char in product.characteristics:
                characteristic_counts[char] += 1
                if char not in characteristic_products:
                    characteristic_products[char] = []
                characteristic_products[char].append(product.name)

        # Sort by count descending and create AggregatedCharacteristic objects
        aggregated_characteristics = [
            AggregatedCharacteristic(
                label=char,
                count=count,
                product_names=characteristic_products[char]
            )
            for char, count in characteristic_counts.most_common(10)  # Top 10 characteristics
        ]

        # Generate AI buying characteristics
        from models import BuyingCharacteristic
        buying_characteristics = None
        try:
            print(f"🤖 Generating AI buying characteristics for query: {query.query}")
            generator = get_characteristic_generator()
            ai_chars = await generator.generate_characteristics(
                query=query.query,
                location="United States",
                context=query.context or {}
            )
            # Convert to BuyingCharacteristic model
            buying_characteristics = [
                BuyingCharacteristic(
                    label=char["label"],
                    reason=char["reason"],
                    explanation=char["explanation"],
                    image_keyword=char["image_keyword"]
                )
                for char in ai_chars
            ]
            print(f"✓ Generated {len(buying_characteristics)} buying characteristics")
        except Exception as e:
            print(f"⚠️  Failed to generate buying characteristics: {e}")
            # Continue without buying characteristics

        # Parse real search metrics if provided
        real_search_metrics = None
        search_queries_list = None
        total_sources = None
        queries_generated_count = None
        sources_by_phase_data = None

        if "real_search_metrics" in agent_result:
            metrics_data = agent_result["real_search_metrics"]
            real_search_metrics = RealSearchMetrics(
                total_sources_analyzed=metrics_data.get("total_sources_analyzed", 0),
                reddit_threads=metrics_data.get("reddit_threads", 0),
                expert_reviews=metrics_data.get("expert_reviews", 0),
                search_queries_executed=metrics_data.get("search_queries_executed", 0),
                search_queries=metrics_data.get("search_queries", []),
                unique_sources=metrics_data.get("unique_sources", 0)
            )

            # Build search transparency fields for frontend
            from models import PhaseQueryInfo, SourcesByPhase

            # Format search queries with phase info
            search_queries_list = []
            sources_by_phase_dict = metrics_data.get("sources_by_phase", {})

            print(f"DEBUG: sources_by_phase_dict keys: {list(sources_by_phase_dict.keys())}")
            print(f"DEBUG: sources_by_phase_dict: {sources_by_phase_dict}")

            for phase_name, phase_data in sources_by_phase_dict.items():
                if isinstance(phase_data, dict) and "queries" in phase_data:
                    queries = phase_data["queries"]
                    print(f"DEBUG: Phase '{phase_name}' has {len(queries)} queries")
                    for query_text in queries:
                        search_queries_list.append(PhaseQueryInfo(
                            phase=phase_name,
                            query=query_text
                        ))

            print(f"DEBUG: Total search_queries_list items: {len(search_queries_list)}")

            # Extract metrics
            total_sources = metrics_data.get("total_sources_analyzed", 0)
            queries_generated_count = metrics_data.get("queries_generated", 0)

            # Build sources by phase
            sources_by_phase_data = SourcesByPhase(
                context_discovery=sources_by_phase_dict.get("context_discovery", {}).get("count", 0) if isinstance(sources_by_phase_dict.get("context_discovery"), dict) else 0,
                product_finder=sources_by_phase_dict.get("product_finder", {}).get("count", 0) if isinstance(sources_by_phase_dict.get("product_finder"), dict) else 0,
                synthesis=sources_by_phase_dict.get("synthesis", {}).get("count", 0) if isinstance(sources_by_phase_dict.get("synthesis"), dict) else 0
            )

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
            educational_insights=agent_result.get("educational_insights", []),
            aggregated_characteristics=aggregated_characteristics,
            buying_characteristics=buying_characteristics,
            real_search_metrics=real_search_metrics,
            # Search transparency fields
            search_queries=search_queries_list,
            total_sources_analyzed=total_sources,
            queries_generated=queries_generated_count,
            sources_by_phase=sources_by_phase_data
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

        def parse_lifespan_to_years(lifespan) -> float:
            """
            Parse lifespan string to numeric years.
            Handles formats: "2-5 years", "30+ years", "15 years", "Lifetime", "Generations", "Decades", or plain numbers.
            Returns average for ranges, minimum for "+" format.
            """
            if isinstance(lifespan, (int, float)):
                return float(lifespan)

            if not isinstance(lifespan, str):
                return 1.0  # Default fallback

            # Remove "years" and clean up
            lifespan_str = lifespan.lower().replace("years", "").replace("year", "").strip()

            # Strip parenthetical text to avoid breaking range parsing
            # e.g., "5-10 (or more with careful handling)" → "5-10"
            import re
            lifespan_str = re.sub(r'\([^)]*\)', '', lifespan_str).strip()

            # Handle special lifetime keywords (before numeric parsing)
            if "lifetime" in lifespan_str and "generation" in lifespan_str:
                # "Lifetime / Generations" → 75 years (multiple generations)
                return 75.0
            elif "lifetime" in lifespan_str:
                # "Lifetime" → 50 years (buy-it-for-life quality)
                return 50.0
            elif "generation" in lifespan_str:
                # "Generations" → 75 years (heirloom quality)
                return 75.0
            elif "decade" in lifespan_str:
                # "Decades" → 30 years (multiple decades estimated)
                return 30.0

            # Handle range format: "2-5" → average
            if "-" in lifespan_str:
                try:
                    parts = lifespan_str.split("-")
                    start = float(parts[0].strip())
                    end = float(parts[1].strip().replace("+", ""))
                    return (start + end) / 2.0
                except (ValueError, IndexError):
                    return 1.0

            # Handle "30+" format → use minimum
            if "+" in lifespan_str:
                try:
                    return float(lifespan_str.replace("+", "").strip())
                except ValueError:
                    return 1.0

            # Handle plain number: "15" → 15
            try:
                return float(lifespan_str)
            except ValueError:
                return 1.0

        for product_data in products_data:
            try:
                # Calculate value metrics (convert to float in case AI returns strings)
                price = product_data.get("price")
                lifespan = product_data.get("lifespan")

                print(f"DEBUG: Parsing product '{product_data.get('name', 'unknown')}'")
                print(f"  price type: {type(price)}, value: {price}")
                print(f"  lifespan type: {type(lifespan)}, value: {lifespan}")

                # Handle None values and convert to defaults
                if price is None or price == "" or (isinstance(price, str) and price.lower() == "unknown"):
                    print(f"  ⚠️  Price is None/empty/unknown, skipping product '{product_data.get('name', 'unknown')}'")
                    continue  # Skip products without price data

                if lifespan is None or lifespan == "":
                    lifespan = "5"  # Default to 5 years if no lifespan provided

                # Convert to float if they're strings
                if isinstance(price, str):
                    # Remove $ and commas, and extract first number if multiple
                    price_clean = price.replace("$", "").replace(",", "").strip()
                    # Handle cases like "210 (average)" - extract just the number
                    if " " in price_clean:
                        price_clean = price_clean.split()[0]
                    price = float(price_clean)

                # Parse lifespan (handles ranges like "2-5 years")
                lifespan = parse_lifespan_to_years(lifespan)
                print(f"  lifespan parsed to: {lifespan} years")

                value_metrics = ValueMetrics.calculate(
                    price=float(price),
                    lifespan=float(lifespan)
                )

                # Web sources - agents don't output this, create placeholder from purchase links
                web_sources = []
                purchase_links = product_data.get("purchase_links", [])
                if purchase_links:
                    # Create web source from first purchase link as reference
                    first_link = purchase_links[0]
                    if isinstance(first_link, dict) and "url" in first_link:
                        web_sources.append(WebSource(
                            url=first_link["url"],
                            title=first_link.get("name", "Product Page"),
                            snippet=f"Purchase link for {product_data.get('name', 'product')}"
                        ))

                # Handle drawbacks (might be string or list)
                drawbacks_raw = product_data.get("drawbacks", [])
                if isinstance(drawbacks_raw, str):
                    # Split by period for sentence-based drawbacks
                    if ". " in drawbacks_raw:
                        drawbacks = [t.strip() for t in drawbacks_raw.split(". ") if t.strip()]
                    else:
                        drawbacks = [drawbacks_raw] if drawbacks_raw else []
                else:
                    drawbacks = drawbacks_raw

                # Import QualityData model
                from models import QualityData

                # Check if agent has already extracted quality data
                if 'quality_data_extracted' in product_data:
                    # Use agent-extracted quality data (preferred)
                    extracted = product_data['quality_data_extracted']
                    quality_data = QualityData(
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
                    # Fallback: Calculate quality score using quality_scorer
                    quality_scorer = get_quality_scorer()
                    quality_calc = quality_scorer.calculate_quality_score({
                        "expected_lifespan_years": lifespan,  # Use parsed numeric lifespan
                        "failure_percentage": product_data.get("failure_percentage"),
                        "reddit_mentions": product_data.get("reddit_mentions"),
                        "repairability_info": product_data.get("repairability_info"),
                        "maintenance_level": product_data.get("maintenance_level", "Medium"),
                        "materials": product_data.get("materials", []),
                        "why_its_a_gem": product_data.get("why_its_a_gem", ""),
                        "tier": product_data.get("tier", "better")
                    })

                    # Extract material quality indicators
                    material_indicators = [
                        mat.get("material", "") for mat in quality_calc.material_data.get("materials", [])
                    ]

                    # Build data sources list
                    data_sources = ["AI-analyzed Reddit discussions", "Product review aggregation"]

                    quality_data = QualityData(
                        score=quality_calc.total,
                        average_lifespan_years=float(quality_calc.longevity_data.get("expected_years", value_metrics.expected_lifespan_years)),
                        still_working_after_5years_percent=int((quality_calc.failure_rate_score / 25) * 100),
                        total_user_reports=quality_calc.failure_data.get("reddit_mentions", 0) or 0,
                        common_failure_points=[],  # Will be populated from AI analysis in future
                        repairability_score=int((quality_calc.repairability_score / 20) * 100),
                        material_quality_indicators=material_indicators,
                        data_sources=data_sources
                    )

                # Parse practical_metrics if provided by AI
                from models import PracticalMetrics
                import re
                practical_metrics = None
                if 'practical_metrics' in product_data and product_data['practical_metrics']:
                    pm_data = product_data['practical_metrics']

                    # Extract cleaning_time_minutes from strings like "1 minute" or "5 minutes"
                    cleaning_time = pm_data.get('cleaning_time_minutes') or pm_data.get('cleaning_time')
                    cleaning_time_minutes = None
                    if cleaning_time:
                        if isinstance(cleaning_time, (int, float)):
                            cleaning_time_minutes = int(cleaning_time)
                        elif isinstance(cleaning_time, str):
                            match = re.search(r'(\d+)', cleaning_time)
                            if match:
                                cleaning_time_minutes = int(match.group(1))

                    # Extract weight_lbs from strings like "6.3 ounces" or "1.5 lbs"
                    weight = pm_data.get('weight_lbs') or pm_data.get('weight')
                    weight_lbs = None
                    if weight:
                        if isinstance(weight, (int, float)):
                            weight_lbs = float(weight)
                        elif isinstance(weight, str):
                            match = re.search(r'([\d.]+)', weight)
                            if match:
                                value = float(match.group(1))
                                # Convert ounces to pounds if necessary
                                if 'oz' in weight.lower() or 'ounce' in weight.lower():
                                    weight_lbs = value / 16.0
                                else:
                                    weight_lbs = value

                    practical_metrics = PracticalMetrics(
                        cleaning_time_minutes=cleaning_time_minutes,
                        cleaning_details=pm_data.get('cleaning_details', ''),
                        setup_time=pm_data.get('setup_time', 'Ready'),
                        setup_details=pm_data.get('setup_details', ''),
                        learning_curve=pm_data.get('learning_curve', 'Medium'),
                        learning_details=pm_data.get('learning_details', ''),
                        maintenance_level=pm_data.get('maintenance_level', 'Medium'),
                        maintenance_details=pm_data.get('maintenance_details', ''),
                        weight_lbs=weight_lbs,
                        weight_notes=pm_data.get('weight_notes'),
                        dishwasher_safe=pm_data.get('dishwasher_safe', False),
                        oven_safe=pm_data.get('oven_safe', False),
                        oven_max_temp=pm_data.get('oven_max_temp')
                    )

                # Normalize fields that should be lists (AI sometimes returns strings or dicts)
                # Fix: If materials is a single string, split by comma or keep as single-item list
                materials = product_data.get("materials", [])
                if isinstance(materials, str):
                    # Split by comma if it contains multiple materials
                    if "," in materials:
                        materials = [m.strip() for m in materials.split(",") if m.strip()]
                    else:
                        materials = [materials] if materials else []

                # Fix: If key_features is a single string, split by period or keep as single-item list
                key_features = product_data.get("key_features", [])
                if isinstance(key_features, str):
                    # Split by period for sentence-based features
                    if ". " in key_features:
                        key_features = [f.strip() for f in key_features.split(". ") if f.strip()]
                    else:
                        key_features = [key_features] if key_features else []

                characteristics = product_data.get("characteristics", [])
                if isinstance(characteristics, str):
                    # Split by comma if it contains multiple characteristics
                    if "," in characteristics:
                        characteristics = [c.strip() for c in characteristics.split(",") if c.strip()]
                    else:
                        characteristics = [characteristics] if characteristics else []
                elif isinstance(characteristics, dict):
                    # Convert dict to list of "key: value" strings
                    characteristics = [f"{k}: {v}" for k, v in characteristics.items()]

                # Derive maintenance_level from maintenance_tasks if not provided
                maintenance_tasks = product_data.get("maintenance_tasks", [])
                maintenance_level = product_data.get("maintenance_level")
                if not maintenance_level and maintenance_tasks:
                    # Derive from number of maintenance tasks
                    num_tasks = len(maintenance_tasks) if isinstance(maintenance_tasks, list) else 1
                    if num_tasks <= 1:
                        maintenance_level = "Low"
                    elif num_tasks <= 3:
                        maintenance_level = "Medium"
                    else:
                        maintenance_level = "High"
                else:
                    maintenance_level = maintenance_level or "Medium"

                # Create Product object
                product = Product(
                    name=product_data.get("name", "Unknown Product"),
                    brand=product_data.get("brand", "Unknown Brand"),
                    tier=TierLevel(product_data.get("tier", "better")),
                    category=product_data.get("category", "kitchen product"),
                    value_metrics=value_metrics,
                    quality_data=quality_data,
                    practical_metrics=practical_metrics,
                    characteristics=characteristics,
                    key_features=key_features,
                    materials=materials,
                    why_its_a_gem=product_data.get("why_its_a_gem", ""),
                    key_differentiator=product_data.get("key_differentiator"),
                    image_url=product_data.get("image_url"),
                    web_sources=web_sources,
                    reddit_mentions=product_data.get("reddit_mentions"),
                    professional_reviews=product_data.get("professional_reviews", []),
                    maintenance_level=maintenance_level,
                    purchase_links=product_data.get("purchase_links", []),
                    environmental_warnings=product_data.get("environmental_warnings"),
                    best_for=product_data.get("best_for", ""),
                    drawbacks=drawbacks
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


# ============================================================================
# CATCH-ALL ROUTE FOR STATIC EXPORT (must be last!)
# ============================================================================
@app.get("/{full_path:path}")
async def catch_all(request: Request, full_path: str):
    """
    Catch-all route for Next.js static export.
    Tries to serve the specific HTML file for the route, falls back to index.html.
    This enables both pre-rendered pages and client-side routing.
    """
    # Don't catch API routes, WebSocket, or health check
    if full_path.startswith(("api/", "ws/", "health", "_next/", "static-assets/")):
        raise HTTPException(status_code=404, detail="Not Found")

    # Try to serve the specific HTML file for this route
    # e.g., /login → login.html
    html_file = FRONTEND_BUILD_DIR / f"{full_path}.html"
    if html_file.exists() and html_file.is_file():
        return FileResponse(html_file)

    # Try directory index (e.g., /login/ → login/index.html)
    dir_index = FRONTEND_BUILD_DIR / full_path / "index.html"
    if dir_index.exists() and dir_index.is_file():
        return FileResponse(dir_index)

    # Fall back to root index.html for client-side routing
    index_path = FRONTEND_BUILD_DIR / "index.html"
    if index_path.exists():
        return FileResponse(index_path)
    else:
        raise HTTPException(status_code=404, detail="Frontend not found")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
