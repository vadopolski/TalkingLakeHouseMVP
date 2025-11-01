"""
LLM pipeline orchestrator for query processing.

Pipeline flow: classify → pick template → extract params → validate → execute → format response

Constitutional Principle V: LLM role is strictly limited to template selection
and parameter extraction. No SQL structure modification.
"""

from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass

from src.database.query_executor import get_query_executor
from src.validation.parameter_validator import get_parameter_validator
from src.middleware.rate_limiter import get_rate_limiter
from src.logging.audit_logger import get_audit_logger
from config.settings import get_settings


@dataclass
class QueryResponse:
    """Response from query pipeline."""
    success: bool
    data: Optional[List[Dict[str, Any]]] = None
    text_response: Optional[str] = None
    chart_data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    template_id: Optional[str] = None
    execution_time_ms: Optional[float] = None


class QueryPipeline:
    """
    Orchestrates the complete query processing pipeline.

    Steps:
    1. Rate limiting check
    2. Intent classification (sales, traffic, conversion)
    3. Template selection
    4. Parameter extraction
    5. Parameter validation
    6. SQL execution
    7. Response formatting (text + chart)
    """

    def __init__(self):
        """Initialize query pipeline."""
        self.settings = get_settings()
        self.query_executor = get_query_executor()
        self.parameter_validator = get_parameter_validator()
        self.rate_limiter = get_rate_limiter()
        self.audit_logger = get_audit_logger()

    def process_query(
        self,
        user_query: str,
        user_id: str = "default_user"
    ) -> QueryResponse:
        """
        Process a natural language query through the complete pipeline.

        Args:
            user_query: Natural language question from user
            user_id: User identifier for rate limiting and audit

        Returns:
            QueryResponse with results or error
        """
        # Step 1: Rate limiting
        allowed, remaining, error = self.rate_limiter.is_allowed(user_id)
        if not allowed:
            return QueryResponse(
                success=False,
                error_message=error
            )

        # Step 2: Intent classification (placeholder - will be implemented in Phase 3)
        # For now, return a structured response indicating pipeline is ready
        intent = self._classify_intent(user_query)

        # Step 3: Template selection (placeholder - will be implemented in Phase 3)
        template_id, confidence = self._select_template(user_query, intent)

        if template_id is None:
            return QueryResponse(
                success=False,
                error_message=(
                    "I don't have a template to answer that question yet. "
                    "I can help with: sales queries, traffic analysis, and conversion metrics."
                )
            )

        # Log template selection
        self.audit_logger.log_template_selection(
            user_query=user_query,
            template_id=template_id,
            confidence_score=confidence,
            user_id=user_id
        )

        # Step 4: Parameter extraction (placeholder - will be implemented in Phase 3)
        parameters = self._extract_parameters(user_query, template_id)

        # Step 5: Load template and validate parameters (placeholder)
        template = self._load_template(template_id)
        if not template:
            return QueryResponse(
                success=False,
                error_message=f"Template '{template_id}' not found"
            )

        # Validate parameters
        valid, error, sanitized_params = self.parameter_validator.validate_parameters(
            parameters=parameters,
            parameter_definitions=template.get("parameters", [])
        )

        if not valid:
            self.audit_logger.log_validation_failure(
                user_query=user_query,
                validation_type="parameter_validation",
                reason=error,
                user_id=user_id
            )
            return QueryResponse(
                success=False,
                error_message=f"Parameter validation failed: {error}"
            )

        # Step 6: Execute query
        sql = template.get("sql_structure", "")
        sql = self._substitute_parameters(sql, sanitized_params)

        success, results, error = self.query_executor.execute_query(
            sql=sql,
            parameters=sanitized_params,
            allowed_tables=template.get("whitelisted_tables", []),
            allowed_columns=template.get("whitelisted_columns", []),
            timeout_seconds=template.get("timeout_seconds"),
            user_id=user_id,
            user_query=user_query,
            template_id=template_id
        )

        if not success:
            return QueryResponse(
                success=False,
                error_message=error,
                template_id=template_id
            )

        # Step 7: Format response (placeholder - will be enhanced in Phase 3)
        text_response = self._format_text_response(results, template)
        chart_data = self._format_chart_data(results, template)

        return QueryResponse(
            success=True,
            data=results,
            text_response=text_response,
            chart_data=chart_data,
            template_id=template_id
        )

    def _classify_intent(self, user_query: str) -> str:
        """
        Classify user query intent (sales, traffic, conversion).

        Placeholder - will be enhanced with LLM in Phase 3.

        Args:
            user_query: Natural language query

        Returns:
            Intent category (sales, traffic, conversion, unknown)
        """
        query_lower = user_query.lower()

        # Simple keyword matching for now
        sales_keywords = ["sales", "revenue", "products", "transactions", "purchases"]
        traffic_keywords = ["visitors", "visits", "traffic", "sessions"]
        conversion_keywords = ["conversion", "rate", "business", "performance"]

        if any(kw in query_lower for kw in sales_keywords):
            return "sales"
        elif any(kw in query_lower for kw in traffic_keywords):
            return "traffic"
        elif any(kw in query_lower for kw in conversion_keywords):
            return "conversion"
        else:
            return "unknown"

    def _select_template(self, user_query: str, intent: str) -> Tuple[Optional[str], float]:
        """
        Select appropriate SQL template based on user query.

        Placeholder - will be enhanced with LLM and few-shot examples in Phase 3.

        Args:
            user_query: Natural language query
            intent: Query intent (sales, traffic, conversion)

        Returns:
            Tuple of (template_id, confidence_score)
        """
        # Placeholder: Return None to indicate template selection not yet implemented
        # Phase 3 will implement actual template selection logic
        return None, 0.0

    def _extract_parameters(self, user_query: str, template_id: str) -> Dict[str, Any]:
        """
        Extract parameters from natural language query.

        Placeholder - will be enhanced with LLM in Phase 3.

        Args:
            user_query: Natural language query
            template_id: Selected template ID

        Returns:
            Dictionary of extracted parameters
        """
        # Placeholder: Return empty dict
        # Phase 3 will implement actual parameter extraction
        return {}

    def _load_template(self, template_id: str) -> Optional[Dict[str, Any]]:
        """
        Load SQL template by ID.

        Placeholder - will be implemented with TemplateLoader in T015.

        Args:
            template_id: Template identifier

        Returns:
            Template dictionary or None
        """
        # Placeholder: Return None until TemplateLoader is implemented
        return None

    def _substitute_parameters(self, sql: str, parameters: Dict[str, Any]) -> str:
        """
        Substitute parameters into SQL template.

        Args:
            sql: SQL template with placeholders
            parameters: Parameter values

        Returns:
            SQL with substituted parameters
        """
        for key, value in parameters.items():
            placeholder = f"{{{key}}}"
            if isinstance(value, str):
                sql = sql.replace(placeholder, f"'{value}'")
            else:
                sql = sql.replace(placeholder, str(value))
        return sql

    def _format_text_response(
        self,
        results: List[Dict[str, Any]],
        template: Dict[str, Any]
    ) -> str:
        """
        Format query results as natural language text.

        Placeholder - will be enhanced with TextFormatter in Phase 3.

        Args:
            results: Query results
            template: Template metadata

        Returns:
            Natural language summary
        """
        if not results:
            return "No data found for your query."

        row_count = len(results)
        return f"Found {row_count} result(s)."

    def _format_chart_data(
        self,
        results: List[Dict[str, Any]],
        template: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Format query results for chart visualization.

        Placeholder - will be enhanced with ChartSelector in Phase 3.

        Args:
            results: Query results
            template: Template metadata

        Returns:
            Chart data dictionary or None
        """
        chart_type = template.get("chart_type", "none")

        if chart_type == "none" or not results:
            return None

        return {
            "chart_type": chart_type,
            "data": results
        }


# Global pipeline instance
_query_pipeline: Optional[QueryPipeline] = None


def get_query_pipeline() -> QueryPipeline:
    """
    Get or create the global query pipeline.

    Returns:
        QueryPipeline instance
    """
    global _query_pipeline
    if _query_pipeline is None:
        _query_pipeline = QueryPipeline()
    return _query_pipeline
