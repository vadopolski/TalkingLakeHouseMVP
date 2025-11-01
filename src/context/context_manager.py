"""
Conversational context manager for follow-up questions.

Constitutional Principle II: Support for follow-up questions and clarifications.
Example: "show me last month" followed by "what about this month?"
"""

from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta
from collections import deque


class ConversationContext:
    """Stores context for a single conversation session."""

    def __init__(self, user_id: str, max_history: int = 5):
        """
        Initialize conversation context.

        Args:
            user_id: User identifier
            max_history: Maximum number of queries to retain in history
        """
        self.user_id = user_id
        self.max_history = max_history
        self.history: deque = deque(maxlen=max_history)
        self.last_query_time = datetime.now()
        self.session_start = datetime.now()

    def add_query(
        self,
        user_query: str,
        template_id: Optional[str],
        parameters: Optional[Dict[str, Any]],
        results: Optional[List[Dict[str, Any]]]
    ) -> None:
        """
        Add a query to conversation history.

        Args:
            user_query: Natural language query
            template_id: Selected template ID
            parameters: Extracted parameters
            results: Query results (truncated)
        """
        query_record = {
            "timestamp": datetime.now().isoformat(),
            "user_query": user_query,
            "template_id": template_id,
            "parameters": parameters or {},
            "result_count": len(results) if results else 0,
            "has_results": bool(results)
        }

        self.history.append(query_record)
        self.last_query_time = datetime.now()

    def get_last_parameters(self) -> Optional[Dict[str, Any]]:
        """
        Get parameters from the most recent query.

        Returns:
            Parameters dictionary or None
        """
        if not self.history:
            return None

        return self.history[-1].get("parameters")

    def get_last_template(self) -> Optional[str]:
        """
        Get template ID from the most recent query.

        Returns:
            Template ID or None
        """
        if not self.history:
            return None

        return self.history[-1].get("template_id")

    def get_history(self, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Get conversation history.

        Args:
            limit: Maximum number of queries to return

        Returns:
            List of query records
        """
        return list(self.history)[-limit:]

    def is_session_active(self, timeout_minutes: int = 30) -> bool:
        """
        Check if conversation session is still active.

        Args:
            timeout_minutes: Session timeout in minutes

        Returns:
            True if session is active
        """
        time_since_last = datetime.now() - self.last_query_time
        return time_since_last.total_seconds() < (timeout_minutes * 60)

    def clear(self) -> None:
        """Clear conversation history."""
        self.history.clear()


class ContextManager:
    """
    Manages conversational context for all users.

    Enables follow-up questions by:
    - Tracking query history per user
    - Reusing parameters from previous queries
    - Resolving relative references ("this month", "same period")
    """

    def __init__(self):
        """Initialize context manager."""
        self.contexts: Dict[str, ConversationContext] = {}
        self.session_timeout_minutes = 30

    def get_context(self, user_id: str) -> ConversationContext:
        """
        Get or create conversation context for user.

        Args:
            user_id: User identifier

        Returns:
            ConversationContext instance
        """
        if user_id not in self.contexts:
            self.contexts[user_id] = ConversationContext(user_id)
        else:
            # Check if session is expired
            context = self.contexts[user_id]
            if not context.is_session_active(self.session_timeout_minutes):
                # Clear expired session and create new one
                self.contexts[user_id] = ConversationContext(user_id)

        return self.contexts[user_id]

    def resolve_follow_up_parameters(
        self,
        user_id: str,
        current_parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Resolve follow-up query parameters using context.

        Args:
            user_id: User identifier
            current_parameters: Parameters extracted from current query

        Returns:
            Merged parameters with context
        """
        context = self.get_context(user_id)
        last_params = context.get_last_parameters()

        if not last_params:
            return current_parameters

        # Merge: current parameters override previous ones
        merged = last_params.copy()
        merged.update(current_parameters)

        return merged

    def detect_follow_up_intent(self, user_query: str) -> bool:
        """
        Detect if query is a follow-up question.

        Args:
            user_query: Natural language query

        Returns:
            True if likely a follow-up question
        """
        query_lower = user_query.lower()

        follow_up_indicators = [
            "what about", "how about", "and", "also",
            "same", "similar", "this", "that",
            "too", "as well", "again"
        ]

        return any(indicator in query_lower for indicator in follow_up_indicators)

    def resolve_relative_dates(
        self,
        user_query: str,
        context: ConversationContext
    ) -> Optional[Dict[str, Any]]:
        """
        Resolve relative date references using context.

        Args:
            user_query: Natural language query
            context: Conversation context

        Returns:
            Date parameters or None
        """
        query_lower = user_query.lower()
        last_params = context.get_last_parameters()

        if not last_params:
            return None

        # Handle "this month" after "last month"
        if "this month" in query_lower and "start_date" in last_params:
            # Calculate this month based on previous query
            last_start = last_params.get("start_date")
            if last_start:
                # Shift forward by one month
                # This is a simplified version; production would use dateutil
                today = datetime.now()
                return {
                    "start_date": today.replace(day=1).strftime("%Y-%m-%d"),
                    "end_date": today.strftime("%Y-%m-%d")
                }

        # Handle "same period"
        if "same period" in query_lower or "same time" in query_lower:
            if "start_date" in last_params and "end_date" in last_params:
                return {
                    "start_date": last_params["start_date"],
                    "end_date": last_params["end_date"]
                }

        return None

    def clear_user_context(self, user_id: str) -> None:
        """
        Clear context for a specific user.

        Args:
            user_id: User identifier
        """
        if user_id in self.contexts:
            del self.contexts[user_id]

    def cleanup_expired_sessions(self) -> int:
        """
        Remove expired conversation sessions.

        Returns:
            Number of sessions removed
        """
        expired = [
            user_id for user_id, context in self.contexts.items()
            if not context.is_session_active(self.session_timeout_minutes)
        ]

        for user_id in expired:
            del self.contexts[user_id]

        return len(expired)


# Global context manager instance
_context_manager: Optional[ContextManager] = None


def get_context_manager() -> ContextManager:
    """
    Get or create the global context manager.

    Returns:
        ContextManager instance
    """
    global _context_manager
    if _context_manager is None:
        _context_manager = ContextManager()
    return _context_manager
