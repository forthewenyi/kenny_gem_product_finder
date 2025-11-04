"""
Quality Score Calculator for Kenny Gem Finder
Calculates a 0-100 quality score based on 4 components:
- 40 points: Longevity Reports (how long users keep it)
- 25 points: Failure Rate (what % still works after 5+ years)
- 20 points: Repairability (can you fix it?)
- 15 points: Material Quality Indicators
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class QualityScore:
    """Complete quality score with component breakdown"""
    total: int  # 0-100
    longevity_score: int  # 0-40
    failure_rate_score: int  # 0-25
    repairability_score: int  # 0-20
    material_quality_score: int  # 0-15

    # Metadata for display
    longevity_data: Dict[str, Any]
    failure_data: Dict[str, Any]
    repairability_data: Dict[str, Any]
    material_data: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total": self.total,
            "longevity_score": self.longevity_score,
            "failure_rate_score": self.failure_rate_score,
            "repairability_score": self.repairability_score,
            "material_quality_score": self.material_quality_score,
            "longevity_data": self.longevity_data,
            "failure_data": self.failure_data,
            "repairability_data": self.repairability_data,
            "material_data": self.material_data,
        }

    def get_grade(self) -> str:
        """Get letter grade based on total score"""
        if self.total >= 90:
            return "A+"
        elif self.total >= 85:
            return "A"
        elif self.total >= 80:
            return "A-"
        elif self.total >= 75:
            return "B+"
        elif self.total >= 70:
            return "B"
        elif self.total >= 65:
            return "B-"
        elif self.total >= 60:
            return "C+"
        elif self.total >= 55:
            return "C"
        else:
            return "C-"


class QualityScorer:
    """Calculate quality scores from product data"""

    def calculate_longevity_score(self, lifespan_years: float, user_reports: Optional[Dict] = None) -> tuple[int, Dict]:
        """
        Calculate longevity score (0-40 points)
        Based on average lifespan from user reports

        Scoring (matches formula):
        - >= 15 years: 40 points (lifetime investment)
        - >= 10 years: 32 points (excellent)
        - >= 5 years: 24 points (very good)
        - >= 3 years: 16 points (good)
        - < 3 years: 8 points (short-lived)
        """
        if lifespan_years >= 15:
            score = 40
            category = "Lifetime Investment"
        elif lifespan_years >= 10:
            score = 32
            category = "Excellent"
        elif lifespan_years >= 5:
            score = 24
            category = "Very Good"
        elif lifespan_years >= 3:
            score = 16
            category = "Good"
        else:
            score = 8
            category = "Short-Lived"

        data = {
            "expected_years": lifespan_years,
            "category": category,
            "user_reports": user_reports or {}
        }

        return score, data

    def calculate_failure_rate_score(self, working_percent: Optional[float] = None,
                                     failure_percentage: Optional[float] = None,
                                     reddit_mentions: Optional[int] = None) -> tuple[int, Dict]:
        """
        Calculate failure rate score (0-25 points)
        Based on % of products still working after 5+ years

        Scoring (matches formula):
        - score = working_percent * 0.25
        - Example: 80% still working = 80 * 0.25 = 20 points

        If no data available, estimate from failure_percentage or reddit mentions
        """
        if working_percent is not None:
            # Direct formula: working_percent * 0.25
            score = int(working_percent * 0.25)
            score = max(0, min(score, 25))  # Clamp to 0-25
            reliability = self._get_reliability_category(working_percent)
        elif failure_percentage is not None:
            # Convert failure % to working %
            working_percent = 100 - failure_percentage
            score = int(working_percent * 0.25)
            score = max(0, min(score, 25))
            reliability = self._get_reliability_category(working_percent)
        else:
            # Estimate from reddit sentiment (if available)
            if reddit_mentions and reddit_mentions > 10:
                working_percent = 80  # estimated for popular products
                score = 20
                reliability = "Community Trusted (estimated)"
            else:
                working_percent = 75  # default estimate
                score = 19
                reliability = "Limited Data (estimated)"

        data = {
            "working_percent": working_percent,
            "failure_percentage": 100 - working_percent if working_percent else None,
            "reliability": reliability,
            "reddit_mentions": reddit_mentions
        }

        return score, data

    def _get_reliability_category(self, working_percent: float) -> str:
        """Get reliability category based on % still working"""
        if working_percent >= 95:
            return "Rock Solid"
        elif working_percent >= 85:
            return "Very Reliable"
        elif working_percent >= 75:
            return "Reliable"
        elif working_percent >= 60:
            return "Some Issues"
        elif working_percent >= 40:
            return "Concerning"
        else:
            return "High Failure Rate"

    def calculate_repairability_score(self, repairability_info: Optional[str] = None,
                                     repair_score_raw: Optional[int] = None,
                                     maintenance_level: Optional[str] = None) -> tuple[int, Dict]:
        """
        Calculate repairability score (0-20 points)
        Based on how easy it is to repair/maintain

        Scoring (matches formula):
        - score = repair_score (0-100) * 0.20
        - Example: 80/100 repairability = 80 * 0.20 = 16 points

        Scoring guide for repair_score_raw (0-100):
        - 100-90: User-serviceable, easy DIY repair
        - 89-70: Professional repair available
        - 69-50: Some repair possible
        - 49-30: Limited repair options
        - 29-0: Not repairable
        """
        # If raw score provided (0-100), use formula
        if repair_score_raw is not None:
            score = int(repair_score_raw * 0.20)
            score = max(0, min(score, 20))  # Clamp to 0-20
            category = self._get_repairability_category(repair_score_raw)
        # Parse repairability from text descriptions
        elif repairability_info:
            info_lower = repairability_info.lower()

            if any(word in info_lower for word in ["user-serviceable", "easy to repair", "diy repair", "spare parts available"]):
                repair_score_raw = 95
                score = int(95 * 0.20)  # = 19
                category = "User-Serviceable"
            elif any(word in info_lower for word in ["professional repair", "authorized service", "repairable"]):
                repair_score_raw = 75
                score = int(75 * 0.20)  # = 15
                category = "Professional Repair"
            elif any(word in info_lower for word in ["some repair", "limited repair", "basic maintenance"]):
                repair_score_raw = 55
                score = int(55 * 0.20)  # = 11
                category = "Limited Repair"
            elif any(word in info_lower for word in ["difficult to repair", "proprietary parts"]):
                repair_score_raw = 30
                score = int(30 * 0.20)  # = 6
                category = "Difficult to Repair"
            else:
                repair_score_raw = 50
                score = int(50 * 0.20)  # = 10
                category = "Standard Repair"
        else:
            # Estimate from maintenance level
            if maintenance_level:
                level_lower = maintenance_level.lower()
                if "low" in level_lower:
                    repair_score_raw = 75
                    score = int(75 * 0.20)  # = 15
                    category = "Low Maintenance"
                elif "medium" in level_lower or "moderate" in level_lower:
                    repair_score_raw = 50
                    score = int(50 * 0.20)  # = 10
                    category = "Medium Maintenance"
                else:
                    repair_score_raw = 40
                    score = int(40 * 0.20)  # = 8
                    category = "High Maintenance"
            else:
                repair_score_raw = 50
                score = int(50 * 0.20)  # = 10
                category = "Unknown"

        data = {
            "repair_score_raw": repair_score_raw,
            "category": category,
            "maintenance_level": maintenance_level,
            "notes": repairability_info
        }

        return score, data

    def _get_repairability_category(self, repair_score: int) -> str:
        """Get repairability category based on 0-100 score"""
        if repair_score >= 90:
            return "User-Serviceable"
        elif repair_score >= 70:
            return "Professional Repair"
        elif repair_score >= 50:
            return "Limited Repair"
        elif repair_score >= 30:
            return "Difficult to Repair"
        else:
            return "Not Repairable"

    def calculate_material_quality_score(self, materials: list[str],
                                        material_score_raw: Optional[int] = None,
                                        why_gem: Optional[str] = None,
                                        tier: str = "better") -> tuple[int, Dict]:
        """
        Calculate material quality score (0-15 points)
        Based on materials used and construction quality

        Scoring (matches formula):
        - score = material_score (0-100) * 0.15
        - Example: 80/100 materials = 80 * 0.15 = 12 points

        Scoring guide for material_score_raw (0-100):
        - 100-90: Premium materials (cast iron, forged steel, solid wood)
        - 89-70: High-quality materials (stainless steel, hard-anodized aluminum)
        - 69-50: Good materials (aluminum, ceramic)
        - 49-30: Standard materials
        - 29-0: Low-quality materials
        """
        # If raw score provided (0-100), use formula
        if material_score_raw is not None:
            score = int(material_score_raw * 0.15)
            score = max(0, min(score, 15))  # Clamp to 0-15
            quality_level = self._get_material_quality_level(material_score_raw)
            material_grades = [{"material": "Custom", "quality": quality_level, "score": material_score_raw}]
        else:
            # Calculate from materials list
            raw_score = 0
            material_grades = []

            # Premium materials scoring (0-100 scale)
            premium_materials = {
                "stainless steel": 33,  # 33 * 3 materials = ~99
                "cast iron": 35,
                "carbon steel": 34,
                "forged steel": 35,
                "high-carbon stainless": 35,
                "copper": 30,
                "aluminum": 25,
                "hard-anodized aluminum": 30,
                "enameled cast iron": 35,
                "ceramic": 25,
                "glass": 22,
                "wood": 28,
                "bamboo": 26,
            }

            for material in materials:
                material_lower = material.lower()
                for premium, points in premium_materials.items():
                    if premium in material_lower:
                        raw_score = min(raw_score + points, 100)  # Cap at 100
                        material_grades.append({
                            "material": material,
                            "quality": "Premium" if points >= 30 else "Good"
                        })
                        break

            # If no materials specified, estimate from tier
            if raw_score == 0:
                if tier == "best":
                    raw_score = 80
                    material_grades.append({"material": "Unknown", "quality": "Premium (estimated)"})
                elif tier == "better":
                    raw_score = 60
                    material_grades.append({"material": "Unknown", "quality": "Good (estimated)"})
                else:
                    raw_score = 40
                    material_grades.append({"material": "Unknown", "quality": "Standard (estimated)"})

            # Boost score if "why_gem" mentions quality construction
            if why_gem:
                why_lower = why_gem.lower()
                quality_indicators = ["professional-grade", "commercial quality", "heirloom", "lifetime warranty"]
                if any(indicator in why_lower for indicator in quality_indicators):
                    raw_score = min(raw_score + 10, 100)

            # Apply formula
            material_score_raw = raw_score
            score = int(raw_score * 0.15)
            score = max(0, min(score, 15))
            quality_level = self._get_material_quality_level(raw_score)

        data = {
            "material_score_raw": material_score_raw,
            "materials": material_grades,
            "quality_level": quality_level
        }

        return score, data

    def _get_material_quality_level(self, material_score: int) -> str:
        """Get material quality level based on 0-100 score"""
        if material_score >= 90:
            return "Premium"
        elif material_score >= 70:
            return "High-Quality"
        elif material_score >= 50:
            return "Good"
        elif material_score >= 30:
            return "Standard"
        else:
            return "Low-Quality"

    def calculate_quality_score(self, product_data: Dict[str, Any]) -> QualityScore:
        """
        Calculate complete quality score from product data

        Args:
            product_data: Dict with keys:
                - expected_lifespan_years (required)
                - failure_percentage (optional)
                - reddit_mentions (optional)
                - repairability_info (optional)
                - maintenance_level (optional)
                - materials (optional list)
                - why_gem (optional)
                - tier (optional)

        Returns:
            QualityScore object with total and component scores
        """
        # Component 1: Longevity (40 points)
        longevity_score, longevity_data = self.calculate_longevity_score(
            product_data.get("expected_lifespan_years", 5),
            product_data.get("user_reports")
        )

        # Component 2: Failure Rate (25 points)
        failure_score, failure_data = self.calculate_failure_rate_score(
            working_percent=None,
            failure_percentage=product_data.get("failure_percentage"),
            reddit_mentions=product_data.get("reddit_mentions")
        )

        # Component 3: Repairability (20 points)
        repairability_score, repairability_data = self.calculate_repairability_score(
            repairability_info=product_data.get("repairability_info"),
            repair_score_raw=None,
            maintenance_level=product_data.get("maintenance_level")
        )

        # Component 4: Material Quality (15 points)
        material_score, material_data = self.calculate_material_quality_score(
            materials=product_data.get("materials", []),
            material_score_raw=None,
            why_gem=product_data.get("why_gem"),
            tier=product_data.get("tier", "better")
        )

        # Total score
        total = longevity_score + failure_score + repairability_score + material_score

        return QualityScore(
            total=total,
            longevity_score=longevity_score,
            failure_rate_score=failure_score,
            repairability_score=repairability_score,
            material_quality_score=material_score,
            longevity_data=longevity_data,
            failure_data=failure_data,
            repairability_data=repairability_data,
            material_data=material_data
        )


# Singleton instance
_scorer_instance = None


def get_quality_scorer() -> QualityScorer:
    """Get or create the global quality scorer instance"""
    global _scorer_instance
    if _scorer_instance is None:
        _scorer_instance = QualityScorer()
    return _scorer_instance
