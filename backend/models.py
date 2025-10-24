"""
Data models for Kenny Gem Finder API
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum


class TierLevel(str, Enum):
    """Tier level classification"""
    GOOD = "good"
    BETTER = "better"
    BEST = "best"


class ValueMetrics(BaseModel):
    """Value analysis for a product"""
    upfront_price: float = Field(..., description="Purchase price in USD", gt=0)
    expected_lifespan_years: float = Field(..., description="Expected years of use", gt=0)
    cost_per_year: float = Field(..., description="Calculated: price / lifespan")
    cost_per_day: float = Field(..., description="Calculated: cost_per_year / 365")

    @classmethod
    def calculate(cls, price: float, lifespan: float) -> "ValueMetrics":
        """Calculate value metrics from price and lifespan"""
        if lifespan <= 0:
            raise ValueError("Lifespan must be greater than 0")
        if price <= 0:
            raise ValueError("Price must be greater than 0")

        cost_per_year = price / lifespan
        cost_per_day = cost_per_year / 365

        return cls(
            upfront_price=round(price, 2),
            expected_lifespan_years=round(lifespan, 1),
            cost_per_year=round(cost_per_year, 2),
            cost_per_day=round(cost_per_day, 2)
        )


class WebSource(BaseModel):
    """Web source citation"""
    url: str
    title: str
    snippet: str
    relevance_score: Optional[float] = None


class DurabilityData(BaseModel):
    """Durability data from user reports and research"""
    score: int = Field(..., ge=0, le=100, description="Overall durability score (0-100)")
    average_lifespan_years: float = Field(..., description="Average lifespan based on user reports")
    still_working_after_5years_percent: int = Field(..., ge=0, le=100, description="% still working after 5 years")
    total_user_reports: int = Field(default=0, description="Number of user reports aggregated")
    common_failure_points: List[str] = Field(default_factory=list, description="Common points of failure")
    repairability_score: int = Field(..., ge=0, le=100, description="How easy to repair (0-100)")
    material_quality_indicators: List[str] = Field(default_factory=list, description="Quality indicators from materials")
    data_sources: List[str] = Field(default_factory=list, description="Reddit threads, review sites, etc.")


class AlternativeSolution(BaseModel):
    """Non-purchase solution to solve the problem"""
    problem: str = Field(..., description="The problem the user is trying to solve")
    consumer_solution: str = Field(..., description="What people typically buy")
    consumer_cost: float = Field(..., description="Cost of consumer solution")
    consumer_issues: List[str] = Field(..., description="Problems with buying approach")
    your_solution: str = Field(..., description="Non-purchase or cheaper alternative")
    your_cost: float = Field(..., description="Cost of your solution")
    why_better: str = Field(..., description="Why this approach is better")
    how_to: str = Field(..., description="Step-by-step instructions")
    savings_per_year: float = Field(..., description="Calculated savings")
    when_to_buy_instead: Optional[str] = Field(None, description="When the purchase makes sense")


class BeforeYouBuy(BaseModel):
    """Section showing alternatives before pushing products"""
    title: str = Field(default="Before You Buy...", description="Section title")
    subtitle: str = Field(default="Let's solve the problem first", description="Subtitle")
    alternatives: List[AlternativeSolution] = Field(..., description="Non-purchase solutions")
    educational_insight: str = Field(..., description="Why we show this")


class Product(BaseModel):
    """Kitchen product with full details"""
    name: str = Field(..., description="Product name and model")
    brand: str
    tier: TierLevel
    category: str = Field(..., description="e.g., chef's knife, skillet, dutch oven")

    # Value metrics (most important!)
    value_metrics: ValueMetrics

    # Durability data (NEW!)
    durability_data: Optional[DurabilityData] = Field(None, description="Durability data from user reports and research")

    # Core details
    key_features: List[str] = Field(..., description="Top 3-5 features", min_length=1)
    materials: List[str] = Field(default_factory=list)
    why_its_a_gem: str = Field(..., description="What makes it special from web research")

    # Web research findings
    web_sources: List[WebSource] = Field(..., description="Sources from Tavily search")
    reddit_mentions: Optional[int] = None
    professional_reviews: List[str] = Field(default_factory=list)

    # Practical info
    maintenance_level: str = Field(..., description="Low, Medium, or High")
    purchase_links: List[Dict[str, str]] = Field(default_factory=list)

    # Context considerations
    environmental_warnings: Optional[List[str]] = None
    best_for: str = Field(..., description="Life stage/use case match")

    # Trade-offs
    trade_offs: Optional[List[str]] = Field(default_factory=list, description="Honest drawbacks")


class ProductTier(BaseModel):
    """Product tier with aggregated products and durability data"""
    tier: TierLevel
    products: List[Product] = Field(default_factory=list)
    durability: Optional[DurabilityData] = Field(None, description="Aggregate durability data for this tier")


class SearchQuery(BaseModel):
    """User search request"""
    query: str = Field(..., min_length=3, description="User's search query")
    tier_preference: Optional[TierLevel] = None
    max_price: Optional[float] = Field(None, gt=0)
    context: Optional[Dict[str, str]] = Field(default_factory=dict, description="User context like location, experience level")


class TierResults(BaseModel):
    """Results organized by tier"""
    good: List[Product] = Field(default_factory=list)
    better: List[Product] = Field(default_factory=list)
    best: List[Product] = Field(default_factory=list)


class SearchResponse(BaseModel):
    """Search API response"""
    before_you_buy: Optional[BeforeYouBuy] = Field(None, description="Alternative solutions before showing products")
    results: TierResults
    search_metadata: Dict[str, Any] = Field(..., description="Queries used, sources searched")
    processing_time_seconds: float
    educational_insights: Optional[List[str]] = Field(default_factory=list, description="Tips and common mistakes")


class HealthCheckResponse(BaseModel):
    """Health check response"""
    status: str
    version: str
    environment: str


class ErrorResponse(BaseModel):
    """Error response"""
    error: str
    detail: Optional[str] = None
    status_code: int
