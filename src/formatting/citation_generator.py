"""
Data source citation generator.

Constitutional Principle VII: System must include data source citation
(table names, date range) in every response.
"""

from typing import Any, Dict, List, Optional
from datetime import datetime


class CitationGenerator:
    """
    Generates data source citations for query responses.

    Citations include:
    - Source tables queried
    - Date range of data
    - Timestamp of query execution
    - Row count returned
    """

    def generate_citation(
        self,
        tables: List[str],
        date_range: Optional[tuple[str, str]] = None,
        row_count: Optional[int] = None,
        template_id: Optional[str] = None
    ) -> str:
        """
        Generate a data source citation.

        Args:
            tables: List of tables queried
            date_range: Tuple of (start_date, end_date) if applicable
            row_count: Number of rows returned
            template_id: Template ID used for query

        Returns:
            Citation string
        """
        citation_parts = []

        # Source tables
        if tables:
            table_str = ", ".join(tables)
            citation_parts.append(f"Source: {table_str}")

        # Date range
        if date_range:
            start, end = date_range
            if start == end:
                citation_parts.append(f"Date: {start}")
            else:
                citation_parts.append(f"Date range: {start} to {end}")

        # Row count
        if row_count is not None:
            citation_parts.append(f"{row_count} record(s)")

        # Query timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        citation_parts.append(f"Retrieved: {timestamp}")

        return " | ".join(citation_parts)

    def generate_full_citation(
        self,
        query_metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate full citation with all metadata.

        Args:
            query_metadata: Dictionary containing query metadata

        Returns:
            Citation dictionary with structured data
        """
        return {
            "source_tables": query_metadata.get("tables", []),
            "date_range": {
                "start": query_metadata.get("start_date"),
                "end": query_metadata.get("end_date")
            },
            "row_count": query_metadata.get("row_count"),
            "template_id": query_metadata.get("template_id"),
            "query_timestamp": datetime.now().isoformat(),
            "citation_text": self.generate_citation(
                tables=query_metadata.get("tables", []),
                date_range=(
                    query_metadata.get("start_date"),
                    query_metadata.get("end_date")
                ) if query_metadata.get("start_date") else None,
                row_count=query_metadata.get("row_count"),
                template_id=query_metadata.get("template_id")
            )
        }

    def extract_date_range_from_parameters(
        self,
        parameters: Dict[str, Any]
    ) -> Optional[tuple[str, str]]:
        """
        Extract date range from query parameters.

        Args:
            parameters: Query parameters

        Returns:
            Tuple of (start_date, end_date) or None
        """
        start_date = parameters.get("start_date")
        end_date = parameters.get("end_date")

        if start_date and end_date:
            # Convert to string if datetime objects
            if isinstance(start_date, datetime):
                start_date = start_date.strftime("%Y-%m-%d")
            if isinstance(end_date, datetime):
                end_date = end_date.strftime("%Y-%m-%d")

            return (str(start_date), str(end_date))

        return None

    def format_citation_for_display(
        self,
        citation: Dict[str, Any],
        include_metadata: bool = False
    ) -> str:
        """
        Format citation for user display.

        Args:
            citation: Citation dictionary
            include_metadata: Whether to include technical metadata

        Returns:
            Formatted citation string
        """
        parts = []

        # Always include source tables
        tables = citation.get("source_tables", [])
        if tables:
            parts.append(f"📊 Data from: {', '.join(tables)}")

        # Date range if available
        date_range = citation.get("date_range", {})
        if date_range.get("start") and date_range.get("end"):
            start = date_range["start"]
            end = date_range["end"]
            if start == end:
                parts.append(f"📅 Date: {start}")
            else:
                parts.append(f"📅 {start} to {end}")

        # Row count
        row_count = citation.get("row_count")
        if row_count is not None:
            parts.append(f"📈 {row_count} record(s)")

        # Metadata for technical users
        if include_metadata:
            template_id = citation.get("template_id")
            if template_id:
                parts.append(f"Template: {template_id}")

            timestamp = citation.get("query_timestamp")
            if timestamp:
                parts.append(f"Retrieved: {timestamp}")

        return "\n".join(parts)


# Global citation generator instance
_citation_generator: Optional[CitationGenerator] = None


def get_citation_generator() -> CitationGenerator:
    """
    Get or create the global citation generator.

    Returns:
        CitationGenerator instance
    """
    global _citation_generator
    if _citation_generator is None:
        _citation_generator = CitationGenerator()
    return _citation_generator
