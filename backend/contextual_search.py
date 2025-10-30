"""
Context-aware search implementation using AI-driven query generation.
Based on Just-In-Time framework with attribute dependency reasoning.
Now powered by Google Gemini instead of OpenAI.
"""
import os
import asyncio
import time
import json
from typing import Dict, Any, List, Optional
import google.generativeai as genai
import httpx
from google_search_service import get_google_search_service


class ContextualKennySearch:
    """
    Multi-phase search using AI-driven query generation with Google Gemini.

    Phases:
    1. Context Discovery - Understand user's actual needs
    2. Material Science - Determine optimal materials
    3. Product Identification - Find correctly-built products
    4. Frustration Research - Discover real pain points
    5. Value Synthesis - Build context-aware recommendations
    """

    def __init__(self):
        # Configure Google Gemini
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment variables")

        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash')

        # Initialize Google Search service (with fallback support)
        self.search_service = get_google_search_service()

    async def _generate_contextual_queries(
        self,
        product_query: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, List[str]]:
        """
        Use AI to generate strategic search queries based on context.

        Instead of hardcoded templates, we reason about what information
        we need and generate targeted queries.
        """

        context_str = ""
        if user_context:
            context_str = f"\nUser context: {user_context}"

        prompt = f"""You are a product research expert. Generate strategic search queries to help find the best {product_query}.

{context_str}

Use the 5-phase research framework:

1. CONTEXT DISCOVERY PHASE
Generate 2-3 queries to understand how people actually use this product:
- Living situation constraints (kitchen setup, space, etc.)
- Usage patterns (daily vs occasional, cooking style)
- Existing tools and compatibility

2. MATERIAL SCIENCE PHASE
Generate 2-3 queries to determine optimal materials:
- What materials work best for different use cases
- Material compatibility with cooking methods
- Durability characteristics of different materials

3. PRODUCT IDENTIFICATION PHASE
Generate 2-3 queries to find correctly-built products:
- Products built with optimal materials
- Professional recommendations based on use case
- Buy-it-for-life quality products

4. FRUSTRATION RESEARCH PHASE
Generate 2-3 queries to discover real pain points:
- Common problems and failures
- Marketing gimmicks vs real features
- What features are unnecessary

5. VALUE SYNTHESIS PHASE
Generate 1-2 queries for long-term value:
- Long-term ownership experiences
- Repair and maintenance reality
- True cost of ownership

Focus on Reddit, expert review sites, and user experiences.

Return ONLY a JSON object with this structure:
{{
  "context_discovery": ["query1", "query2", ...],
  "material_science": ["query1", "query2", ...],
  "product_identification": ["query1", "query2", ...],
  "frustration_research": ["query1", "query2", ...],
  "value_synthesis": ["query1", "query2"]
}}

Make queries specific and actionable. Include "reddit" where appropriate for real user experiences."""

        # Generate queries using Gemini
        response = self.model.generate_content(prompt)
        response_text = response.text

        # Clean markdown if present
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0]
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0]

        queries = json.loads(response_text.strip())

        # Flatten and limit to 10 total queries for cost/speed balance
        all_queries = []
        for phase, phase_queries in queries.items():
            all_queries.extend(phase_queries)

        # Return limited set (2 from each phase)
        limited_queries = {
            "context_discovery": queries.get("context_discovery", [])[:2],
            "material_science": queries.get("material_science", [])[:2],
            "product_identification": queries.get("product_identification", [])[:2],
            "frustration_research": queries.get("frustration_research", [])[:2],
            "value_synthesis": queries.get("value_synthesis", [])[:2]
        }

        return limited_queries

    async def _fetch_page_content(self, url: str) -> Optional[str]:
        """Fetch page content from URL"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url, follow_redirects=True)
                if response.status_code == 200:
                    # Extract text content (simplified - in production use BeautifulSoup)
                    text = response.text[:1000]  # First 1000 chars
                    return text
                return None
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            return None

    async def _execute_queries_by_phase(
        self,
        queries_by_phase: Dict[str, List[str]]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Execute queries organized by research phase using Google Search.
        Run phases in parallel for speed.
        """

        async def run_single_search(query: str, phase: str, query_num: int):
            """Execute a single Google search"""
            query_start = time.time()
            try:
                print(f"  [{phase}] Query {query_num}: {query[:60]}...")

                # Run Google search in thread pool (it's synchronous)
                loop = asyncio.get_event_loop()

                def do_search():
                    """Wrapper for Google search with error handling"""
                    try:
                        # Use the new Google Search service
                        # This automatically uses Custom Search API if configured,
                        # otherwise falls back to googlesearch-python
                        return self.search_service.search(query, num_results=6)
                    except Exception as e:
                        print(f"     ⚠️  Google search error: {e}")
                        return []

                search_results = await asyncio.wait_for(
                    loop.run_in_executor(None, do_search),
                    timeout=30.0  # Increased timeout to 30 seconds
                )

                # Format results to match expected structure
                # search_results already contains dicts with url, title, snippet
                results = []
                for result in search_results:
                    results.append({
                        "url": result.get("url", ""),
                        "title": result.get("title", ""),
                        "content": result.get("snippet", ""),
                        "display_link": result.get("display_link", "")
                    })

                query_elapsed = time.time() - query_start

                if len(results) > 0:
                    print(f"     ✓ [{phase}] Query {query_num} completed in {query_elapsed:.1f}s ({len(results)} results)")
                else:
                    print(f"     ⚠️  [{phase}] Query {query_num} completed but found 0 results (possible rate limiting)")

                return {
                    "phase": phase,
                    "query": query,
                    "results": results,
                    "success": len(results) > 0
                }

            except asyncio.TimeoutError:
                print(f"     ⏱️  [{phase}] Query {query_num} timed out after 30s")
                return {"phase": phase, "query": query, "results": [], "success": False}
            except Exception as e:
                print(f"     ⚠️  [{phase}] Query {query_num} failed: {e}")
                import traceback
                traceback.print_exc()
                return {"phase": phase, "query": query, "results": [], "success": False}

        # Create all search tasks
        all_tasks = []
        for phase, queries in queries_by_phase.items():
            for i, query in enumerate(queries, 1):
                all_tasks.append(run_single_search(query, phase, i))

        print(f"\n🔍 Executing {len(all_tasks)} contextual research queries...")
        print("⚡ Running all phases in parallel for maximum speed!\n")

        search_start = time.time()
        search_results = await asyncio.gather(*all_tasks, return_exceptions=True)
        search_elapsed = time.time() - search_start

        # Organize results by phase
        results_by_phase = {
            "context_discovery": [],
            "material_science": [],
            "product_identification": [],
            "frustration_research": [],
            "value_synthesis": []
        }

        for result in search_results:
            if isinstance(result, dict) and result.get("success"):
                phase = result["phase"]
                results_by_phase[phase].extend(result["results"])

        # Calculate totals
        total_results = sum(len(results) for results in results_by_phase.values())
        print(f"\n✓ Research complete! Collected {total_results} sources in {search_elapsed:.1f}s")
        print(f"  • Context Discovery: {len(results_by_phase['context_discovery'])} sources")
        print(f"  • Material Science: {len(results_by_phase['material_science'])} sources")
        print(f"  • Product Identification: {len(results_by_phase['product_identification'])} sources")
        print(f"  • Frustration Research: {len(results_by_phase['frustration_research'])} sources")
        print(f"  • Value Synthesis: {len(results_by_phase['value_synthesis'])} sources")

        return results_by_phase

    async def search_products(
        self,
        query: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Main search entry point using contextual AI-driven approach.
        """

        # Phase 1: Generate contextual queries using AI
        print(f"\n🤖 Generating contextual research queries for: {query}")
        queries_by_phase = await self._generate_contextual_queries(query, context)

        # Show generated queries
        print("\n📋 Generated Research Plan:")
        for phase, queries in queries_by_phase.items():
            print(f"  {phase.replace('_', ' ').title()}: {len(queries)} queries")

        # Phase 2: Execute queries organized by research phase
        results_by_phase = await self._execute_queries_by_phase(queries_by_phase)

        # Phase 3: Synthesize results using AI with context awareness
        print("\n🧠 Synthesizing context-aware recommendations...")

        synthesis_prompt = f"""You are Kenny, an expert at finding high-quality products through context-aware analysis.

USER QUERY: {query}
USER CONTEXT: {context}

RESEARCH DATA (organized by phase):

=== CONTEXT DISCOVERY ===
{self._format_phase_results(results_by_phase['context_discovery'])}

=== MATERIAL SCIENCE ===
{self._format_phase_results(results_by_phase['material_science'])}

=== PRODUCT IDENTIFICATION ===
{self._format_phase_results(results_by_phase['product_identification'])}

=== FRUSTRATION RESEARCH ===
{self._format_phase_results(results_by_phase['frustration_research'])}

=== VALUE SYNTHESIS ===
{self._format_phase_results(results_by_phase['value_synthesis'])}

Based on this multi-phase research, create recommendations following this framework:

1. CONTEXT ANALYSIS
Understand: How do people actually use this product? What constraints matter?

2. MATERIAL REASONING
Determine: What materials are optimal for the identified use cases?
Consider: attribute dependencies (cooking method + tools → material requirements)

3. PRODUCT SELECTION
Find: Products correctly built with optimal materials (not just "most popular")
Extract: minimum 9 products (3 per tier) with specific models and brands

4. FRUSTRATION AWARENESS
Identify: Real pain points from long-term users
Filter: Marketing gimmicks vs features that solve real problems

5. VALUE SYNTHESIS
Recommend: Best valuable products = longest-lasting for USER'S specific context

Return JSON with:
{{
  "context_insights": {{
    "use_case_summary": "How people actually use this",
    "key_constraints": ["constraint1", "constraint2"],
    "optimal_materials": ["material1", "material2"],
    "material_reasoning": "Why these materials for this use case"
  }},
  "good_tier": [3 products - $20-80, 2-5 years],
  "better_tier": [3 products - $80-200, 8-15 years],
  "best_tier": [3 products - $200-600+, 15-30+ years],
  "common_frustrations": [
    {{"issue": "...", "why_it_matters": "...", "how_to_avoid": "..."}}
  ],
  "unnecessary_features": ["feature1: why it's a gimmick"],
  "sources": [list of URLs used],
  "educational_insights": ["insight1", "insight2"]
}}

Each product must include:
- name, brand, category, price, lifespan
- materials (CRITICAL - based on material science phase)
- characteristics (5-8 normalized attributes)
- key_features, why_its_a_gem
- web_sources, maintenance_level, best_for, trade_offs
- practical_metrics (cleaning_time, setup_time, learning_curve, weight, etc.)
- context_fit (how well it matches the user's specific use case)

Return ONLY valid JSON."""

        # Generate synthesis using Gemini
        response = self.model.generate_content(synthesis_prompt)
        response_text = response.text

        # Parse JSON response
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0]
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0]

        result = json.loads(response_text.strip())

        # Calculate search metrics
        total_sources = sum(len(results) for results in results_by_phase.values())
        all_queries = []
        for phase, queries in queries_by_phase.items():
            for q in queries:
                all_queries.append({"phase": phase.replace('_', ' ').title(), "query": q})

        # Add metadata
        result["search_approach"] = "contextual_ai_driven_gemini"
        result["queries_generated"] = sum(len(q) for q in queries_by_phase.values())
        result["research_phases"] = list(queries_by_phase.keys())
        result["search_queries"] = all_queries  # Include actual queries
        result["total_sources_analyzed"] = total_sources  # How many sources were found
        result["sources_by_phase"] = {
            "context_discovery": len(results_by_phase['context_discovery']),
            "material_science": len(results_by_phase['material_science']),
            "product_identification": len(results_by_phase['product_identification']),
            "frustration_research": len(results_by_phase['frustration_research']),
            "value_synthesis": len(results_by_phase['value_synthesis'])
        }

        return result

    def _format_phase_results(self, results: List[Dict[str, Any]]) -> str:
        """Format search results for a specific research phase"""
        if not results:
            return "No data collected for this phase."

        formatted = []
        for i, result in enumerate(results[:5], 1):  # Limit to top 5 per phase
            formatted.append(f"""
Source {i}:
Title: {result.get('title', 'N/A')}
URL: {result.get('url', 'N/A')}
Content: {result.get('content', 'N/A')[:300]}...
""")
        return "\n".join(formatted)


# Global instance
_contextual_search_instance = None


def get_contextual_search() -> ContextualKennySearch:
    """Get or create the global contextual search instance"""
    global _contextual_search_instance
    if _contextual_search_instance is None:
        _contextual_search_instance = ContextualKennySearch()
    return _contextual_search_instance
