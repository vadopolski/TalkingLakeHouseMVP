"""
Sales-specific error messages for user-friendly error handling.

Constitutional Principle VII: Error messages are user-friendly and never
expose SQL, database schema, or system internals.
"""

from typing import Optional


class SalesErrorMessages:
    """
    Generates user-friendly error messages for sales query failures.

    Provides helpful suggestions and alternative actions.
    """

    @staticmethod
    def no_data_found(date_range: Optional[tuple[str, str]] = None) -> str:
        """
        Error message when no sales data found.

        Args:
            date_range: Optional date range queried

        Returns:
            User-friendly error message
        """
        if date_range:
            start, end = date_range
            return (
                f"No sales data found for {start} to {end}. "
                f"Try a different time period or check if there were any transactions during this time."
            )
        return (
            "No sales data found for your query. "
            "Try asking about a different time period or product."
        )

    @staticmethod
    def ambiguous_date(user_input: str) -> str:
        """
        Error message for ambiguous date references.

        Args:
            user_input: User's date input

        Returns:
            Clarification message
        """
        return (
            f"I'm not sure what date range you mean by '{user_input}'. "
            f"Try being more specific, like:\n"
            f"- 'last week'\n"
            f"- 'this month'\n"
            f"- 'October 1 to October 15'"
        )

    @staticmethod
    def invalid_product(product_name: str) -> str:
        """
        Error message for invalid product name.

        Args:
            product_name: Product name from query

        Returns:
            User-friendly error message
        """
        return (
            f"I couldn't find a product named '{product_name}'. "
            f"Check the spelling or try asking for 'top products' to see what's available."
        )

    @staticmethod
    def date_in_future() -> str:
        """
        Error message for queries about future dates.

        Returns:
            User-friendly error message
        """
        return (
            "I can't show sales data for future dates. "
            "Try asking about past or current periods."
        )

    @staticmethod
    def too_broad_query() -> str:
        """
        Error message for overly broad queries.

        Returns:
            User-friendly error message
        """
        return (
            "Your query might be too broad. "
            "Try narrowing it down with a specific time period or product category. "
            "For example: 'sales last month' or 'top 5 products this year'."
        )

    @staticmethod
    def rate_limit_exceeded(wait_seconds: int) -> str:
        """
        Error message for rate limit exceeded.

        Args:
            wait_seconds: Seconds to wait before next query

        Returns:
            User-friendly error message
        """
        return (
            f"You've asked too many questions in a short time. "
            f"Please wait {wait_seconds} seconds before trying again."
        )

    @staticmethod
    def query_timeout() -> str:
        """
        Error message for query timeout.

        Returns:
            User-friendly error message
        """
        return (
            "This query is taking too long to process. "
            "Try asking for a shorter time period or fewer products. "
            "For example, 'sales last week' instead of 'sales this year'."
        )

    @staticmethod
    def template_not_found(user_query: str) -> str:
        """
        Error message when no template matches query.

        Args:
            user_query: Original user query

        Returns:
            User-friendly error message with suggestions
        """
        return (
            f"I don't know how to answer '{user_query}' yet. "
            f"I can help you with questions like:\n"
            f"- 'What were sales last week?'\n"
            f"- 'Show me top selling products'\n"
            f"- 'Total revenue this month'\n"
            f"- 'Sales from October 1 to October 15'"
        )

    @staticmethod
    def parameter_validation_failed(parameter: str, reason: str) -> str:
        """
        Error message for parameter validation failure.

        Args:
            parameter: Parameter that failed validation
            reason: Validation failure reason

        Returns:
            User-friendly error message
        """
        # Don't expose technical parameter names
        friendly_params = {
            "start_date": "start date",
            "end_date": "end date",
            "product_id": "product name",
            "limit": "number of results"
        }

        friendly_name = friendly_params.get(parameter, "input")

        return (
            f"There's an issue with the {friendly_name} in your question. "
            f"{reason}. Please try rephrasing your question."
        )

    @staticmethod
    def generic_error() -> str:
        """
        Generic error message for unexpected failures.

        Returns:
            User-friendly error message
        """
        return (
            "Something went wrong while processing your question. "
            "Please try asking in a different way or contact support if the problem persists."
        )


def get_sales_error_message(
    error_type: str,
    **kwargs
) -> str:
    """
    Get appropriate sales error message.

    Args:
        error_type: Type of error
        **kwargs: Additional context for error message

    Returns:
        User-friendly error message
    """
    error_messages = SalesErrorMessages()

    error_map = {
        "no_data": error_messages.no_data_found,
        "ambiguous_date": error_messages.ambiguous_date,
        "invalid_product": error_messages.invalid_product,
        "future_date": error_messages.date_in_future,
        "too_broad": error_messages.too_broad_query,
        "rate_limit": error_messages.rate_limit_exceeded,
        "timeout": error_messages.query_timeout,
        "template_not_found": error_messages.template_not_found,
        "parameter_validation": error_messages.parameter_validation_failed,
        "generic": error_messages.generic_error
    }

    error_func = error_map.get(error_type, error_messages.generic_error)

    try:
        return error_func(**kwargs)
    except TypeError:
        # If kwargs don't match function signature, return generic error
        return error_messages.generic_error()
