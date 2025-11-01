"""
Text response formatter for natural language summaries.

Constitutional Principle VII: Text outputs structured as natural language
summaries with clear data presentation.
"""

from typing import Any, Dict, List, Optional
from datetime import datetime


class TextFormatter:
    """
    Formats query results as natural language text responses.

    Creates user-friendly summaries that:
    - Use clear, conversational language
    - Highlight key metrics and insights
    - Present data in readable format
    - Avoid technical jargon
    """

    def format_response(
        self,
        results: List[Dict[str, Any]],
        query_intent: str,
        template_id: Optional[str] = None
    ) -> str:
        """
        Format query results as natural language text.

        Args:
            results: Query results
            query_intent: Intent category (sales, traffic, conversion)
            template_id: Template ID for context

        Returns:
            Natural language summary
        """
        if not results:
            return "No data found for your query. Try a different time period or question."

        # Route to specific formatter based on intent
        if query_intent == "sales":
            return self._format_sales_response(results, template_id)
        elif query_intent == "traffic":
            return self._format_traffic_response(results, template_id)
        elif query_intent == "conversion":
            return self._format_conversion_response(results, template_id)
        else:
            return self._format_generic_response(results)

    def _format_sales_response(
        self,
        results: List[Dict[str, Any]],
        template_id: Optional[str]
    ) -> str:
        """Format sales query results."""
        row_count = len(results)

        if template_id == "sales_by_date_range":
            # Calculate total revenue
            total_revenue = sum(row.get("revenue", 0) for row in results)
            return (
                f"Total sales: ${total_revenue:,.2f} across {row_count} day(s). "
                f"Average daily revenue: ${total_revenue / row_count:,.2f}."
            )

        elif template_id == "top_products":
            # List top products
            top_products = results[:5]  # Top 5
            product_list = [
                f"{i+1}. {row.get('product_name', 'Unknown')} (${row.get('revenue', 0):,.2f})"
                for i, row in enumerate(top_products)
            ]
            return "Top selling products:\n" + "\n".join(product_list)

        elif template_id == "sales_aggregation":
            # Single aggregated value
            if row_count == 1:
                value = list(results[0].values())[0]
                return f"Total: ${value:,.2f}"

        # Generic sales response
        return f"Found {row_count} sales record(s)."

    def _format_traffic_response(
        self,
        results: List[Dict[str, Any]],
        template_id: Optional[str]
    ) -> str:
        """Format traffic query results."""
        row_count = len(results)

        if template_id == "visitors_by_date_range":
            # Calculate total visitors
            total_visitors = sum(row.get("visitor_count", 0) for row in results)
            return (
                f"Total visitors: {total_visitors:,} across {row_count} day(s). "
                f"Average daily visitors: {total_visitors / row_count:,.0f}."
            )

        elif template_id == "peak_traffic_times":
            # Show peak hour/day
            if results:
                peak = max(results, key=lambda x: x.get("visitor_count", 0))
                peak_time = peak.get("hour") or peak.get("day_of_week") or "Unknown"
                peak_count = peak.get("visitor_count", 0)
                return f"Peak traffic occurs at {peak_time} with {peak_count:,} visitors."

        elif template_id == "visitor_sources":
            # List top sources
            top_sources = results[:5]
            source_list = [
                f"{i+1}. {row.get('source', 'Unknown')} ({row.get('visitor_count', 0):,} visitors)"
                for i, row in enumerate(top_sources)
            ]
            return "Top traffic sources:\n" + "\n".join(source_list)

        elif template_id == "traffic_comparison":
            # Compare two periods
            if row_count >= 2:
                current = results[0].get("visitor_count", 0)
                previous = results[1].get("visitor_count", 0)
                change = ((current - previous) / previous * 100) if previous > 0 else 0
                direction = "increase" if change > 0 else "decrease"
                return (
                    f"Current period: {current:,} visitors. "
                    f"Previous period: {previous:,} visitors. "
                    f"Change: {abs(change):.1f}% {direction}."
                )

        # Generic traffic response
        return f"Found {row_count} traffic record(s)."

    def _format_conversion_response(
        self,
        results: List[Dict[str, Any]],
        template_id: Optional[str]
    ) -> str:
        """Format conversion query results."""
        row_count = len(results)

        if template_id == "conversion_rate":
            # Show conversion rate
            if results:
                rate = results[0].get("conversion_rate", 0)
                visitors = results[0].get("total_visitors", 0)
                purchases = results[0].get("total_purchases", 0)
                return (
                    f"Conversion rate: {rate:.2f}%. "
                    f"{purchases:,} purchases from {visitors:,} visitors."
                )

        elif template_id == "revenue_per_visitor":
            # Show revenue per visitor
            if results:
                rpv = results[0].get("revenue_per_visitor", 0)
                return f"Average revenue per visitor: ${rpv:.2f}"

        elif template_id == "best_conversion_days":
            # List best days
            top_days = results[:5]
            day_list = [
                f"{i+1}. {row.get('date', 'Unknown')} ({row.get('conversion_rate', 0):.2f}%)"
                for i, row in enumerate(top_days)
            ]
            return "Best conversion days:\n" + "\n".join(day_list)

        elif template_id == "business_summary":
            # Multi-metric summary
            if results:
                row = results[0]
                return (
                    f"Business Summary:\n"
                    f"- Total Sales: ${row.get('total_revenue', 0):,.2f}\n"
                    f"- Total Visitors: {row.get('total_visitors', 0):,}\n"
                    f"- Conversion Rate: {row.get('conversion_rate', 0):.2f}%\n"
                    f"- Revenue per Visitor: ${row.get('revenue_per_visitor', 0):.2f}"
                )

        # Generic conversion response
        return f"Found {row_count} conversion record(s)."

    def _format_generic_response(self, results: List[Dict[str, Any]]) -> str:
        """Format generic query results."""
        row_count = len(results)

        if row_count == 1:
            # Single row - show key-value pairs
            row = results[0]
            items = [f"{key}: {value}" for key, value in row.items()]
            return "Result: " + ", ".join(items)
        else:
            # Multiple rows - show count
            return f"Found {row_count} result(s)."


# Global text formatter instance
_text_formatter: Optional[TextFormatter] = None


def get_text_formatter() -> TextFormatter:
    """
    Get or create the global text formatter.

    Returns:
        TextFormatter instance
    """
    global _text_formatter
    if _text_formatter is None:
        _text_formatter = TextFormatter()
    return _text_formatter
