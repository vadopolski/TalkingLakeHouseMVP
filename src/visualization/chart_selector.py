"""
Chart type selector based on data characteristics.

Constitutional Principle VII: Chart type selection based on data characteristics
and query intent. Supports bar, line, pie, scatter charts.
"""

from typing import Any, Dict, List, Optional


class ChartSelector:
    """
    Selects appropriate chart type based on query results and data characteristics.

    Chart type selection rules:
    - Time series data → line chart
    - Categorical comparison → bar chart
    - Distribution/proportions → pie chart
    - Correlation/scatter → scatter plot
    - Multi-metric → mixed chart
    """

    def select_chart_type(
        self,
        results: List[Dict[str, Any]],
        suggested_type: Optional[str] = None,
        query_intent: Optional[str] = None
    ) -> str:
        """
        Select appropriate chart type for data.

        Args:
            results: Query results
            suggested_type: Chart type suggested by template
            query_intent: Query intent (sales, traffic, conversion)

        Returns:
            Chart type (bar, line, pie, scatter, mixed, none)
        """
        if not results:
            return "none"

        # Use suggested type if provided and valid
        if suggested_type and suggested_type in ["bar", "line", "pie", "scatter", "mixed"]:
            return suggested_type

        # Analyze data characteristics
        data_analysis = self._analyze_data(results)

        # Selection logic based on data characteristics
        if data_analysis["has_date_field"] and data_analysis["row_count"] > 1:
            return "line"  # Time series data
        elif data_analysis["has_categorical_field"] and data_analysis["row_count"] <= 10:
            if data_analysis["has_percentage"] or query_intent == "traffic":
                return "pie"  # Distribution data
            else:
                return "bar"  # Categorical comparison
        elif data_analysis["numeric_field_count"] >= 2:
            return "scatter"  # Multiple numeric fields suggest correlation
        elif data_analysis["row_count"] > 1:
            return "bar"  # Default to bar chart
        else:
            return "none"  # Single row, no chart needed

    def _analyze_data(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze data characteristics.

        Args:
            results: Query results

        Returns:
            Dictionary with data characteristics
        """
        if not results:
            return {
                "row_count": 0,
                "column_count": 0,
                "has_date_field": False,
                "has_categorical_field": False,
                "has_percentage": False,
                "numeric_field_count": 0
            }

        first_row = results[0]
        columns = list(first_row.keys())

        # Detect field types
        has_date = any("date" in col.lower() or "time" in col.lower() for col in columns)
        has_categorical = any(
            isinstance(first_row[col], str) for col in columns
            if "date" not in col.lower() and "time" not in col.lower()
        )
        has_percentage = any("percent" in col.lower() or "rate" in col.lower() for col in columns)
        numeric_count = sum(
            1 for col in columns
            if isinstance(first_row[col], (int, float))
        )

        return {
            "row_count": len(results),
            "column_count": len(columns),
            "has_date_field": has_date,
            "has_categorical_field": has_categorical,
            "has_percentage": has_percentage,
            "numeric_field_count": numeric_count
        }

    def format_chart_data(
        self,
        results: List[Dict[str, Any]],
        chart_type: str
    ) -> Dict[str, Any]:
        """
        Format query results for chart rendering.

        Args:
            results: Query results
            chart_type: Selected chart type

        Returns:
            Chart data formatted for frontend
        """
        if not results or chart_type == "none":
            return {"type": "none", "data": []}

        # Extract labels and values based on chart type
        if chart_type in ["bar", "line"]:
            return self._format_bar_line_chart(results)
        elif chart_type == "pie":
            return self._format_pie_chart(results)
        elif chart_type == "scatter":
            return self._format_scatter_chart(results)
        else:
            return {"type": chart_type, "data": results}

    def _format_bar_line_chart(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Format data for bar or line chart."""
        # Assume first column is label/x-axis, remaining are values/y-axis
        labels = []
        datasets = []

        if not results:
            return {"labels": [], "datasets": []}

        first_row = results[0]
        columns = list(first_row.keys())

        # First column as labels (typically date or category)
        label_col = columns[0]
        labels = [row[label_col] for row in results]

        # Remaining columns as datasets
        for col in columns[1:]:
            datasets.append({
                "label": col,
                "data": [row[col] for row in results]
            })

        return {
            "labels": labels,
            "datasets": datasets
        }

    def _format_pie_chart(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Format data for pie chart."""
        if not results:
            return {"labels": [], "data": []}

        first_row = results[0]
        columns = list(first_row.keys())

        # First column as labels, second as values
        label_col = columns[0]
        value_col = columns[1] if len(columns) > 1 else columns[0]

        labels = [row[label_col] for row in results]
        data = [row[value_col] for row in results]

        return {
            "labels": labels,
            "data": data
        }

    def _format_scatter_chart(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Format data for scatter chart."""
        if not results:
            return {"data": []}

        first_row = results[0]
        columns = list(first_row.keys())

        # Use first two numeric columns as x and y
        numeric_cols = [
            col for col in columns
            if isinstance(first_row[col], (int, float))
        ]

        if len(numeric_cols) < 2:
            return {"data": []}

        x_col = numeric_cols[0]
        y_col = numeric_cols[1]

        data = [
            {"x": row[x_col], "y": row[y_col]}
            for row in results
        ]

        return {
            "x_label": x_col,
            "y_label": y_col,
            "data": data
        }


# Global chart selector instance
_chart_selector: Optional[ChartSelector] = None


def get_chart_selector() -> ChartSelector:
    """
    Get or create the global chart selector.

    Returns:
        ChartSelector instance
    """
    global _chart_selector
    if _chart_selector is None:
        _chart_selector = ChartSelector()
    return _chart_selector
