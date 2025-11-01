"""
Template selector for matching user queries to SQL templates.

Uses few-shot examples and keyword matching to select appropriate templates.
Constitutional Principle V: LLM selects templates but does not modify SQL structure.
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from difflib import SequenceMatcher

from src.templates.template_loader import get_template_loader
from config.settings import get_settings


class TemplateSelector:
    """
    Selects appropriate SQL template based on user query and intent.

    Uses:
    - Few-shot example matching
    - Keyword similarity
    - Template metadata (example questions)
    - Intent category filtering
    """

    def __init__(self):
        """Initialize template selector."""
        self.settings = get_settings()
        self.template_loader = get_template_loader()
        self._load_few_shot_examples()

    def _load_few_shot_examples(self) -> None:
        """Load few-shot examples for template matching."""
        few_shot_path = Path(self.settings.few_shot_examples_path)

        if few_shot_path.exists():
            with open(few_shot_path, 'r') as f:
                data = json.load(f)
                self.examples = data.get("examples", [])
        else:
            self.examples = []

    def select_template(
        self,
        user_query: str,
        intent: str
    ) -> Tuple[Optional[str], float, Dict]:
        """
        Select best matching template for user query.

        Args:
            user_query: Natural language query
            intent: Query intent (sales, traffic, conversion)

        Returns:
            Tuple of (template_id, confidence_score, match_info)
        """
        # Filter examples by intent
        relevant_examples = [
            ex for ex in self.examples
            if ex.get("category") == intent
        ]

        if not relevant_examples:
            return None, 0.0, {"reason": "No examples for intent"}

        # Find best matching example
        best_match = None
        best_score = 0.0

        for example in relevant_examples:
            example_query = example.get("user_query", "")
            similarity = self._calculate_similarity(user_query, example_query)

            if similarity > best_score:
                best_score = similarity
                best_match = example

        # Require minimum confidence threshold
        min_confidence = 0.3
        if best_score < min_confidence:
            return None, best_score, {"reason": "Low confidence match"}

        if best_match:
            template_id = best_match.get("template_id")
            match_info = {
                "matched_example": best_match.get("user_query"),
                "similarity_score": best_score,
                "explanation": best_match.get("explanation")
            }
            return template_id, best_score, match_info

        return None, 0.0, {"reason": "No suitable match found"}

    def _calculate_similarity(self, query1: str, query2: str) -> float:
        """
        Calculate similarity between two queries.

        Args:
            query1: First query
            query2: Second query

        Returns:
            Similarity score (0.0 to 1.0)
        """
        # Convert to lowercase for comparison
        q1_lower = query1.lower()
        q2_lower = query2.lower()

        # Use SequenceMatcher for string similarity
        base_similarity = SequenceMatcher(None, q1_lower, q2_lower).ratio()

        # Boost score if key phrases match
        q1_words = set(q1_lower.split())
        q2_words = set(q2_lower.split())
        common_words = q1_words & q2_words

        # Important keywords boost similarity
        important_keywords = {
            "sales", "revenue", "products", "top", "total", "average",
            "last", "this", "week", "month", "year", "yesterday"
        }
        important_matches = common_words & important_keywords

        keyword_bonus = len(important_matches) * 0.1
        final_score = min(1.0, base_similarity + keyword_bonus)

        return final_score

    def get_template_suggestions(self, intent: str, limit: int = 5) -> List[Dict]:
        """
        Get template suggestions for an intent category.

        Args:
            intent: Intent category
            limit: Maximum number of suggestions

        Returns:
            List of template suggestions with examples
        """
        relevant_templates = {}

        for example in self.examples:
            if example.get("category") == intent:
                template_id = example.get("template_id")
                if template_id not in relevant_templates:
                    relevant_templates[template_id] = {
                        "template_id": template_id,
                        "examples": []
                    }
                relevant_templates[template_id]["examples"].append(
                    example.get("user_query")
                )

        suggestions = list(relevant_templates.values())[:limit]
        return suggestions

    def validate_template_for_intent(
        self,
        template_id: str,
        intent: str
    ) -> bool:
        """
        Validate that template matches the intent category.

        Args:
            template_id: Template identifier
            intent: Intent category

        Returns:
            True if template is valid for intent
        """
        template = self.template_loader.load_template(template_id)
        if not template:
            return False

        template_category = template.get("category")
        return template_category == intent


# Global template selector instance
_template_selector: Optional[TemplateSelector] = None


def get_template_selector() -> TemplateSelector:
    """
    Get or create the global template selector.

    Returns:
        TemplateSelector instance
    """
    global _template_selector
    if _template_selector is None:
        _template_selector = TemplateSelector()
    return _template_selector
