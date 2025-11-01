"""
LLM intent classifier for user query categorization.

Classifies queries into categories: sales, traffic, conversion, unknown.
Uses keyword matching and pattern recognition (LLM integration for Phase 3).
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from config.settings import get_settings


class IntentClassifier:
    """
    Classifies user query intent to determine which templates to consider.

    Categories:
    - sales: Revenue, products, transactions, purchases
    - traffic: Visitors, visits, sessions, pageviews
    - conversion: Conversion rate, business metrics, multi-metric
    - unknown: Cannot classify
    """

    def __init__(self):
        """Initialize intent classifier."""
        self.settings = get_settings()
        self._load_indicators()

    def _load_indicators(self) -> None:
        """Load intent indicators from few-shot examples."""
        few_shot_path = Path(self.settings.few_shot_examples_path)

        if few_shot_path.exists():
            with open(few_shot_path, 'r') as f:
                data = json.load(f)
                guidelines = data.get("template_selection_guidelines", {})

                self.sales_indicators = guidelines.get("sales_indicators", [
                    "sales", "revenue", "products", "transactions", "purchases", "orders"
                ])
                self.traffic_indicators = guidelines.get("traffic_indicators", [
                    "visitors", "visits", "traffic", "sessions", "pageviews"
                ])
                self.conversion_indicators = guidelines.get("conversion_indicators", [
                    "conversion", "rate", "business", "performance", "metrics"
                ])
        else:
            # Default indicators if file not found
            self.sales_indicators = ["sales", "revenue", "products", "transactions", "purchases"]
            self.traffic_indicators = ["visitors", "visits", "traffic", "sessions"]
            self.conversion_indicators = ["conversion", "rate", "business", "performance"]

    def classify(self, user_query: str) -> Tuple[str, float]:
        """
        Classify user query intent.

        Args:
            user_query: Natural language query

        Returns:
            Tuple of (category, confidence_score)
        """
        query_lower = user_query.lower()

        # Count matches for each category
        sales_score = sum(1 for kw in self.sales_indicators if kw in query_lower)
        traffic_score = sum(1 for kw in self.traffic_indicators if kw in query_lower)
        conversion_score = sum(1 for kw in self.conversion_indicators if kw in query_lower)

        # Determine category based on highest score
        scores = {
            "sales": sales_score,
            "traffic": traffic_score,
            "conversion": conversion_score
        }

        max_category = max(scores, key=scores.get)
        max_score = scores[max_category]

        if max_score == 0:
            return "unknown", 0.0

        # Calculate confidence (simple approach for now)
        total_score = sum(scores.values())
        confidence = max_score / total_score if total_score > 0 else 0.0

        return max_category, confidence

    def get_category_description(self, category: str) -> str:
        """
        Get human-readable description of category.

        Args:
            category: Intent category

        Returns:
            Description string
        """
        descriptions = {
            "sales": "Sales and revenue analysis",
            "traffic": "Website traffic and visitor analysis",
            "conversion": "Conversion and business performance metrics",
            "unknown": "Unable to determine query type"
        }
        return descriptions.get(category, "Unknown category")

    def suggest_rephrase(self, user_query: str) -> Optional[str]:
        """
        Suggest how to rephrase an unclear query.

        Args:
            user_query: Natural language query

        Returns:
            Suggestion string or None
        """
        category, confidence = self.classify(user_query)

        if category == "unknown":
            return (
                "I'm not sure what you're asking about. Try questions like:\n"
                "- 'What were sales last week?' (for sales data)\n"
                "- 'How many visitors yesterday?' (for traffic data)\n"
                "- 'What's our conversion rate?' (for business metrics)"
            )

        if confidence < 0.5:
            return (
                f"Your question seems to be about {self.get_category_description(category)}, "
                f"but I'm not entirely sure. Could you rephrase it more specifically?"
            )

        return None


# Global classifier instance
_intent_classifier: Optional[IntentClassifier] = None


def get_intent_classifier() -> IntentClassifier:
    """
    Get or create the global intent classifier.

    Returns:
        IntentClassifier instance
    """
    global _intent_classifier
    if _intent_classifier is None:
        _intent_classifier = IntentClassifier()
    return _intent_classifier
