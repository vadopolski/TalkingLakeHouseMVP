"""
Parameter extractor for SQL template parameters.

Extracts dates, product names, metrics, and other parameters from natural language.
Constitutional Principle V: LLM extracts parameter values but does not modify SQL.
"""

import re
from datetime import datetime, timedelta
from typing import Any, Dict, Optional
import json
from pathlib import Path

from config.settings import get_settings


class ParameterExtractor:
    """
    Extracts parameters from natural language queries.

    Handles:
    - Date extraction (relative and absolute)
    - Aggregation types (sum, average, count)
    - Sorting/ordering preferences
    - Numeric limits
    """

    def __init__(self):
        """Initialize parameter extractor."""
        self.settings = get_settings()
        self._load_patterns()

    def _load_patterns(self) -> None:
        """Load extraction patterns from few-shot examples."""
        few_shot_path = Path(self.settings.few_shot_examples_path)

        if few_shot_path.exists():
            with open(few_shot_path, 'r') as f:
                data = json.load(f)
                self.date_patterns = data.get("parameter_extraction_patterns", {}).get("date_patterns", [])
                self.aggregation_keywords = data.get("parameter_extraction_patterns", {}).get("aggregation_keywords", {})
        else:
            self.date_patterns = []
            self.aggregation_keywords = {}

    def extract_parameters(
        self,
        user_query: str,
        template_id: str
    ) -> Dict[str, Any]:
        """
        Extract parameters from user query for a specific template.

        Args:
            user_query: Natural language query
            template_id: Selected template ID

        Returns:
            Dictionary of extracted parameters
        """
        parameters = {}

        # Extract dates
        start_date, end_date = self._extract_dates(user_query)
        if start_date:
            parameters["start_date"] = start_date
        if end_date:
            parameters["end_date"] = end_date

        # Extract aggregation type
        aggregation = self._extract_aggregation(user_query)
        if aggregation:
            parameters["aggregation"] = aggregation

        # Extract ordering preference
        order_by = self._extract_order_by(user_query)
        if order_by:
            parameters["order_by"] = order_by

        # Extract limit (top N)
        limit = self._extract_limit(user_query)
        if limit:
            parameters["limit"] = limit

        return parameters

    def _extract_dates(self, user_query: str) -> tuple[Optional[str], Optional[str]]:
        """
        Extract date range from query.

        Args:
            user_query: Natural language query

        Returns:
            Tuple of (start_date, end_date) as ISO strings
        """
        query_lower = user_query.lower()
        today = datetime.now().date()

        # Relative date patterns

        # Check for "last year" modifier first (before other patterns)
        year_offset = 0
        if "last year" in query_lower or "previous year" in query_lower:
            year_offset = -1
        elif "two years ago" in query_lower or "2 years ago" in query_lower:
            year_offset = -2

        if "yesterday" in query_lower:
            date = (today - timedelta(days=1)).replace(year=today.year + year_offset)
            return date.isoformat(), date.isoformat()

        if "last week" in query_lower or "past week" in query_lower:
            reference_date = today.replace(year=today.year + year_offset) if year_offset else today
            end_date = reference_date.isoformat()
            start_date = (reference_date - timedelta(days=7)).isoformat()
            return start_date, end_date

        if "this week" in query_lower:
            # Start of week (Monday)
            reference_date = today.replace(year=today.year + year_offset) if year_offset else today
            start_of_week = reference_date - timedelta(days=reference_date.weekday())
            return start_of_week.isoformat(), reference_date.isoformat()

        if "last month" in query_lower:
            # Previous month
            reference_date = today.replace(year=today.year + year_offset) if year_offset else today
            first_of_this_month = reference_date.replace(day=1)
            last_of_prev_month = first_of_this_month - timedelta(days=1)
            first_of_prev_month = last_of_prev_month.replace(day=1)
            return first_of_prev_month.isoformat(), last_of_prev_month.isoformat()

        if "this month" in query_lower:
            reference_date = today.replace(year=today.year + year_offset) if year_offset else today
            first_of_month = reference_date.replace(day=1)
            return first_of_month.isoformat(), reference_date.isoformat()

        if "this year" in query_lower:
            reference_date = today.replace(year=today.year + year_offset) if year_offset else today
            first_of_year = reference_date.replace(month=1, day=1)
            return first_of_year.isoformat(), reference_date.isoformat()

        # Look for specific date patterns (e.g., "October 1 to October 15")
        date_range = self._extract_specific_dates(user_query)
        if date_range:
            return date_range

        # Default: last 30 days
        default_start = (today - timedelta(days=30)).isoformat()
        default_end = today.isoformat()
        return default_start, default_end

    def _extract_specific_dates(self, user_query: str) -> Optional[tuple[str, str]]:
        """
        Extract specific dates from patterns like 'October 1 to October 15'.

        Args:
            user_query: Natural language query

        Returns:
            Tuple of (start_date, end_date) or None
        """
        # Pattern: "Month Day to Month Day"
        pattern = r'(\w+)\s+(\d+)\s+to\s+(\w+)\s+(\d+)'
        match = re.search(pattern, user_query, re.IGNORECASE)

        if match:
            start_month, start_day, end_month, end_day = match.groups()
            year = datetime.now().year

            try:
                start_date = datetime.strptime(f"{start_month} {start_day} {year}", "%B %d %Y").date()
                end_date = datetime.strptime(f"{end_month} {end_day} {year}", "%B %d %Y").date()
                return start_date.isoformat(), end_date.isoformat()
            except ValueError:
                pass

        # Pattern: "YYYY-MM-DD to YYYY-MM-DD"
        iso_pattern = r'(\d{4}-\d{2}-\d{2})\s+to\s+(\d{4}-\d{2}-\d{2})'
        match = re.search(iso_pattern, user_query)
        if match:
            return match.group(1), match.group(2)

        return None

    def _extract_aggregation(self, user_query: str) -> Optional[str]:
        """
        Extract aggregation type from query.

        Args:
            user_query: Natural language query

        Returns:
            Aggregation type (SUM, AVG, COUNT, etc.) or None
        """
        query_lower = user_query.lower()

        for keyword, agg_type in self.aggregation_keywords.items():
            if keyword in query_lower:
                return agg_type.upper()

        # Additional patterns
        if any(word in query_lower for word in ["total", "sum"]):
            return "SUM"
        if any(word in query_lower for word in ["average", "avg", "mean"]):
            return "AVG"
        if any(word in query_lower for word in ["count", "number of", "how many"]):
            return "COUNT"
        if "max" in query_lower or "maximum" in query_lower or "highest" in query_lower:
            return "MAX"
        if "min" in query_lower or "minimum" in query_lower or "lowest" in query_lower:
            return "MIN"

        return None

    def _extract_order_by(self, user_query: str) -> Optional[str]:
        """
        Extract ordering preference from query.

        Args:
            user_query: Natural language query

        Returns:
            Order by field or None
        """
        query_lower = user_query.lower()

        if any(word in query_lower for word in ["revenue", "sales", "money", "dollars"]):
            return "total_revenue"
        if any(word in query_lower for word in ["quantity", "units", "items"]):
            return "total_quantity"
        if "transaction" in query_lower:
            return "transaction_count"

        # Default for top/best queries
        if any(word in query_lower for word in ["top", "best", "highest"]):
            return "total_revenue"

        return None

    def _extract_limit(self, user_query: str) -> Optional[int]:
        """
        Extract limit (top N) from query.

        Args:
            user_query: Natural language query

        Returns:
            Limit number or None
        """
        # Look for "top N", "best N", etc.
        pattern = r'\b(?:top|best|first|leading)\s+(\d+)\b'
        match = re.search(pattern, user_query, re.IGNORECASE)

        if match:
            return int(match.group(1))

        # Default top queries to 5
        if any(word in user_query.lower() for word in ["top", "best"]):
            return 5

        return None


# Global parameter extractor instance
_parameter_extractor: Optional[ParameterExtractor] = None


def get_parameter_extractor() -> ParameterExtractor:
    """
    Get or create the global parameter extractor.

    Returns:
        ParameterExtractor instance
    """
    global _parameter_extractor
    if _parameter_extractor is None:
        _parameter_extractor = ParameterExtractor()
    return _parameter_extractor
