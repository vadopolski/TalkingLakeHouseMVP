"""
SQL keyword blocker for risky operations.

Constitutional Principle VI: Block DROP, DELETE, UPDATE, INSERT, and other
dangerous SQL keywords to prevent data modification.
"""

import re
from typing import List, Set
from config.settings import get_settings


class SQLValidator:
    """
    Validates SQL queries to block risky operations.

    Enforces Constitutional Principle VI by preventing:
    - Data modification (INSERT, UPDATE, DELETE)
    - Schema changes (DROP, ALTER, CREATE)
    - Permission changes (GRANT, REVOKE)
    - Execution of stored procedures
    """

    def __init__(self):
        """Initialize SQL validator."""
        self.settings = get_settings()
        self.blocked_keywords: Set[str] = set(
            keyword.upper() for keyword in self.settings.blocked_keywords
        )

    def validate_no_blocked_keywords(self, sql: str) -> tuple[bool, str]:
        """
        Validate that SQL does not contain blocked keywords.

        Args:
            sql: SQL query to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        sql_upper = sql.upper()

        # Check for blocked keywords
        found_keywords = []
        for keyword in self.blocked_keywords:
            # Use word boundaries to avoid false positives
            # e.g., "DESCRIPTION" should not match "DELETE"
            pattern = r'\b' + re.escape(keyword) + r'\b'
            if re.search(pattern, sql_upper):
                found_keywords.append(keyword)

        if found_keywords:
            return False, f"Blocked SQL keywords detected: {', '.join(found_keywords)}. Only SELECT queries are allowed."

        return True, ""

    def validate_select_only(self, sql: str) -> tuple[bool, str]:
        """
        Validate that SQL is a SELECT statement.

        Args:
            sql: SQL query to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        sql_stripped = sql.strip().upper()

        if not sql_stripped.startswith("SELECT"):
            return False, "Only SELECT queries are allowed. This query does not start with SELECT."

        return True, ""

    def validate_no_comments(self, sql: str) -> tuple[bool, str]:
        """
        Validate that SQL does not contain comments.

        Comments can be used to hide malicious SQL, so we block them.

        Args:
            sql: SQL query to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check for SQL comments (-- and /* */)
        if '--' in sql:
            return False, "SQL comments (--) are not allowed"

        if '/*' in sql or '*/' in sql:
            return False, "SQL comments (/* */) are not allowed"

        return True, ""

    def validate_no_semicolons(self, sql: str) -> tuple[bool, str]:
        """
        Validate that SQL does not contain multiple statements.

        Semicolons allow SQL injection via statement chaining.

        Args:
            sql: SQL query to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        # Remove trailing semicolon (allowed)
        sql_trimmed = sql.rstrip().rstrip(';')

        # Check for additional semicolons
        if ';' in sql_trimmed:
            return False, "Multiple SQL statements are not allowed (semicolon detected)"

        return True, ""

    def validate_no_unions(self, sql: str) -> tuple[bool, str]:
        """
        Validate that SQL does not use UNION.

        UNION can be used to extract data from unauthorized tables.

        Args:
            sql: SQL query to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        sql_upper = sql.upper()

        if ' UNION ' in sql_upper or ' UNION ALL ' in sql_upper:
            return False, "UNION operations are not allowed for security reasons"

        return True, ""

    def validate_query(self, sql: str) -> tuple[bool, str]:
        """
        Perform complete SQL security validation.

        Args:
            sql: SQL query to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check 1: Must be SELECT only
        valid, error = self.validate_select_only(sql)
        if not valid:
            return False, error

        # Check 2: No blocked keywords
        valid, error = self.validate_no_blocked_keywords(sql)
        if not valid:
            return False, error

        # Check 3: No comments
        valid, error = self.validate_no_comments(sql)
        if not valid:
            return False, error

        # Check 4: No semicolons (except trailing)
        valid, error = self.validate_no_semicolons(sql)
        if not valid:
            return False, error

        # Check 5: No UNION operations
        valid, error = self.validate_no_unions(sql)
        if not valid:
            return False, error

        return True, ""


# Global validator instance
_sql_validator: SQLValidator | None = None


def get_sql_validator() -> SQLValidator:
    """
    Get or create the global SQL validator.

    Returns:
        SQLValidator instance
    """
    global _sql_validator
    if _sql_validator is None:
        _sql_validator = SQLValidator()
    return _sql_validator
