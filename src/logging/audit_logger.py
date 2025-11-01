"""
Audit logging infrastructure for query tracking and compliance.

Logs all queries, template selections, parameter values, and execution results
per Constitutional Principle VI (Safety & Security).
"""

import logging
import json
from datetime import datetime
from typing import Any, Dict, Optional
from pathlib import Path
import sys


class AuditLogger:
    """
    Centralized audit logger for tracking all system operations.

    Logs include:
    - User query text
    - Selected SQL template
    - Extracted parameters
    - Query execution time
    - Result row count
    - Any errors or validation failures
    """

    def __init__(self, log_path: str = "logs/audit.log", log_level: str = "INFO"):
        """
        Initialize audit logger.

        Args:
            log_path: Path to audit log file
            log_level: Logging level (INFO, WARNING, ERROR)
        """
        self.log_path = Path(log_path)
        self.log_path.parent.mkdir(parents=True, exist_ok=True)

        # Create logger
        self.logger = logging.getLogger("audit")
        self.logger.setLevel(getattr(logging, log_level.upper()))

        # Remove existing handlers to avoid duplicates
        self.logger.handlers.clear()

        # File handler with JSON formatting
        file_handler = logging.FileHandler(self.log_path)
        file_handler.setLevel(logging.INFO)

        # Console handler for development
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)

        # JSON formatter
        formatter = logging.Formatter(
            '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "message": %(message)s}',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

    def log_query(
        self,
        user_query: str,
        template_id: Optional[str],
        parameters: Optional[Dict[str, Any]],
        execution_time_ms: Optional[float],
        row_count: Optional[int],
        success: bool,
        error: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> None:
        """
        Log a query execution event.

        Args:
            user_query: Original natural language query from user
            template_id: ID of selected SQL template
            parameters: Extracted and validated parameters
            execution_time_ms: Query execution time in milliseconds
            row_count: Number of rows returned
            success: Whether query executed successfully
            error: Error message if query failed
            user_id: Optional user identifier
        """
        log_entry = {
            "event": "query_execution",
            "user_query": user_query,
            "template_id": template_id,
            "parameters": parameters,
            "execution_time_ms": execution_time_ms,
            "row_count": row_count,
            "success": success,
            "error": error,
            "user_id": user_id,
            "timestamp": datetime.utcnow().isoformat()
        }

        self.logger.info(json.dumps(log_entry))

    def log_validation_failure(
        self,
        user_query: str,
        validation_type: str,
        reason: str,
        user_id: Optional[str] = None
    ) -> None:
        """
        Log a validation failure event.

        Args:
            user_query: Original user query
            validation_type: Type of validation that failed (whitelist, keyword, parameter, etc.)
            reason: Reason for validation failure
            user_id: Optional user identifier
        """
        log_entry = {
            "event": "validation_failure",
            "user_query": user_query,
            "validation_type": validation_type,
            "reason": reason,
            "user_id": user_id,
            "timestamp": datetime.utcnow().isoformat()
        }

        self.logger.warning(json.dumps(log_entry))

    def log_rate_limit(
        self,
        user_id: str,
        queries_in_window: int,
        limit: int
    ) -> None:
        """
        Log a rate limit event.

        Args:
            user_id: User identifier
            queries_in_window: Number of queries in current time window
            limit: Rate limit threshold
        """
        log_entry = {
            "event": "rate_limit_exceeded",
            "user_id": user_id,
            "queries_in_window": queries_in_window,
            "limit": limit,
            "timestamp": datetime.utcnow().isoformat()
        }

        self.logger.warning(json.dumps(log_entry))

    def log_template_selection(
        self,
        user_query: str,
        template_id: str,
        confidence_score: Optional[float] = None,
        user_id: Optional[str] = None
    ) -> None:
        """
        Log template selection by LLM.

        Args:
            user_query: Original user query
            template_id: Selected template ID
            confidence_score: LLM confidence in template selection
            user_id: Optional user identifier
        """
        log_entry = {
            "event": "template_selection",
            "user_query": user_query,
            "template_id": template_id,
            "confidence_score": confidence_score,
            "user_id": user_id,
            "timestamp": datetime.utcnow().isoformat()
        }

        self.logger.info(json.dumps(log_entry))

    def log_system_event(
        self,
        event_type: str,
        details: Dict[str, Any]
    ) -> None:
        """
        Log general system events.

        Args:
            event_type: Type of system event
            details: Event details
        """
        log_entry = {
            "event": "system_event",
            "event_type": event_type,
            "details": details,
            "timestamp": datetime.utcnow().isoformat()
        }

        self.logger.info(json.dumps(log_entry))


# Global audit logger instance
_audit_logger: Optional[AuditLogger] = None


def get_audit_logger(log_path: str = "logs/audit.log", log_level: str = "INFO") -> AuditLogger:
    """
    Get or create the global audit logger instance.

    Args:
        log_path: Path to audit log file
        log_level: Logging level

    Returns:
        AuditLogger instance
    """
    global _audit_logger
    if _audit_logger is None:
        _audit_logger = AuditLogger(log_path=log_path, log_level=log_level)
    return _audit_logger
