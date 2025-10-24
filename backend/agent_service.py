"""
AI Agent Service for Kenny Gem Finder
Uses LangChain with Tavily search to find and organize kitchen products
"""
import os
import json
from typing import Dict, Any, List
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain_openai import ChatOpenAI
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.schema import AIMessage

from models import (
    TierResults,
    Product,
    ProductTier,
    ValueMetrics,
    WebSource
)


class KennyAgent:
    """
    AI Agent for researching kitchen products and organizing them into tiers
    """

    def __init__(self):
        """Initialize the agent with LangChain and Tavily"""
        # Check for required API keys
        self.openai_key = os.getenv("OPENAI_API_KEY")
        self.tavily_key = os.getenv("TAVILY_API_KEY")

        if not self.openai_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        if not self.tavily_key:
            raise ValueError("TAVILY_API_KEY not found in environment variables")

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

IMPORTANT:
- Kitchen products ONLY
- Cite sources with URLs
- Be honest about trade-offs
- Find at least 1-2 products per tier

For each product, provide detailed information about brand, name, price, expected lifespan, key features, why it's special, web sources found, maintenance level, where to buy, and who it's best for."""

    async def search_products(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Search for kitchen products based on user query

        Args:
            query: User's search query
            context: User context (location, preferences, etc.)

        Returns:
            Dictionary with tier results and metadata
        """
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
            return self._parse_agent_output(result)

        except Exception as e:
            raise Exception(f"Agent search failed: {str(e)}")

    def _parse_agent_output(self, agent_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse agent output into structured format

        Args:
            agent_result: Raw output from agent executor

        Returns:
            Structured dictionary with tier results
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
