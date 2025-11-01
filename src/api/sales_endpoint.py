"""
API endpoint for sales queries.

Handles POST /api/query/sales requests for natural language sales questions.
"""

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

from src.pipeline.query_pipeline import get_query_pipeline
from src.pipeline.intent_classifier import get_intent_classifier
from src.pipeline.template_selector import get_template_selector
from src.pipeline.parameter_extractor import get_parameter_extractor
from src.templates.template_loader import get_template_loader
from src.database.query_executor import get_query_executor
from src.visualization.chart_selector import get_chart_selector
from src.formatting.text_formatter import get_text_formatter
from src.formatting.citation_generator import get_citation_generator
from src.errors.sales_errors import get_sales_error_message
from src.logging.audit_logger import get_audit_logger


router = APIRouter(prefix="/api/query", tags=["query"])


class QueryRequest(BaseModel):
    """Request model for natural language queries."""
    query: str
    user_id: Optional[str] = "default_user"


class QueryResponse(BaseModel):
    """Response model for query results."""
    success: bool
    text_response: Optional[str] = None
    chart_data: Optional[Dict[str, Any]] = None
    citation: Optional[str] = None
    error: Optional[str] = None
    template_id: Optional[str] = None


@router.post("/sales", response_model=QueryResponse)
async def query_sales(request: QueryRequest):
    """
    Process natural language sales query.

    Args:
        request: Query request with user question

    Returns:
        QueryResponse with results or error
    """
    # Initialize components
    intent_classifier = get_intent_classifier()
    template_selector = get_template_selector()
    parameter_extractor = get_parameter_extractor()
    template_loader = get_template_loader()
    query_executor = get_query_executor()
    chart_selector = get_chart_selector()
    text_formatter = get_text_formatter()
    citation_generator = get_citation_generator()
    audit_logger = get_audit_logger()

    try:
        # Step 1: Classify intent
        intent, intent_confidence = intent_classifier.classify(request.query)

        # Ensure it's a sales query
        if intent != "sales":
            return QueryResponse(
                success=False,
                error=get_sales_error_message(
                    "template_not_found",
                    user_query=request.query
                )
            )

        # Step 2: Select template
        template_id, template_confidence, match_info = template_selector.select_template(
            request.query,
            intent
        )

        if not template_id:
            return QueryResponse(
                success=False,
                error=get_sales_error_message(
                    "template_not_found",
                    user_query=request.query
                )
            )

        # Log template selection
        audit_logger.log_template_selection(
            user_query=request.query,
            template_id=template_id,
            confidence_score=template_confidence,
            user_id=request.user_id
        )

        # Step 3: Load template
        template = template_loader.load_template(template_id)
        if not template:
            return QueryResponse(
                success=False,
                error="Template configuration error. Please try again."
            )

        # Step 4: Extract parameters
        parameters = parameter_extractor.extract_parameters(
            request.query,
            template_id
        )

        # Step 5: Fill SQL template
        sql = template.get("sql_structure", "")
        for key, value in parameters.items():
            placeholder = f"{{{key}}}"
            if isinstance(value, str):
                sql = sql.replace(placeholder, value)
            else:
                sql = sql.replace(placeholder, str(value))

        # Step 6: Execute query
        success, results, error = query_executor.execute_query(
            sql=sql,
            parameters=parameters,
            allowed_tables=template.get("whitelisted_tables", []),
            allowed_columns=template.get("whitelisted_columns", []),
            timeout_seconds=template.get("timeout_seconds"),
            user_id=request.user_id,
            user_query=request.query,
            template_id=template_id
        )

        if not success:
            return QueryResponse(
                success=False,
                error=error,
                template_id=template_id
            )

        # Step 7: Format response
        text_response = text_formatter.format_response(
            results=results,
            query_intent="sales",
            template_id=template_id
        )

        # Step 8: Generate chart
        chart_type = chart_selector.select_chart_type(
            results=results,
            suggested_type=template.get("chart_type"),
            query_intent="sales"
        )

        chart_data = None
        if chart_type != "none":
            chart_data = chart_selector.format_chart_data(results, chart_type)
            chart_data["type"] = chart_type

        # Step 9: Generate citation
        date_range = citation_generator.extract_date_range_from_parameters(parameters)
        citation_text = citation_generator.generate_citation(
            tables=template.get("whitelisted_tables", []),
            date_range=date_range,
            row_count=len(results),
            template_id=template_id
        )

        return QueryResponse(
            success=True,
            text_response=text_response,
            chart_data=chart_data,
            citation=citation_text,
            template_id=template_id
        )

    except Exception as e:
        # Log error
        audit_logger.log_system_event(
            event_type="sales_query_error",
            details={
                "user_query": request.query,
                "error": str(e),
                "user_id": request.user_id
            }
        )

        return QueryResponse(
            success=False,
            error=get_sales_error_message("generic")
        )


# Create main API router
def create_sales_router() -> APIRouter:
    """
    Create and configure sales API router.

    Returns:
        Configured APIRouter instance
    """
    return router
