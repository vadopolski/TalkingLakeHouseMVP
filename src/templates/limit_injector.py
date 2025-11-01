"""
LIMIT clause injector for SQL safety.

Constitutional Principle VI: All SELECT queries MUST include a LIMIT clause.
Prevents unbounded result sets and performance issues.
"""

import re
from typing import Optional

from config.settings import get_settings


class LimitInjector:
    """
    Injects or enforces LIMIT clauses in SQL queries.

    Ensures:
    - All SELECT queries have LIMIT clause
    - LIMIT does not exceed maximum allowed
    - Templates can specify custom limits
    """

    def __init__(self):
        """Initialize LIMIT injector."""
        self.settings = get_settings()
        self.default_limit = self.settings.default_row_limit
        self.max_limit = self.settings.max_row_limit

    def inject_limit(
        self,
        sql: str,
        requested_limit: Optional[int] = None,
        template_requires_limit: bool = True
    ) -> str:
        """
        Inject LIMIT clause into SQL query if not present.

        Args:
            sql: SQL query
            requested_limit: Requested limit (e.g., from template or user)
            template_requires_limit: Whether template requires LIMIT

        Returns:
            SQL with LIMIT clause
        """
        # Some aggregation queries don't need LIMIT
        if not template_requires_limit:
            return sql

        # Determine effective limit
        limit = requested_limit or self.default_limit
        limit = min(limit, self.max_limit)  # Enforce maximum

        # Check if LIMIT already exists
        if self._has_limit_clause(sql):
            # Validate and potentially replace existing LIMIT
            return self._replace_limit(sql, limit)
        else:
            # Add LIMIT clause
            return self._add_limit(sql, limit)

    def _has_limit_clause(self, sql: str) -> bool:
        """
        Check if SQL already has LIMIT clause.

        Args:
            sql: SQL query

        Returns:
            True if LIMIT clause exists
        """
        return bool(re.search(r'\bLIMIT\s+\d+', sql, re.IGNORECASE))

    def _replace_limit(self, sql: str, limit: int) -> str:
        """
        Replace existing LIMIT clause with enforced limit.

        Args:
            sql: SQL query with existing LIMIT
            limit: New limit to enforce

        Returns:
            SQL with updated LIMIT
        """
        # Extract existing limit
        match = re.search(r'\bLIMIT\s+(\d+)', sql, re.IGNORECASE)
        if match:
            existing_limit = int(match.group(1))
            # Only replace if existing exceeds maximum
            if existing_limit > self.max_limit:
                sql = re.sub(
                    r'\bLIMIT\s+\d+',
                    f'LIMIT {self.max_limit}',
                    sql,
                    flags=re.IGNORECASE
                )
        return sql

    def _add_limit(self, sql: str, limit: int) -> str:
        """
        Add LIMIT clause to SQL query.

        Args:
            sql: SQL query without LIMIT
            limit: Limit to add

        Returns:
            SQL with LIMIT clause
        """
        # Remove trailing semicolon and whitespace
        sql = sql.rstrip().rstrip(';')

        # Add LIMIT before any ORDER BY if present
        # Order of SQL clauses: WHERE -> GROUP BY -> HAVING -> ORDER BY -> LIMIT
        if re.search(r'\bORDER\s+BY\b', sql, re.IGNORECASE):
            # LIMIT goes after ORDER BY
            sql = f"{sql} LIMIT {limit}"
        else:
            # Just append LIMIT
            sql = f"{sql} LIMIT {limit}"

        return sql

    def validate_limit(self, limit: int) -> tuple[bool, str, int]:
        """
        Validate requested limit.

        Args:
            limit: Requested limit

        Returns:
            Tuple of (is_valid, error_message, adjusted_limit)
        """
        if limit <= 0:
            return False, "LIMIT must be positive", self.default_limit

        if limit > self.max_limit:
            return True, f"LIMIT adjusted to maximum ({self.max_limit})", self.max_limit

        return True, "", limit


# Global limit injector instance
_limit_injector: Optional[LimitInjector] = None


def get_limit_injector() -> LimitInjector:
    """
    Get or create the global limit injector.

    Returns:
        LimitInjector instance
    """
    global _limit_injector
    if _limit_injector is None:
        _limit_injector = LimitInjector()
    return _limit_injector
