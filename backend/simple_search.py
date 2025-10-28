"""
Simplified search implementation using OpenAI + Tavily directly
"""
import os
from typing import Dict, Any, List
from openai import OpenAI
from tavily import TavilyClient


class SimpleKennySearch:
    """Simplified search without LangChain agent complexity"""

    def __init__(self):
        self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

    def _generate_durability_queries(self, base_query: str) -> List[str]:
        """
        Generate multiple search queries focused on durability and longevity.

        Args:
            base_query: The user's original search query (e.g., "chef's knife")

        Returns:
            List of search queries targeting different durability aspects
        """
        # Extract product name/category from query
        product_name = base_query.lower().strip()

        queries = [
            # General product search with durability focus
            f"{product_name} recommendations reddit buy it for life",

            # Longevity and lifespan queries
            f"{product_name} how long does it last",
            f"{product_name} still working after 5 years",
            f"{product_name} durability longevity reddit",

            # Comparison and value queries
            f"{product_name} vs cheap alternative longevity",
            f"best {product_name} that lasts lifetime",

            # Failure and problem queries
            f"{product_name} common problems failures",
            f"{product_name} broke after how long",
            f"why did my {product_name} break",

            # Repair and maintenance queries
            f"{product_name} easy to repair maintain",
            f"{product_name} replacement parts available",

            # User experience queries
            f"{product_name} owned for 10 years review",
            f"{product_name} worth the investment long term"
        ]

        return queries

    def _generate_alternative_solutions(self, query: str) -> List[str]:
        """
        Generate search queries to find non-purchase alternatives.

        Args:
            query: The user's product search query

        Returns:
            List of search queries for finding alternatives
        """
        product_name = query.lower().strip()

        queries = [
            # Find the actual problem they're trying to solve
            f"why do I need {product_name}",
            f"alternatives to buying {product_name}",

            # Find DIY/free solutions
            f"how to solve without {product_name}",
            f"DIY alternative to {product_name}",
            f"{product_name} unnecessary waste of money",

            # Find repair/maintenance alternatives
            f"fix instead of replacing {product_name}",
            f"restore old {product_name}",

            # Find cheaper household alternatives
            f"household items that work like {product_name}",
            f"what did people use before {product_name}"
        ]

        return queries

    async def search_products(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Search for kitchen products using multiple durability-focused queries

        Args:
            query: User's search query
            context: User context

        Returns:
            Dictionary with product results
        """
        # Step 1: Generate multiple durability-focused queries
        durability_queries = self._generate_durability_queries(query)

        # Step 2: Execute multiple searches (limit to top 4 to manage API costs)
        all_results = []
        queries_used = []

        print(f"🔍 Executing {min(4, len(durability_queries))} durability-focused searches...")

        for search_query in durability_queries[:4]:  # Limit to 4 searches
            try:
                print(f"  → {search_query}")
                tavily_results = self.tavily_client.search(
                    query=search_query,
                    search_depth="advanced",
                    max_results=5,  # Fewer results per query since we're doing multiple queries
                    include_domains=[
                        "reddit.com",
                        "seriouseats.com",
                        "americastestkitchen.com",
                        "cooksillustrated.com"
                    ]
                )

                # Collect results
                if tavily_results.get("results"):
                    all_results.extend(tavily_results.get("results", []))
                    queries_used.append(search_query)

            except Exception as e:
                print(f"  ⚠️  Search failed for '{search_query}': {e}")
                continue

        print(f"✓ Collected {len(all_results)} total search results from {len(queries_used)} queries")

        # Step 3: Remove duplicate URLs
        seen_urls = set()
        unique_results = []
        for result in all_results:
            url = result.get('url', '')
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique_results.append(result)

        print(f"✓ Deduplicated to {len(unique_results)} unique results")

        # Step 4: Format search results for OpenAI
        search_context = self._format_search_results({"results": unique_results})

        # Step 5: Use OpenAI to analyze and organize into tiers with durability focus
        system_prompt = """You are Kenny, an expert at finding high-quality kitchen products with a focus on durability and longevity.

PHILOSOPHY: You want to help people solve problems, not just buy solutions. Always consider non-purchase alternatives first.

## Step 1: BEFORE YOU BUY - Identify alternatives

Analyze if the user's query has non-purchase alternatives:
- Is this solving a problem that doesn't require a purchase?
- Are there DIY/household alternatives?
- Can they fix/restore what they already have?

If alternatives exist, create a "before_you_buy" section with 1-3 alternative solutions showing:
- What problem they're trying to solve
- What people typically buy (and its cost/issues)
- Your alternative solution (and its cost/benefits)
- How-to instructions
- When buying actually makes sense

Examples:
- Problem: Fabric softener → Alternative: White vinegar (pennies vs $8, works better)
- Problem: Non-stick spray → Alternative: Re-season cast iron properly (free vs $5-20)
- Problem: New knife set → Alternative: Sharpen existing knives ($15 whetstone vs $200)

## Step 2: PRODUCT RECOMMENDATIONS

Analyze the web search results and organize products into three tiers:
- GOOD: $20-80, 2-5 years (students, renters)
- BETTER: $80-200, 8-15 years (homeowners)
- BEST: $200-600+, 15-30+ years (lifetime investment)

For each product, calculate cost-per-year = price / lifespan.

CRITICAL - DURABILITY DATA EXTRACTION:
Pay special attention to durability information in the search results:
- Extract phrases about longevity: "still using after X years", "lasted X years", "owned for X years"
- Note failure reports: "broke after X months/years", "stopped working", "failed"
- Identify common failure points: "handle broke", "rust", "motor died", "coating peeled"
- Find repair mentions: "easy to fix", "replaced the gasket", "can't repair"
- Count reports of long-term ownership (5+ years)
- Include specific durability info in product descriptions

Return a JSON response with this structure (no markdown, just raw JSON):
{
  "before_you_buy": {
    "title": "Before You Buy...",
    "subtitle": "Let's solve the problem first",
    "alternatives": [
      {
        "problem": "...",
        "consumer_solution": "...",
        "consumer_cost": 0.0,
        "consumer_issues": ["...", "..."],
        "your_solution": "...",
        "your_cost": 0.0,
        "why_better": "...",
        "how_to": "...",
        "savings_per_year": 0.0,
        "when_to_buy_instead": "..."
      }
    ],
    "educational_insight": "Why we show alternatives first"
  },
  "good_tier": [],
  "better_tier": [],
  "best_tier": [],
  "sources": [],
  "educational_insights": [],
  "search_queries_used": []
}

NOTE: Only include "before_you_buy" if legitimate alternatives exist. For core tools (chef's knife, cast iron pan), skip alternatives and show products directly."""

        user_prompt = f"""User query: {query}
Context: {context}

Web search results (from {len(queries_used)} durability-focused searches):
{search_context}

Please organize these findings into Good/Better/Best tiers. For each product include:
- name, brand, category
- price, lifespan (estimate from reviews AND durability reports)
- key_features (list)
- why_its_a_gem (explanation with durability focus)
- web_sources (URLs from search results)
- maintenance_level
- best_for (life stage)
- trade_offs (honest drawbacks)
- durability_info (IMPORTANT: include any specific durability mentions like "still working after 10 years", "handle broke after 2 years", etc.)
- practical_metrics (IMPORTANT: Extract day-to-day usage info):
  {{
    "cleaning_time_minutes": <estimate from reviews, e.g., 5, 15, 30>,
    "cleaning_details": "Hand wash only, needs immediate drying" or "Dishwasher safe",
    "setup_time": "Ready" or "30 min" (for items needing prep),
    "setup_details": "Pre-seasoned" or "Needs initial seasoning",
    "learning_curve": "Low" | "Medium" | "High",
    "learning_details": "3-5 uses to master heat control",
    "maintenance_level": "Low" | "Medium" | "High",
    "maintenance_details": "Re-season 2-3x per year",
    "weight_lbs": 8.5,
    "weight_notes": "Heavy, use two hands",
    "dishwasher_safe": true | false,
    "oven_safe": true | false,
    "oven_max_temp": 500
  }}

Extract as much durability data as possible from user reports in the search results. Look for:
- Years of ownership reported by users
- Failure timeframes and common problems
- Repair experiences
- Long-term performance

Also extract practical usage details from reviews:
- How long it takes to clean
- Whether it needs prep/seasoning
- How heavy it is (look for weight in specs or "heavy" mentions)
- Dishwasher and oven safety

Return ONLY valid JSON, no markdown formatting."""

        response = self.openai_client.chat.completions.create(
            model="gpt-4o-mini",  # Using gpt-4o-mini (faster, cheaper, widely available)
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3,
            max_tokens=4000
        )

        # Parse response
        response_text = response.choices[0].message.content

        # Try to extract JSON from response
        import json
        try:
            # Remove markdown code blocks if present
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0]
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0]

            result = json.loads(response_text.strip())

            # Add the queries we actually used
            if "search_queries_used" not in result:
                result["search_queries_used"] = queries_used

            return result
        except json.JSONDecodeError:
            # Return raw output if JSON parsing fails
            return {
                "good_tier": [],
                "better_tier": [],
                "best_tier": [],
                "sources": unique_results,
                "educational_insights": ["AI returned results in unexpected format"],
                "search_queries_used": queries_used,
                "raw_output": response_text
            }

    def _format_search_results(self, tavily_results: Dict[str, Any]) -> str:
        """Format Tavily search results for OpenAI"""
        results = tavily_results.get("results", [])

        formatted = []
        for i, result in enumerate(results[:10], 1):
            formatted.append(f"""
Result {i}:
Title: {result.get('title', 'N/A')}
URL: {result.get('url', 'N/A')}
Content: {result.get('content', 'N/A')[:500]}
---
""")

        return "\n".join(formatted)


# Global instance
_simple_search_instance = None


def get_simple_search() -> SimpleKennySearch:
    """Get or create the global search instance"""
    global _simple_search_instance
    if _simple_search_instance is None:
        _simple_search_instance = SimpleKennySearch()
    return _simple_search_instance
