"""
ADK-based product search using Google Agent Development Kit.
Uses SequentialAgent to orchestrate 3-phase research pipeline:
  1. Context Discovery → 2. Product Finding → 3. Synthesis
Each agent passes output to next via state management (output_key).
"""
import os
import json
import uuid
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv
from google.adk.agents import Agent, SequentialAgent
from google.adk.tools import FunctionTool
from google.adk import Runner
from google.adk.sessions import InMemorySessionService
from google import genai
from google.genai import types
from google_search_service import get_google_search_service

# Load environment variables
load_dotenv()

# Initialize Google Search service
_search_service = get_google_search_service()


# Global variable to track search result counts (thread-safe for async)
_search_result_counts = []

async def google_search(query: str, num_results: int = 6) -> str:
    """
    Search Google for information using Custom Search API or fallback.

    OPTIMIZED FOR PARALLEL EXECUTION: When you need multiple searches, call this
    function multiple times in parallel rather than sequentially. Each search is
    independent and benefits from concurrent execution.

    Args:
        query: The search query string (single, specific query)
        num_results: Number of results to return (default 6, max 10)

    Returns:
        JSON string with search results including titles, links, and snippets
    """
    global _search_result_counts

    import time
    start_time = time.time()

    # Log search start with truncated query
    query_short = query[:50] + "..." if len(query) > 50 else query
    print(f"🔍 [{time.strftime('%H:%M:%S')}] Search START: {query_short}")

    try:
        results = await _search_service.async_search(query, num_results=min(num_results, 10))

        elapsed = time.time() - start_time
        result_count = len(results)
        _search_result_counts.append(result_count)  # Track globally
        print(f"✅ [{time.strftime('%H:%M:%S')}] Search DONE ({elapsed:.2f}s, {result_count} results): {query_short}")

        # Format results as JSON string for the LLM
        return json.dumps({
            "query": query,
            "num_results": result_count,
            "results": results
        }, indent=2)
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"❌ [{time.strftime('%H:%M:%S')}] Search FAILED ({elapsed:.2f}s): {query_short}")
        return json.dumps({"error": f"Search failed: {str(e)}", "query": query, "num_results": 0})


# Wrap the search function as an ADK FunctionTool
google_search_tool = FunctionTool(func=google_search)


