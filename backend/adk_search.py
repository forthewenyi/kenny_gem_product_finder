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
            instruction="""Research how people use the product in daily life.

IMPORTANT - PARALLEL TOOL CALLS:
When you need multiple pieces of information, ALWAYS call search functions in parallel.
Call all 3 search functions simultaneously in a single turn - do NOT wait for results between searches.

Make EXACTLY 3 searches IN PARALLEL:
1. "[product] reddit honest review"
2. "[product] durability common problems"
3. "[product] material quality"

Examples of parallel calls:
- Need reddit reviews AND durability data → Call both google_search functions simultaneously
- Need 3 different topics → Call google_search 3 times in parallel

After all searches complete, return ONLY this JSON:
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
            instruction="""Find 6-9 products with pricing.

Context: {context_research}

IMPORTANT - PARALLEL TOOL CALLS:
When you need multiple pieces of information, ALWAYS call search functions in parallel.
Call all 8 search functions simultaneously in a single turn - do NOT wait for results between searches.

Make EXACTLY 8 searches IN PARALLEL:
1. "best budget [product] under $50 amazon"
2. "best [product] $50-150 wirecutter"
3. "best premium [product] reddit"
4. "[product] professional recommendation amazon"
5. "[product] wirecutter winner"
6. "[product] america's test kitchen"
7. "best [product] reddit bifl"
8. "[product] comparison review"

Examples of parallel calls:
- Need budget AND premium products → Call both google_search functions simultaneously
- Need reviews from 8 sources → Call google_search 8 times in parallel
- Always prefer multiple specific function calls over sequential searches

After all searches complete, extract products and return JSON. If prices are missing, estimate: Budget=$15-50, Mid=$50-150, Premium=$150-400.

Extract these 15 fields for each product:
- name, brand, category (e.g., "cast iron skillet", "chef's knife", "dutch oven"), materials (array), key_features (array), key_differentiator (string), why_its_a_gem (string)
- maintenance_tasks (array), learning_curve (string), drawbacks (array)
- professional_reviews (array), best_for (string)
- price (number), lifespan (string like "15-25 years" or "5-10 years"), purchase_links (array of {name, url})

Return JSON with 6-9 products:
{
  "products": [
    {
      "name": "Lodge 10.25 Inch Cast Iron Skillet",
      "brand": "Lodge",
      "category": "cast iron skillet",
      "materials": ["cast iron"],
      "key_features": ["Pre-seasoned", "Oven safe to 500°F", "Induction compatible", "Helper handle", "10.25-inch diameter"],
      "key_differentiator": "Best value in entry-level cast iron - pre-seasoned and ready to use at the lowest price point",
      "why_its_a_gem": "The Lodge Cast Iron Skillet is an industry standard that delivers professional-level heat retention and versatility at an unbeatable price. It's been the go-to choice for home cooks and professional chefs for over 100 years.",
      "maintenance_tasks": ["Season after each use", "Hand wash only", "Dry immediately to prevent rust"],
      "learning_curve": "Moderate - requires understanding proper heat control and seasoning maintenance, but becomes intuitive after a few uses",
      "drawbacks": ["Heavy weight (5+ lbs)", "Requires regular seasoning", "Not dishwasher safe"],
      "professional_reviews": ["Wirecutter Budget Pick", "Serious Eats Top Choice"],
      "best_for": "Budget-conscious home cooks who want a durable workhorse for daily cooking",
      "price": 19.99,
      "lifespan": "30+ years",
      "purchase_links": [{"name": "Amazon", "url": "https://amazon.com/..."}]
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
            description="Analyzes all research and creates tiered product recommendations based on Value vs Price",
            instruction="""Organize products into Good/Better/Best tiers by VALUE vs PRICE ratio.

Context: {context_research}
Products: {product_findings}

Tier by VALUE/PRICE ratio:
- GOOD: Solid value at entry price
- BETTER: Step-up worth the investment
- BEST: Exceptional VALUE/PRICE (premium worth it OR budget punching above weight)

For each product, copy ALL 15 fields from product_findings AND add "tier" field. Output ONLY JSON:

{
  "good_tier": [
    {
      "tier": "good",
      "name": "Full Product Name",
      "brand": "Brand Name",
      "category": "cast iron skillet",
      "materials": ["cast iron"],
      "key_features": ["Pre-seasoned", "Oven safe", "Helper handle"],
      "key_differentiator": "What makes this special",
      "why_its_a_gem": "Value proposition...",
      "maintenance_tasks": ["Season after use", "Hand wash"],
      "learning_curve": "Moderate - requires seasoning knowledge",
      "drawbacks": ["Heavy", "Needs maintenance"],
      "professional_reviews": ["Wirecutter Pick"],
      "best_for": "Budget home cooks",
      "price": 19.99,
      "lifespan": "30+ years",
      "purchase_links": [{"name": "Amazon", "url": "https://..."}]
    }
  ],
  "better_tier": [products with ALL 15 fields + tier="better"],
  "best_tier": [products with ALL 15 fields + tier="best"],
  "key_insights": ["Based on context research, users should prioritize..."],
  "what_to_avoid": ["Common issue to avoid..."]
}

For each product:
1. Copy ALL 15 fields from product_findings exactly as they appear
2. Add "tier" field matching the tier they're assigned to ("good", "better", or "best")
3. Place in appropriate tier array based on VALUE vs PRICE ratio

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

            # Normalize products: copy key_features to characteristics for filtering
            for tier in ["good_tier", "better_tier", "best_tier"]:
                for product in result.get(tier, []):
                    if "characteristics" not in product and "key_features" in product:
                        product["characteristics"] = product["key_features"]

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
