"""
AI Agent Service for Kenny Gem Finder
Uses LangChain with Tavily search to find and organize kitchen products
Includes Supabase caching to reduce API calls
"""
import os
import json
import re
from typing import Dict, Any, List, Optional, Tuple
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain_openai import ChatOpenAI
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.schema import AIMessage

from models import (
    TierResults,
    Product,
    TierLevel,
    ValueMetrics,
    WebSource,
    DurabilityData
)
from database_service import DatabaseService


class KennyAgent:
    """
    AI Agent for researching kitchen products and organizing them into tiers
    """

    def __init__(self):
        """Initialize the agent with LangChain, Tavily, and Supabase cache"""
        # Check for required API keys
        self.openai_key = os.getenv("OPENAI_API_KEY")
        self.tavily_key = os.getenv("TAVILY_API_KEY")

        if not self.openai_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        if not self.tavily_key:
            raise ValueError("TAVILY_API_KEY not found in environment variables")

        # Initialize database service for caching
        try:
            self.db = DatabaseService()
            print("✓ Database caching enabled")
        except Exception as e:
            print(f"⚠️  Database caching disabled: {e}")
            self.db = None

        # Initialize Tavily Search Tool
        self.tavily_tool = TavilySearchResults(
            max_results=10,
            search_depth="advanced",
            include_domains=[
                "reddit.com",
                "seriouseats.com",
                "americastestkitchen.com",
                "cooksillustrated.com",
                "goodhousekeeping.com",
            ],
            # Don't exclude domains - we want comprehensive results
        )

        # Define Agent Prompt
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", self._get_system_prompt()),
            ("user", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])

        # Create LLM
        self.llm = ChatOpenAI(
            model="gpt-4-turbo-preview",
            temperature=0.3,  # Slightly creative for variety, but mostly factual
            api_key=self.openai_key
        )

        # Create Agent
        self.agent = create_openai_functions_agent(
            self.llm,
            [self.tavily_tool],
            self.prompt
        )

        # Create Agent Executor
        self.agent_executor = AgentExecutor(
            agent=self.agent,
            tools=[self.tavily_tool],
            verbose=True,  # For debugging
            max_iterations=5,
            early_stopping_method="generate"
        )

    def _get_system_prompt(self) -> str:
        """Get the system prompt for the agent"""
        return """You are Kenny, an expert kitchen product researcher.

Your job: Research kitchen products on the web and organize them into Good/Better/Best tiers.

TIER SYSTEM:
- GOOD: $20-80, 2-5 years (students, renters)
- BETTER: $80-200, 8-15 years (homeowners, serious cooks)
- BEST: $200-600+, 15-30+ years (lifetime investment)

RESEARCH PROCESS:
1. Use Tavily to search Reddit, review sites, kitchen forums
2. Find "hidden gems" - niche brands, pro-grade options
3. Extract: brand, price, lifespan, features, reviews
4. Calculate: cost per year = price / lifespan
5. Organize into tiers

DURABILITY RESEARCH (CRITICAL):
For each product, extract durability information from user reports:
- Long-term ownership: Look for phrases like "still using after X years", "lasted X years", "had it for X years", "going strong for X years"
- Failure reports: Look for "broke after X months/years", "stopped working", "failed after", "died after"
- Common failure points: Extract specific failures like "handle broke", "rust after 2 years", "motor died", "coating peeled"
- Repair mentions: Look for "easy to fix", "replaced the gasket", "repaired it myself", "can't be fixed"
- Count how many users report 5+ years of ownership
- Note the data sources (Reddit threads, review sites, etc.)

IMPORTANT:
- Kitchen products ONLY
- Cite sources with URLs
- Be honest about trade-offs
- Find 2 GOOD, 3 BETTER, 3 BEST products (8 total max, less if products unavailable)
- Include durability data for each product

For each product, provide detailed information about brand, name, price, expected lifespan, key features, why it's special, web sources found, maintenance level, where to buy, who it's best for, AND durability data (user reports, failure points, repair mentions)."""

    async def search_products(self, query: str, context: Dict[str, Any],
                            tier_preference: Optional[str] = None,
                            max_price: Optional[float] = None) -> Dict[str, Any]:
        """
        Search for kitchen products based on user query.
        Checks database cache first to avoid redundant API calls.

        Args:
            query: User's search query
            context: User context (location, preferences, etc.)
            tier_preference: Optional tier filter (good, better, best)
            max_price: Optional maximum price filter

        Returns:
            Dictionary with tier results and metadata
        """
        # Step 1: Check database cache first
        if self.db:
            print(f"🔍 Checking cache for query: '{query}'")
            cached_result = await self.db.get_cached_search(
                query=query,
                tier_preference=tier_preference,
                max_price=max_price
            )

            if cached_result:
                print("✓ Cache hit! Returning cached results")
                # Convert SearchResponse to dict format expected by caller
                return {
                    "results": cached_result.results,
                    "search_metadata": cached_result.search_metadata,
                    "processing_time_seconds": 0.0,
                    "educational_insights": cached_result.educational_insights,
                    "cached": True
                }

            print("✗ Cache miss. Performing fresh search...")

        # Step 2: No cache hit - perform fresh search
        # Build the full query with context
        full_query = f"""Find kitchen products for: {query}

User context: {json.dumps(context, indent=2)}

Research the web thoroughly using Tavily. Focus on:
1. Reddit discussions (r/BuyItForLife, r/Cooking, r/AskCulinary)
2. Professional review sites
3. Specialty kitchen retailers
4. Hidden gems from niche manufacturers

Return results in Good/Better/Best tiers with full details including value calculations.
Format response as JSON matching the schema in the system prompt."""

        try:
            # Invoke the agent
            result = await self.agent_executor.ainvoke({
                "input": full_query
            })

            # Parse the agent's output
            parsed_result = self._parse_agent_output(result)

            # Step 3: Cache the results for future queries
            if self.db and parsed_result:
                print("💾 Caching search results to database...")
                # This will be done in main.py after creating SearchResponse
                parsed_result["should_cache"] = True
                parsed_result["cache_params"] = {
                    "tier_preference": tier_preference,
                    "max_price": max_price,
                    "context": context
                }

            return parsed_result

        except Exception as e:
            raise Exception(f"Agent search failed: {str(e)}")

    def _extract_durability_data(self, text: str, sources: List[str]) -> Dict[str, Any]:
        """
        Extract durability information from text using pattern matching.

        Args:
            text: Text to analyze (product description, reviews, etc.)
            sources: List of source URLs for attribution

        Returns:
            Dictionary with durability metrics
        """
        text_lower = text.lower()

        # Pattern 1: Extract years of ownership mentions
        # Matches: "still using after 10 years", "lasted 5 years", "had it for 8 years"
        ownership_patterns = [
            r'(?:still using|still works|still have|had it|lasted|using|owned|going strong).*?(\d+)\s*(?:years?)',
            r'(\d+)\s*(?:years?).*?(?:still works|still using|going strong|no issues)',
            r'(?:after|for)\s*(\d+)\s*(?:years?).*?(?:still|works|functional|good|great)',
        ]

        years_reported = []
        for pattern in ownership_patterns:
            matches = re.finditer(pattern, text_lower, re.IGNORECASE)
            for match in matches:
                try:
                    years = int(match.group(1))
                    if 1 <= years <= 50:  # Reasonable range
                        years_reported.append(years)
                except (ValueError, IndexError):
                    continue

        # Pattern 2: Extract failure reports
        # Matches: "broke after 2 years", "stopped working after 6 months", "failed after 3 years"
        failure_patterns = [
            r'(?:broke|failed|died|stopped|quit).*?(?:after|in)\s*(\d+)\s*(years?|months?)',
            r'(?:only lasted|lasted only)\s*(\d+)\s*(years?|months?)',
        ]

        failure_points = []
        for pattern in failure_patterns:
            matches = re.finditer(pattern, text_lower, re.IGNORECASE)
            for match in matches:
                try:
                    time_value = int(match.group(1))
                    time_unit = match.group(2)

                    # Convert to years
                    if 'month' in time_unit:
                        years = time_value / 12
                    else:
                        years = time_value

                    if 0.1 <= years <= 50:
                        failure_points.append(years)
                except (ValueError, IndexError):
                    continue

        # Pattern 3: Extract common failure descriptions
        # Look for specific failure mentions
        failure_descriptions = []
        failure_keywords = [
            r'handle (?:broke|broken|snapped)',
            r'(?:rust|rusted|rusting)(?:\s+after)?',
            r'motor (?:died|failed|stopped)',
            r'coating (?:peeled|chipped|worn)',
            r'blade (?:dull|chipped|bent)',
            r'hinge (?:broke|loose|failed)',
            r'seal (?:failed|leaked|worn)',
            r'gasket (?:failed|worn|leaked)',
            r'button (?:stuck|broke|stopped)',
            r'plastic (?:cracked|broke|melted)',
        ]

        for keyword_pattern in failure_keywords:
            matches = re.finditer(keyword_pattern, text_lower, re.IGNORECASE)
            for match in matches:
                failure_desc = match.group(0)
                if failure_desc not in failure_descriptions:
                    failure_descriptions.append(failure_desc)

        # Pattern 4: Extract repair mentions
        repair_patterns = [
            r'(?:easy|simple|can) (?:to )?(?:fix|repair)',
            r'replaced? (?:the )?(?:gasket|seal|blade|part)',
            r'repaired? (?:it )?(?:myself|at home)',
            r'(?:can\'t|cannot|difficult to|hard to) (?:be )?(?:fix|repair)',
            r'user[- ]serviceable',
            r'maintenance friendly',
        ]

        repair_mentions = []
        repairability_score = 50  # Default middle score

        for pattern in repair_patterns:
            matches = re.finditer(pattern, text_lower, re.IGNORECASE)
            for match in matches:
                mention = match.group(0)
                repair_mentions.append(mention)

                # Adjust repairability score based on mentions
                if any(word in mention for word in ['easy', 'simple', 'can', 'myself', 'serviceable', 'friendly']):
                    repairability_score = min(repairability_score + 10, 100)
                elif any(word in mention for word in ['can\'t', 'cannot', 'difficult', 'hard']):
                    repairability_score = max(repairability_score - 15, 0)

        # Calculate metrics
        total_reports = len(years_reported) + len(failure_points)
        users_5plus_years = len([y for y in years_reported if y >= 5])

        # Calculate average lifespan
        if years_reported:
            avg_lifespan = sum(years_reported) / len(years_reported)
        elif failure_points:
            avg_lifespan = sum(failure_points) / len(failure_points)
        else:
            avg_lifespan = 5.0  # Default estimate

        # Calculate percentage still working after 5 years
        if total_reports > 0:
            still_working_5yr_pct = int((users_5plus_years / total_reports) * 100)
        else:
            still_working_5yr_pct = 75  # Default estimate

        # Material quality indicators from text
        quality_indicators = []
        quality_keywords = [
            'stainless steel', 'carbon steel', 'cast iron', 'forged',
            'solid wood', 'hardwood', 'full tang', 'riveted',
            'teflon-free', 'pfoa-free', 'ceramic coating'
        ]

        for keyword in quality_keywords:
            if keyword in text_lower:
                quality_indicators.append(keyword)

        return {
            'years_reported': years_reported,
            'failure_points': failure_points,
            'failure_descriptions': failure_descriptions[:5],  # Top 5
            'repair_mentions': repair_mentions[:5],  # Top 5
            'total_user_reports': total_reports,
            'users_5plus_years': users_5plus_years,
            'average_lifespan_years': round(avg_lifespan, 1),
            'still_working_5yr_percent': still_working_5yr_pct,
            'repairability_score': repairability_score,
            'material_quality_indicators': quality_indicators,
            'data_sources': sources[:5]  # Top 5 sources
        }

    def _calculate_durability_score(self, durability_data: Dict[str, Any]) -> int:
        """
        Calculate overall durability score (0-100) based on extracted data.

        Scoring breakdown:
        - 40 points: Longevity (average lifespan)
        - 25 points: Failure rate (% still working after 5 years)
        - 20 points: Repairability
        - 15 points: Material quality

        Args:
            durability_data: Extracted durability metrics

        Returns:
            Overall score (0-100)
        """
        score = 0

        # 1. Longevity Score (0-40 points)
        # Based on average lifespan: 2 years = 10pts, 5 years = 20pts, 10+ years = 40pts
        avg_lifespan = durability_data.get('average_lifespan_years', 5.0)
        if avg_lifespan >= 15:
            longevity_score = 40
        elif avg_lifespan >= 10:
            longevity_score = 35
        elif avg_lifespan >= 7:
            longevity_score = 28
        elif avg_lifespan >= 5:
            longevity_score = 20
        elif avg_lifespan >= 3:
            longevity_score = 12
        else:
            longevity_score = int(avg_lifespan * 4)  # Proportional for < 3 years

        score += longevity_score

        # 2. Failure Rate Score (0-25 points)
        # Based on % still working after 5 years
        still_working_pct = durability_data.get('still_working_5yr_percent', 75)
        failure_score = int((still_working_pct / 100) * 25)
        score += failure_score

        # 3. Repairability Score (0-20 points)
        # Already calculated as 0-100, convert to 0-20
        repairability = durability_data.get('repairability_score', 50)
        repairability_score = int((repairability / 100) * 20)
        score += repairability_score

        # 4. Material Quality Score (0-15 points)
        # Based on number of quality indicators found
        quality_indicators = durability_data.get('material_quality_indicators', [])
        num_indicators = len(quality_indicators)
        if num_indicators >= 4:
            material_score = 15
        elif num_indicators == 3:
            material_score = 12
        elif num_indicators == 2:
            material_score = 9
        elif num_indicators == 1:
            material_score = 6
        else:
            material_score = 3  # Base score even without indicators

        score += material_score

        # Ensure score is within 0-100 range
        return max(0, min(100, score))

    def _parse_agent_output(self, agent_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse agent output into structured format and extract durability data.

        Args:
            agent_result: Raw output from agent executor

        Returns:
            Structured dictionary with tier results and durability data
        """
        # Extract the output text
        output_text = agent_result.get("output", "")

        # Try to extract JSON from the output
        try:
            # Look for JSON in the output (agent might include explanatory text)
            start_idx = output_text.find("{")
            end_idx = output_text.rfind("}") + 1

            if start_idx != -1 and end_idx > start_idx:
                json_str = output_text[start_idx:end_idx]
                parsed_data = json.loads(json_str)
            else:
                # If no JSON found, return a structured error
                parsed_data = {
                    "good_tier": [],
                    "better_tier": [],
                    "best_tier": [],
                    "sources": [],
                    "educational_insights": [],
                    "search_queries_used": [],
                    "raw_output": output_text
                }

            # Extract durability data for each product in each tier
            for tier_name in ["good_tier", "better_tier", "best_tier"]:
                tier_products = parsed_data.get(tier_name, [])

                for product in tier_products:
                    # Combine all text sources for durability analysis
                    analysis_text = ""

                    # Add product description
                    analysis_text += f"{product.get('name', '')} "
                    analysis_text += f"{product.get('why_its_a_gem', '')} "
                    analysis_text += " ".join(product.get('key_features', []))
                    analysis_text += f" {product.get('best_for', '')} "
                    analysis_text += " ".join(product.get('trade_offs', []))

                    # Add any durability text from agent if present
                    if 'durability_info' in product:
                        analysis_text += f" {product.get('durability_info', '')}"

                    # Extract source URLs for attribution
                    sources = []
                    for source in product.get('web_sources', []):
                        if isinstance(source, dict):
                            url = source.get('url', '')
                            if url:
                                sources.append(url)
                        elif isinstance(source, str):
                            sources.append(source)

                    # Extract durability data from text
                    durability_data = self._extract_durability_data(analysis_text, sources)

                    # Calculate overall durability score
                    durability_score = self._calculate_durability_score(durability_data)

                    # Create DurabilityData object for the product
                    product['durability_data_extracted'] = {
                        'score': durability_score,
                        'average_lifespan_years': durability_data['average_lifespan_years'],
                        'still_working_after_5years_percent': durability_data['still_working_5yr_percent'],
                        'total_user_reports': durability_data['total_user_reports'],
                        'common_failure_points': durability_data['failure_descriptions'],
                        'repairability_score': durability_data['repairability_score'],
                        'material_quality_indicators': durability_data['material_quality_indicators'],
                        'data_sources': durability_data['data_sources']
                    }

                    print(f"  ✓ Extracted durability data for {product.get('name', 'product')}: score={durability_score}")

            return parsed_data

        except json.JSONDecodeError as e:
            # Return raw output if JSON parsing fails
            return {
                "good_tier": [],
                "better_tier": [],
                "best_tier": [],
                "sources": [],
                "educational_insights": [
                    "Agent returned results but in unexpected format. Working on improving this."
                ],
                "search_queries_used": [],
                "raw_output": output_text,
                "parse_error": str(e)
            }


# Global agent instance (singleton pattern)
_agent_instance = None


def get_agent() -> KennyAgent:
    """Get or create the global agent instance"""
    global _agent_instance
    if _agent_instance is None:
        _agent_instance = KennyAgent()
    return _agent_instance