class ADKProductSearch:
    """
    Sequential agent-based product search using Google ADK.

    Architecture:
    - SequentialAgent pipeline orchestrates 3 specialized agents
    - Context Discovery Agent: Researches usage patterns (saves to 'context_research')
    - Product Finder Agent: Finds products (reads 'context_research', saves to 'product_findings')
    - Synthesis Agent: Creates Good/Better/Best tiers (reads both, outputs final JSON)
    """

    def __init__(self):
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment variables")

        # Initialize model for agents
        self.model = "gemini-2.5-flash"

        # Create specialized research agents
        self.context_agent = self._create_context_agent()
        self.product_finder_agent = self._create_product_finder_agent()
        self.synthesis_agent = self._create_synthesis_agent()

        # Create sequential pipeline (no coordinator needed!)
        self.pipeline = self._create_pipeline()

        # Initialize ADK runner with session service
        self.session_service = InMemorySessionService()
        self.runner = Runner(
            app_name="product_research",
            agent=self.pipeline,
            session_service=self.session_service
        )

        # Metrics tracking for search transparency
        self.search_queries_executed = []
        self.total_sources_analyzed = 0
        self.searches_by_phase = {
            "context_discovery": [],
            "product_finder": [],
            "synthesis": []
        }

    def _create_context_agent(self) -> Agent:
        """Agent that researches product context and usage patterns"""
        return Agent(
            name="context_discovery_agent",
            model=self.model,
            description="Researches how people actually use products and what matters in real-world usage",
            instruction="""You are a product research expert focused on understanding real-world usage.

Your task: Research how people actually use the product in daily life.

SEARCH STRATEGY: Execute 5-7 focused searches to build comprehensive understanding.
Make parallel searches for different aspects - the tool supports concurrent execution.

Search for these topics (make 5-7 separate searches):
1. Real user experiences on Reddit (e.g., "[product] reddit honest review")
2. Usage patterns and scenarios (e.g., "[product] best use cases daily cooking")
3. Durability and longevity (e.g., "[product] how long does it last lifespan")
4. Common problems and failures (e.g., "[product] common problems issues reddit")
5. Material science insights (e.g., "[product] material quality durability comparison")
6. Living situation constraints (e.g., "[product] kitchen space storage requirements")
7. Compatibility considerations (e.g., "[product] works with induction gas electric")

Focus on Reddit, expert forums, and user communities for authentic experiences.

Return ONLY a JSON summary with:
{
  "usage_patterns": ["pattern1", "pattern2"],
  "key_materials": ["material insights"],
  "critical_factors": ["what really matters"],
  "common_issues": ["what to avoid"]
}
""",
            tools=[google_search_tool],
            output_key="context_research"
        )

    def _create_product_finder_agent(self) -> Agent:
        """Agent that finds specific products and reads reviews"""
        return Agent(
            name="product_finder_agent",
            model=self.model,
            description="Finds specific products, reads reviews, and identifies top recommendations",
            instruction="""You are a product research expert focused on finding the best specific products.

Context from previous research: {context_research}

Your task: Find specific product recommendations (6-9 products) across all price ranges that align with the usage patterns.

SEARCH STRATEGY: Execute 8-12 targeted searches to discover quality products across all tiers.
Make parallel searches for different price tiers and product types.

Search for these aspects (make 8-12 separate searches):
1. Budget-tier products (e.g., "best budget [product] under $50 reddit")
2. Mid-tier quality products (e.g., "best [product] $50-150 wirecutter serious eats")
3. Premium buy-it-for-life (e.g., "best premium [product] buy for life reddit")
4. Professional recommendations (e.g., "[product] professional chef recommendation")
5. Reddit favorites (e.g., "best [product] reddit bifl recommendations")
6. Expert reviews (e.g., "[product] wirecutter america's test kitchen review")
7. Specific brands (e.g., "Lodge vs Field Company [product] comparison")
8. Pricing searches (e.g., "[specific product model] price amazon where to buy")
9. Durability reports (e.g., "[product] longevity how many years lifespan")
10. User reviews (e.g., "[product] long term review 5 years later")

For EACH search, extract products you find. Combine findings across all searches.

For each product found, extract ALL of these fields:
- name: Full product name
- brand: Brand name
- price: Numeric price in USD (e.g. 45.99). **CRITICAL: You MUST provide a price for every product**
- lifespan: Expected lifespan in years (e.g. 5, 10, or "10-15")
- materials: Array of materials (e.g. ["cast iron", "stainless steel"])
- key_features: Array of key features (e.g. ["dishwasher safe", "oven safe to 500°F"])
- characteristics: Array of searchable characteristics (e.g. ["Non-stick", "Heavy-duty", "Ergonomic handle"])
- why_its_a_gem: 2-3 sentences explaining why this product is recommended
- best_for: Specific use case (e.g. "Daily cooking for families of 4+")
- trade_offs: Array of cons or limitations (e.g. ["Heavy weight may tire some users"])
- web_sources: Array of source URLs where you found this info
- purchase_links: Array of {name, url} where to buy (e.g. Amazon, manufacturer site)
- professional_reviews: Array of review site names (e.g. ["Wirecutter", "Serious Eats"])

**IMPORTANT PRICING RULES**:
- Extract exact prices from your search results when available
- Make dedicated searches for pricing if needed (e.g., "[product name] price amazon")
- If exact price not found after searching, estimate based on product tier: Budget ($15-50), Mid ($50-150), Premium ($150-400)
- ALWAYS include a price estimate for every product - never leave price as null or unknown
- Include 6-9 products minimum across all tiers

Return ONLY a JSON with 6-9 products total:
{
  "products": [
    {
      "name": "Lodge 10.25 Inch Cast Iron Skillet",
      "brand": "Lodge",
      "price": 19.99,
      "lifespan": "30+",
      "materials": ["cast iron"],
      "key_features": ["Pre-seasoned", "Oven safe", "Induction compatible"],
      "characteristics": ["Heavy-duty", "Non-stick when seasoned", "Versatile"],
      "why_its_a_gem": "The Lodge Cast Iron Skillet is an industry standard...",
      "best_for": "Budget-conscious home cooks who want a durable workhorse",
      "trade_offs": ["Requires seasoning maintenance", "Heavy weight"],
      "web_sources": ["https://www.seriouseats.com/..."],
      "purchase_links": [{"name": "Amazon", "url": "https://amazon.com/..."}],
      "professional_reviews": ["Wirecutter", "Serious Eats"]
    }
  ]
}
""",
            tools=[google_search_tool],
            output_key="product_findings"
        )

    def _create_synthesis_agent(self) -> Agent:
        """Agent that synthesizes all research into final recommendations"""
        return Agent(
            name="synthesis_agent",
            model=self.model,
            description="Analyzes all research and creates tiered product recommendations",
            instruction="""You are a product analysis expert who synthesizes research into actionable recommendations.

Context Research: {context_research}
Product Findings: {product_findings}

Your task: Analyze products and organize them into Good/Better/Best tiers based on QUALITY and DURABILITY, not price.

IMPORTANT: Preserve ALL fields from product_findings for each product. Do not drop any fields.

TIER DISTRIBUTION - QUALITY-BASED (NOT PRICE-BASED):
Organize products based on ALL 4 quality factors weighted equally. Evaluate each product across these dimensions:

**GOOD TIER (Solid Basics)**: 4-6 products
Products that meet MOST of these criteria:
- **Longevity**: 3-7 years typical lifespan
- **Failure Rate**: 60-75% still working after 5 years (moderate reliability)
- **Repairability**: Limited repair options, some maintenance required
- **Materials**: Standard materials (basic cast iron, aluminum, standard stainless steel)
- Example: Budget Lodge skillet ($30) - basic cast iron, will last but needs care

**BETTER TIER (Long-Lasting Quality)**: 4-6 products
Products that meet MOST of these criteria:
- **Longevity**: 7-15 years typical lifespan
- **Failure Rate**: 75-85% still working after 5 years (reliable)
- **Repairability**: Professional repair available, moderate maintenance
- **Materials**: High-quality materials (premium stainless steel, hard-anodized aluminum)
- Example: Mid-range products with solid construction and good track record

**BEST TIER (Lifetime Investment)**: 4-6 products
Products that meet MOST of these criteria:
- **Longevity**: 15+ years or lifetime (heirloom quality)
- **Failure Rate**: 85%+ still working after 5 years (rock solid reliability)
- **Repairability**: User-serviceable, easy to repair, parts available
- **Materials**: Premium materials (cast iron, forged steel, professional-grade stainless)
- Example: Field Company skillet ($145) - premium cast iron that lasts generations

CRITICAL RULES:
1. A product doesn't need to excel in ALL 4 factors - meeting MOST criteria for a tier qualifies it
2. A $30 product with 25-year lifespan + premium materials + easy repair = BEST tier
3. A $300 product with 3-year lifespan + poor materials + no repair = GOOD tier
4. Price is NOT a factor - only the 4 quality dimensions matter
5. Weight all 4 factors equally when making tier decisions

Include ALL worthy products from product_findings. Don't artificially limit to fewer products if you found more good options.

CRITICAL: Output ONLY this JSON structure (no markdown, no explanations):

{
  "good_tier": [
    {
      "name": "Full Product Name",
      "brand": "Brand Name",
      "price": 45.99,
      "lifespan": "10-15",
      "materials": ["material1"],
      "key_features": ["feature1", "feature2"],
      "characteristics": ["char1", "char2"],
      "why_its_a_gem": "Why this product is recommended...",
      "best_for": "Specific use case",
      "trade_offs": ["con1", "con2"],
      "web_sources": ["https://url1.com"],
      "purchase_links": [{"name": "Amazon", "url": "https://..."}],
      "professional_reviews": ["Wirecutter"]
    }
  ],
  "better_tier": [4-7 products with ALL fields],
  "best_tier": [4-7 products with ALL fields],
  "key_insights": ["Based on context research, users should prioritize..."],
  "what_to_avoid": ["Common issue to avoid..."]
}

For each product, copy ALL fields from product_findings. Add to the appropriate tier based on QUALITY/LIFESPAN as specified in the tier distribution rules above (NOT based on price).
Output ONLY the JSON - no markdown blocks, no explanations.
""",
            tools=[]  # Synthesis agent doesn't need to search
        )

    def _create_pipeline(self) -> SequentialAgent:
        """Create sequential pipeline for product research"""
        return SequentialAgent(
            name="product_research_pipeline",
            description="Sequential pipeline: Context Discovery → Product Finding → Synthesis",
            sub_agents=[
                self.context_agent,
                self.product_finder_agent,
                self.synthesis_agent
            ]
        )

    async def search(
        self,
        query: str,
        max_price: Optional[float] = None,
        user_context: Optional[Dict[str, Any]] = None,
        characteristics: Optional[Dict[str, Any]] = None,
        progress_callback: Optional[callable] = None
    ) -> Dict[str, Any]:
        """
        Execute ADK-based product search

        Args:
            query: Product search query (e.g., "cast iron skillet")
            max_price: Maximum price filter
            user_context: User context information
            characteristics: User characteristic preferences
            progress_callback: Optional async function to call with progress updates

        Returns:
            Structured search results with Good/Better/Best recommendations
        """
        # Declare global variable at the top of the function
        global _search_result_counts

        # Build context string
        context_parts = [f"Find the best {query}"]

        if max_price:
            context_parts.append(f"with budget up to ${max_price}")

        if characteristics:
            context_parts.append("\nUser preferences:")
            for key, value in characteristics.items():
                readable_key = key.replace('_', ' ').title()
                if isinstance(value, list):
                    context_parts.append(f"  - {readable_key}: {', '.join(str(v) for v in value)}")
                else:
                    context_parts.append(f"  - {readable_key}: {value}")

        if user_context:
            context_parts.append(f"\nAdditional context: {json.dumps(user_context)}")

        search_request = "\n".join(context_parts)

        print(f"\n🤖 Starting ADK agent-based search for: {query}")
        print(f"📋 Request: {search_request}\n")

        # Reset metrics for this search
        _search_result_counts = []  # Reset global counter
        self.search_queries_executed = []
        self.total_sources_analyzed = 0
        self.searches_by_phase = {
            "context_discovery": [],
            "product_finder": [],
            "synthesis": []
        }

        # Execute the agent workflow
        import time
        workflow_start = time.time()

        try:
            # runner.run_async returns an async generator that yields events
            # Create properly formatted Content object for the message
            message_content = types.Content(
                role="user",
                parts=[types.Part(text=search_request)]
            )

            # Create a new session for this search request
            user_id = "default_user"
            session_id = str(uuid.uuid4())

            # Create the session using the session service
            await self.session_service.create_session(
                app_name="product_research",
                user_id=user_id,
                session_id=session_id
            )

            final_response_text = ""
            event_count = 0
            current_agent = None
            last_agent_notified = None  # Track last agent we sent progress for

            async for event in self.runner.run_async(
                user_id=user_id,
                session_id=session_id,
                new_message=message_content
            ):
                event_count += 1

                # Track which agent is currently running and emit progress
                if event.author in ["context_discovery_agent", "product_finder_agent", "synthesis_agent"]:
                    if current_agent != event.author:
                        current_agent = event.author

                        # Emit progress update when agent changes
                        if progress_callback and last_agent_notified != current_agent:
                            last_agent_notified = current_agent
                            agent_messages = {
                                "context_discovery_agent": "Researching usage patterns and durability...",
                                "product_finder_agent": "Finding specific products...",
                                "synthesis_agent": "Analyzing and organizing products..."
                            }
                            await progress_callback(
                                "agent_progress",
                                agent_messages.get(current_agent, "Processing..."),
                                {"agent": current_agent.replace("_agent", ""), "phase": current_agent}
                            )

                # Track function calls for search transparency
                if event.content and event.content.parts:
                    for part in event.content.parts:
                        # Track google_search function calls
                        if hasattr(part, 'function_call') and part.function_call:
                            func_call = part.function_call
                            if func_call.name == "google_search":
                                # Extract query from function call args
                                query_text = None
                                if hasattr(func_call, 'args') and func_call.args:
                                    if isinstance(func_call.args, dict):
                                        query_text = func_call.args.get('query', 'Unknown query')
                                    elif hasattr(func_call.args, 'get'):
                                        query_text = func_call.args.get('query', 'Unknown query')

                                if query_text:
                                    self.search_queries_executed.append(query_text)

                                    # Track by phase
                                    if current_agent == "context_discovery_agent":
                                        self.searches_by_phase["context_discovery"].append(query_text)
                                    elif current_agent == "product_finder_agent":
                                        self.searches_by_phase["product_finder"].append(query_text)

                                    print(f"📞 [{time.strftime('%H:%M:%S')}] google_search by {event.author}: {query_text[:60]}...")

                                    # Emit progress for search query
                                    if progress_callback:
                                        await progress_callback(
                                            "search_query",
                                            f"Searching: {query_text[:80]}...",
                                            {
                                                "query": query_text,
                                                "agent": current_agent.replace("_agent", "") if current_agent else "unknown",
                                                "total_searches": len(self.search_queries_executed)
                                            }
                                        )

                # Capture final response from synthesis_agent (last agent in pipeline)
                # SequentialAgent passes through final responses from its last sub-agent
                if event.author == "synthesis_agent" and event.is_final_response():
                    if event.content and event.content.parts:
                        for part in event.content.parts:
                            if hasattr(part, 'text') and part.text:
                                final_response_text = part.text

            # Get total sources from global counter
            workflow_elapsed = time.time() - workflow_start
            self.total_sources_analyzed = sum(_search_result_counts)

            print(f"\n⏱️  Total workflow time: {workflow_elapsed:.2f}s ({event_count} events)")
            print(f"🔍 Search Metrics:")
            print(f"   - Total searches executed: {len(self.search_queries_executed)}")
            print(f"   - Total sources analyzed: {self.total_sources_analyzed}")
            print(f"   - Context discovery searches: {len(self.searches_by_phase['context_discovery'])}")
            print(f"   - Product finder searches: {len(self.searches_by_phase['product_finder'])}")

            result_text = final_response_text

            print(f"\n✅ ADK search completed")
            print(f"📊 Response length: {len(result_text)} characters\n")

            # Try to parse as JSON
            try:
                if "```json" in result_text:
                    result_text = result_text.split("```json")[1].split("```")[0]
                elif "```" in result_text:
                    result_text = result_text.split("```")[1].split("```")[0]

                result = json.loads(result_text.strip())
            except json.JSONDecodeError:
                # If not JSON, wrap in structure
                result = {
                    "good_tier": [],
                    "better_tier": [],
                    "best_tier": [],
                    "key_insights": [result_text],
                    "raw_response": result_text
                }

            # Add aggregated characteristics
            result["aggregated_characteristics"] = self._aggregate_characteristics(result)

            # Add search transparency metrics
            result["real_search_metrics"] = {
                "total_sources_analyzed": self.total_sources_analyzed,
                "search_queries_executed": len(self.search_queries_executed),
                "search_queries": self.search_queries_executed,
                "unique_sources": self.total_sources_analyzed,  # Already unique from search API
                "queries_generated": len(self.search_queries_executed),
                "sources_by_phase": {
                    "context_discovery": {
                        "queries": self.searches_by_phase["context_discovery"],
                        "count": len(self.searches_by_phase["context_discovery"])
                    },
                    "product_finder": {
                        "queries": self.searches_by_phase["product_finder"],
                        "count": len(self.searches_by_phase["product_finder"])
                    },
                    "synthesis": {
                        "queries": self.searches_by_phase["synthesis"],
                        "count": len(self.searches_by_phase["synthesis"])
                    }
                }
            }

            return result

        except Exception as e:
            print(f"❌ ADK search error: {e}")
            import traceback
            traceback.print_exc()

            return {
                "good_tier": [],
                "better_tier": [],
                "best_tier": [],
                "error": str(e),
                "aggregated_characteristics": []
            }

    def _aggregate_characteristics(self, result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Aggregate characteristics from all products"""
        characteristic_counts = {}
        characteristic_products = {}

        all_products = (
            result.get("good_tier", []) +
            result.get("better_tier", []) +
            result.get("best_tier", [])
        )

        for product in all_products:
            product_name = product.get("name", "Unknown")
            characteristics = product.get("characteristics", [])

            if isinstance(characteristics, str):
                characteristics = [characteristics]

            for char in characteristics:
                char = char.strip()
                if not char:
                    continue

                if char not in characteristic_counts:
                    characteristic_counts[char] = 0
                    characteristic_products[char] = []

                characteristic_counts[char] += 1
                characteristic_products[char].append(product_name)

        # Build aggregated array
        aggregated = []
        for char, count in sorted(characteristic_counts.items(), key=lambda x: x[1], reverse=True):
            aggregated.append({
                "label": char,
                "count": count,
                "product_names": characteristic_products[char]
            })

        return aggregated


# Factory function for compatibility
async def get_adk_search(
    query: str,
    max_price: Optional[float] = None,
    location: str = "United States",  # Kept for API compatibility, unused in ADK
    user_context: Optional[Dict[str, Any]] = None,
    characteristics: Optional[Dict[str, Any]] = None,
    progress_callback: Optional[callable] = None
) -> Dict[str, Any]:
    """
    Factory function to create and execute ADK search

    Args:
        query: Product search query
        max_price: Maximum price filter
        location: User location (kept for API compatibility)
        user_context: User context information
        characteristics: User characteristic preferences
        progress_callback: Optional async function to call with progress updates

    Returns:
        Structured search results
    """
    _ = location  # Unused, kept for API compatibility
    searcher = ADKProductSearch()
    return await searcher.search(
        query=query,
        max_price=max_price,
        user_context=user_context,
        characteristics=characteristics,
        progress_callback=progress_callback
    )
