"""
Query executor with timeout enforcement and LIMIT clause injection.

Constitutional Principle VI: Query timeout limits prevent long-running queries
from degrading performance. LIMIT clauses are mandatory for all SELECT queries.
"""

import re
import time
from typing import Any, Dict, List, Optional
from datetime import datetime

from src.database.connection_manager import get_connection_manager
from src.security.sql_validator import get_sql_validator
from src.security.whitelist_validator import get_whitelist_validator
from src.logging.audit_logger import get_audit_logger
from config.settings import get_settings


class QueryExecutor:
    """
    Executes SQL queries with comprehensive safety enforcement.

    Features:
    - Timeout enforcement
    - LIMIT clause injection
    - SQL validation (blocked keywords, SELECT-only)
    - Whitelist validation (tables, columns)
    - Audit logging
    - Performance tracking
    """

    def __init__(self):
        """Initialize query executor."""
        self.settings = get_settings()
        self.connection_manager = get_connection_manager()
        self.sql_validator = get_sql_validator()
        self.whitelist_validator = get_whitelist_validator()
        self.audit_logger = get_audit_logger()

    def inject_limit_clause(
        self,
        sql: str,
        limit: Optional[int] = None
    ) -> str:
        """
        Inject LIMIT clause into SQL query if not present.

        Args:
            sql: SQL query
            limit: Row limit (default from settings)

        Returns:
            SQL query with LIMIT clause
        """
        limit = limit or self.settings.default_row_limit
        max_limit = self.settings.max_row_limit

        # Ensure limit does not exceed maximum
        limit = min(limit, max_limit)

        # Check if LIMIT already exists
        if re.search(r'\bLIMIT\s+\d+', sql, re.IGNORECASE):
            # Extract existing limit
            match = re.search(r'\bLIMIT\s+(\d+)', sql, re.IGNORECASE)
            if match:
                existing_limit = int(match.group(1))
                # Ensure it doesn't exceed max
                if existing_limit > max_limit:
                    sql = re.sub(
                        r'\bLIMIT\s+\d+',
                        f'LIMIT {max_limit}',
                        sql,
                        flags=re.IGNORECASE
                    )
            return sql

        # Add LIMIT clause before any trailing semicolon
        sql = sql.rstrip().rstrip(';')
        return f"{sql} LIMIT {limit}"

    def execute_query(
        self,
        sql: str,
        parameters: Optional[Dict[str, Any]] = None,
        allowed_tables: Optional[List[str]] = None,
        allowed_columns: Optional[List[str]] = None,
        timeout_seconds: Optional[int] = None,
        user_id: Optional[str] = None,
        user_query: Optional[str] = None,
        template_id: Optional[str] = None
    ) -> tuple[bool, List[Dict[str, Any]], str]:
        """
        Execute SQL query with full safety validation.

        Args:
            sql: SQL query to execute
            parameters: Query parameters (already validated)
            allowed_tables: Whitelisted tables for this query
            allowed_columns: Whitelisted columns for this query
            timeout_seconds: Query timeout (default from settings)
            user_id: Optional user identifier for audit
            user_query: Original natural language query
            template_id: SQL template ID for audit

        Returns:
            Tuple of (success, results, error_message)
        """
        start_time = time.time()
        success = False
        results = []
        error_message = ""

        try:
            # Step 1: SQL keyword validation
            valid, error = self.sql_validator.validate_query(sql)
            if not valid:
                self.audit_logger.log_validation_failure(
                    user_query=user_query or sql,
                    validation_type="sql_keywords",
                    reason=error,
                    user_id=user_id
                )
                return False, [], error

            # Step 2: Whitelist validation
            if allowed_tables:
                valid, error = self.whitelist_validator.validate_tables(sql, allowed_tables)
                if not valid:
                    self.audit_logger.log_validation_failure(
                        user_query=user_query or sql,
                        validation_type="table_whitelist",
                        reason=error,
                        user_id=user_id
                    )
                    return False, [], error

            # Step 3: Inject LIMIT clause
            sql = self.inject_limit_clause(sql)

            # Step 4: Execute query with timeout
            timeout = timeout_seconds or self.settings.query_timeout_seconds

            results = self.connection_manager.execute_query(
                sql=sql,
                parameters=parameters,
                timeout_seconds=timeout
            )

            success = True
            execution_time_ms = (time.time() - start_time) * 1000

            # Log successful query
            self.audit_logger.log_query(
                user_query=user_query or sql,
                template_id=template_id,
                parameters=parameters,
                execution_time_ms=execution_time_ms,
                row_count=len(results),
                success=True,
                user_id=user_id
            )

            return True, results, ""

        except TimeoutError as e:
            error_message = f"Query timeout: {str(e)}"
            execution_time_ms = (time.time() - start_time) * 1000

            self.audit_logger.log_query(
                user_query=user_query or sql,
                template_id=template_id,
                parameters=parameters,
                execution_time_ms=execution_time_ms,
                row_count=0,
                success=False,
                error=error_message,
                user_id=user_id
            )

            return False, [], error_message

        except Exception as e:
            error_message = f"Query execution failed: {str(e)}"
            execution_time_ms = (time.time() - start_time) * 1000

            self.audit_logger.log_query(
                user_query=user_query or sql,
                template_id=template_id,
                parameters=parameters,
                execution_time_ms=execution_time_ms,
                row_count=0,
                success=False,
                error=error_message,
                user_id=user_id
            )

            return False, [], error_message


# Global executor instance
_query_executor: Optional[QueryExecutor] = None


def get_query_executor() -> QueryExecutor:
    """
    Get or create the global query executor.

    Returns:
        QueryExecutor instance
    """
    global _query_executor
    if _query_executor is None:
        _query_executor = QueryExecutor()
    return _query_executor
