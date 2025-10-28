"""
Characteristic Generator
Generates 5 buying characteristics for a product search query based on location and context
"""
import json
from typing import List, Dict
from openai import OpenAI
import os

class CharacteristicGenerator:
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")
        self.client = OpenAI(api_key=api_key)

    def generate_characteristics(
        self,
        query: str,
        location: str = "US",
        context: Dict = None
    ) -> List[Dict]:
        """
        Generate 5 buying characteristics for a product search

        Args:
            query: Search query (e.g., "cast iron skillet", "chef's knife")
            location: User location (e.g., "Austin, TX", "Seattle, WA")
            context: Additional context (experience_level, budget, etc.)

        Returns:
            List of 5 characteristics:
            [
              {
                "label": "PRE-SEASONED",
                "reason": "Ready to use",
                "explanation": "Pre-seasoned cast iron is ready out of the box...",
                "image_keyword": "cast iron seasoned"
              },
              ...
            ]
        """
        system_prompt = self._build_system_prompt()
        user_prompt = self._build_user_prompt(query, location, context or {})

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=1000
            )

            content = response.choices[0].message.content.strip()

            # Remove markdown code blocks if present
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()

            # Parse JSON
            characteristics = json.loads(content)

            # Validate we have exactly 5 characteristics
            if not isinstance(characteristics, list):
                raise ValueError("Response is not a list")
            if len(characteristics) != 5:
                raise ValueError(f"Expected 5 characteristics, got {len(characteristics)}")

            # Validate each characteristic has required fields
            required_fields = ["label", "reason", "explanation", "image_keyword"]
            for char in characteristics:
                for field in required_fields:
                    if field not in char:
                        raise ValueError(f"Missing field: {field}")

            return characteristics

        except json.JSONDecodeError as e:
            print(f"Failed to parse JSON: {e}")
            print(f"Raw content: {content}")
            # Return fallback characteristics
            return self._get_fallback_characteristics(query)
        except Exception as e:
            print(f"Error generating characteristics: {e}")
            return self._get_fallback_characteristics(query)

    def _build_system_prompt(self) -> str:
        return """You are Kenny, an expert kitchen product advisor. Your job is to generate 5 key buying characteristics that users should look for when shopping for a specific kitchen product.

Your characteristics should be:
1. Practical and specific (not generic advice)
2. Based on common problems users face
3. Influenced by location factors (climate, water quality, etc.)
4. Drawn from Reddit discussions and expert reviews
5. Focused on durability and long-term value

Return ONLY a JSON array with exactly 5 characteristics. Each characteristic must have:
- label: Short characteristic name (2-4 words, UPPERCASE)
- reason: Brief reason (3-5 words)
- explanation: 1 sentence explanation
- image_keyword: Keyword for image search (2-3 words)

Example format:
[
  {
    "label": "PRE-SEASONED",
    "reason": "Ready to use",
    "explanation": "Pre-seasoned cast iron doesn't require initial seasoning and is ready to cook with right out of the box.",
    "image_keyword": "cast iron seasoned"
  },
  ...
]

DO NOT include markdown code blocks or any other text. Return ONLY the JSON array."""

    def _build_user_prompt(self, query: str, location: str, context: Dict) -> str:
        return f"""Generate 5 buying characteristics for: "{query}"

User location: {location}
Context: {json.dumps(context) if context else 'None'}

Consider:
- Local climate and environmental factors (e.g., hard water in Austin, humidity in Seattle)
- Common problems with this product category
- What Reddit users in r/BuyItForLife, r/Cooking, and r/AskCulinary recommend
- Practical usage factors
- Durability and maintenance needs

Return exactly 5 characteristics as a JSON array."""

    def _get_fallback_characteristics(self, query: str) -> List[Dict]:
        """Return generic fallback characteristics if AI generation fails"""
        return [
            {
                "label": "DURABLE MATERIALS",
                "reason": "Lasts longer",
                "explanation": f"Look for {query} made with high-quality materials that resist wear and tear.",
                "image_keyword": f"{query} quality"
            },
            {
                "label": "EASY MAINTENANCE",
                "reason": "Less hassle",
                "explanation": f"Choose {query} that are simple to clean and maintain over time.",
                "image_keyword": f"{query} cleaning"
            },
            {
                "label": "PROVEN BRAND",
                "reason": "Reliable quality",
                "explanation": f"Stick with {query} from brands with strong reputations and user reviews.",
                "image_keyword": f"{query} brand"
            },
            {
                "label": "GOOD VALUE",
                "reason": "Worth the cost",
                "explanation": f"Consider cost-per-year when evaluating {query} options.",
                "image_keyword": f"{query} value"
            },
            {
                "label": "USER RECOMMENDED",
                "reason": "Community approved",
                "explanation": f"Look for {query} frequently mentioned in Reddit's buy-it-for-life communities.",
                "image_keyword": f"{query} review"
            }
        ]


# Singleton instance
_generator_instance = None

def get_characteristic_generator() -> CharacteristicGenerator:
    """Get or create the characteristic generator instance"""
    global _generator_instance
    if _generator_instance is None:
        _generator_instance = CharacteristicGenerator()
    return _generator_instance
