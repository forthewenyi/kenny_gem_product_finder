"""
Simplified search implementation using OpenAI + Tavily directly
"""
import os
from typing import Dict, Any
from openai import OpenAI
from tavily import TavilyClient


class SimpleKennySearch:
    """Simplified search without LangChain agent complexity"""

    def __init__(self):
        self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

    async def search_products(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Search for kitchen products

        Args:
            query: User's search query
            context: User context

        Returns:
            Dictionary with product results
        """
        # Step 1: Use Tavily to search the web
        search_query = f"{query} kitchen product recommendations reddit buy it for life"
        tavily_results = self.tavily_client.search(
            query=search_query,
            search_depth="advanced",
            max_results=10,
            include_domains=[
                "reddit.com",
                "seriouseats.com",
                "americastestkitchen.com"
            ]
        )

        # Step 2: Format search results for OpenAI
        search_context = self._format_search_results(tavily_results)

        # Step 3: Use OpenAI to analyze and organize into tiers
        system_prompt = """You are Kenny, an expert at finding high-quality kitchen products.

Analyze the web search results and organize products into three tiers:
- GOOD: $20-80, 2-5 years (students, renters)
- BETTER: $80-200, 8-15 years (homeowners)
- BEST: $200-600+, 15-30+ years (lifetime investment)

For each product, calculate cost-per-year = price / lifespan.

Return a JSON response with this structure (no markdown, just raw JSON):
{
  "good_tier": [],
  "better_tier": [],
  "best_tier": [],
  "sources": [],
  "educational_insights": [],
  "search_queries_used": []
}"""

        user_prompt = f"""User query: {query}
Context: {context}

Web search results:
{search_context}

Please organize these findings into Good/Better/Best tiers. For each product include:
- name, brand, category
- price, lifespan (estimate from reviews)
- key_features (list)
- why_its_a_gem (explanation)
- web_sources (URLs from search results)
- maintenance_level
- best_for (life stage)
- trade_offs (honest drawbacks)

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
            return result
        except json.JSONDecodeError:
            # Return raw output if JSON parsing fails
            return {
                "good_tier": [],
                "better_tier": [],
                "best_tier": [],
                "sources": tavily_results.get("results", []),
                "educational_insights": ["AI returned results in unexpected format"],
                "search_queries_used": [search_query],
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
