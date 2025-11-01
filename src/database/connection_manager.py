"""
Database connection manager with read-only credentials.

Constitutional Principle VI: Read-only database access to prevent data modification.
"""

from typing import Any, Dict, List, Optional
from contextlib import contextmanager
import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2.pool import ThreadedConnectionPool

from config.settings import get_settings


class DatabaseConnectionManager:
    """
    Manages database connections with strict read-only enforcement.

    Features:
    - Connection pooling for performance
    - Read-only transaction isolation
    - Automatic connection cleanup
    - Query timeout enforcement
    """

    def __init__(self):
        """Initialize database connection manager."""
        self.settings = get_settings()
        self.pool: Optional[ThreadedConnectionPool] = None
        self._initialize_pool()

    def _initialize_pool(self) -> None:
        """Create connection pool with read-only credentials."""
        try:
            self.pool = ThreadedConnectionPool(
                minconn=1,
                maxconn=self.settings.database_pool_size,
                dsn=self.settings.database_url
            )
        except Exception as e:
            raise RuntimeError(f"Failed to initialize database connection pool: {e}")

    @contextmanager
    def get_connection(self):
        """
        Get a read-only database connection from the pool.

        Yields:
            Connection object with read-only transaction

        Raises:
            RuntimeError: If connection pool is not initialized
        """
        if self.pool is None:
            raise RuntimeError("Database connection pool not initialized")

        conn = None
        try:
            conn = self.pool.getconn()
            # Set connection to read-only mode
            conn.set_session(readonly=True, autocommit=False)
            yield conn
        finally:
            if conn:
                try:
                    conn.rollback()  # Ensure no changes are committed
                except Exception:
                    pass
                self.pool.putconn(conn)

    def execute_query(
        self,
        sql: str,
        parameters: Optional[Dict[str, Any]] = None,
        timeout_seconds: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Execute a SELECT query with timeout enforcement.

        Args:
            sql: SQL query to execute (must be SELECT only)
            parameters: Query parameters (properly sanitized)
            timeout_seconds: Query timeout in seconds (default from settings)

        Returns:
            List of result rows as dictionaries

        Raises:
            ValueError: If query is not a SELECT statement
            TimeoutError: If query exceeds timeout
            Exception: For database errors
        """
        # Enforce SELECT-only queries
        sql_upper = sql.strip().upper()
        if not sql_upper.startswith("SELECT"):
            raise ValueError("Only SELECT queries are allowed. All modification queries are blocked.")

        timeout = timeout_seconds or self.settings.query_timeout_seconds

        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                try:
                    # Set query timeout
                    cursor.execute(f"SET statement_timeout = {timeout * 1000}")  # milliseconds

                    # Execute query with parameterized values
                    if parameters:
                        cursor.execute(sql, parameters)
                    else:
                        cursor.execute(sql)

                    # Fetch results
                    results = cursor.fetchall()
                    return [dict(row) for row in results]

                except psycopg2.errors.QueryCanceled as e:
                    raise TimeoutError(f"Query exceeded timeout of {timeout} seconds") from e
                except Exception as e:
                    raise Exception(f"Database query failed: {e}") from e

    def test_connection(self) -> bool:
        """
        Test database connection.

        Returns:
            True if connection successful, False otherwise
        """
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT 1")
                    return True
        except Exception:
            return False

    def close(self) -> None:
        """Close all connections in the pool."""
        if self.pool:
            self.pool.closeall()
            self.pool = None


# Global connection manager instance
_connection_manager: Optional[DatabaseConnectionManager] = None


def get_connection_manager() -> DatabaseConnectionManager:
    """
    Get or create the global database connection manager.

    Returns:
        DatabaseConnectionManager instance
    """
    global _connection_manager
    if _connection_manager is None:
        _connection_manager = DatabaseConnectionManager()
    return _connection_manager
