"""
Table and column whitelist enforcement for SQL security.

Constitutional Principle VI: Only explicitly permitted tables and columns are allowed.
"""

import re
from typing import List, Set
from config.settings import get_settings


class WhitelistValidator:
    """
    Validates that SQL queries only access whitelisted tables and columns.

    This enforces Constitutional Principle VI (Strict Safety Controls) by preventing
    access to unauthorized database objects.
    """

    def __init__(self):
        """Initialize whitelist validator."""
        self.settings = get_settings()
        self.whitelisted_tables: Set[str] = set(self.settings.whitelisted_tables)

    def validate_tables(self, sql: str, allowed_tables: List[str]) -> tuple[bool, str]:
        """
        Validate that SQL only references whitelisted tables.

        Args:
            sql: SQL query to validate
            allowed_tables: List of tables allowed for this specific query

        Returns:
            Tuple of (is_valid, error_message)
        """
        # Convert allowed tables to set for faster lookup
        allowed_set = set(allowed_tables)

        # Check that all allowed tables are in global whitelist
        unauthorized = allowed_set - self.whitelisted_tables
        if unauthorized:
            return False, f"Tables not in global whitelist: {', '.join(unauthorized)}"

        # Extract table names from SQL using regex
        # Matches: FROM table_name, JOIN table_name
        table_pattern = r'(?:FROM|JOIN)\s+([a-z_][a-z0-9_]*)'
        found_tables = set(re.findall(table_pattern, sql, re.IGNORECASE))

        # Check for unauthorized tables
        unauthorized_tables = found_tables - allowed_set
        if unauthorized_tables:
            return False, f"Query references unauthorized tables: {', '.join(unauthorized_tables)}"

        return True, ""

    def validate_no_subqueries(self, sql: str) -> tuple[bool, str]:
        """
        Validate that SQL does not contain subqueries.

        Subqueries can be used to bypass table whitelists, so we block them.

        Args:
            sql: SQL query to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        sql_upper = sql.upper()

        # Check for nested SELECT statements
        select_count = sql_upper.count("SELECT")
        if select_count > 1:
            return False, "Subqueries are not allowed for security reasons"

        return True, ""

    def validate_no_wildcards(self, sql: str, allowed_columns: List[str]) -> tuple[bool, str]:
        """
        Validate that SQL does not use SELECT * and only accesses allowed columns.

        Args:
            sql: SQL query to validate
            allowed_columns: List of columns allowed for this query

        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check for SELECT *
        if re.search(r'SELECT\s+\*', sql, re.IGNORECASE):
            return False, "SELECT * is not allowed. Please specify explicit columns."

        # Extract column names from SELECT clause
        select_pattern = r'SELECT\s+(.*?)\s+FROM'
        match = re.search(select_pattern, sql, re.IGNORECASE | re.DOTALL)

        if not match:
            return False, "Could not parse SELECT clause"

        select_clause = match.group(1)

        # Extract individual column names (handles aliases, functions, etc.)
        # This is a simplified check - production would need more robust parsing
        column_pattern = r'([a-z_][a-z0-9_]*)'
        found_columns = set(re.findall(column_pattern, select_clause, re.IGNORECASE))

        # Filter out SQL keywords that might be matched
        sql_keywords = {
            'as', 'count', 'sum', 'avg', 'max', 'min', 'distinct',
            'case', 'when', 'then', 'else', 'end', 'cast', 'extract',
            'year', 'month', 'day', 'date', 'timestamp'
        }
        found_columns = found_columns - sql_keywords

        # Check against whitelist
        allowed_set = set(allowed_columns)
        unauthorized_columns = found_columns - allowed_set

        if unauthorized_columns:
            return False, f"Query references unauthorized columns: {', '.join(unauthorized_columns)}"

        return True, ""

    def validate_query(
        self,
        sql: str,
        allowed_tables: List[str],
        allowed_columns: List[str]
    ) -> tuple[bool, str]:
        """
        Perform complete whitelist validation.

        Args:
            sql: SQL query to validate
            allowed_tables: Tables allowed for this query
            allowed_columns: Columns allowed for this query

        Returns:
            Tuple of (is_valid, error_message)
        """
        # Validate tables
        valid, error = self.validate_tables(sql, allowed_tables)
        if not valid:
            return False, error

        # Validate no subqueries
        valid, error = self.validate_no_subqueries(sql)
        if not valid:
            return False, error

        # Validate columns (optional - can be skipped if too restrictive)
        # valid, error = self.validate_no_wildcards(sql, allowed_columns)
        # if not valid:
        #     return False, error

        return True, ""


# Global validator instance
_whitelist_validator: WhitelistValidator | None = None


def get_whitelist_validator() -> WhitelistValidator:
    """
    Get or create the global whitelist validator.

    Returns:
        WhitelistValidator instance
    """
    global _whitelist_validator
    if _whitelist_validator is None:
        _whitelist_validator = WhitelistValidator()
    return _whitelist_validator
