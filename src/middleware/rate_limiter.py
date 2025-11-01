"""
Rate limiting middleware to prevent query abuse.

Constitutional Principle VI: User queries must be rate-limited to prevent
system abuse (e.g., 10 queries per minute per user).
"""

import time
from typing import Dict, Optional
from collections import defaultdict, deque
from threading import Lock

from src.logging.audit_logger import get_audit_logger
from config.settings import get_settings


class RateLimiter:
    """
    Rate limiter using sliding window algorithm.

    Tracks query counts per user within a time window and blocks
    requests that exceed the configured limit.
    """

    def __init__(self):
        """Initialize rate limiter."""
        self.settings = get_settings()
        self.audit_logger = get_audit_logger()

        # Queries per user per minute
        self.rate_limit = self.settings.rate_limit_per_minute
        self.window_seconds = 60  # 1 minute window

        # Track query timestamps per user
        # Key: user_id, Value: deque of timestamps
        self.query_times: Dict[str, deque] = defaultdict(deque)
        self.lock = Lock()

    def is_allowed(self, user_id: str) -> tuple[bool, int, str]:
        """
        Check if user is allowed to make a query.

        Args:
            user_id: User identifier

        Returns:
            Tuple of (is_allowed, remaining_queries, error_message)
        """
        with self.lock:
            current_time = time.time()
            user_times = self.query_times[user_id]

            # Remove timestamps outside the window
            while user_times and current_time - user_times[0] > self.window_seconds:
                user_times.popleft()

            queries_in_window = len(user_times)

            # Check if limit exceeded
            if queries_in_window >= self.rate_limit:
                # Calculate time until oldest query expires
                oldest_time = user_times[0]
                wait_seconds = int(self.window_seconds - (current_time - oldest_time)) + 1

                error_message = (
                    f"Rate limit exceeded. You've reached the limit of {self.rate_limit} queries per minute. "
                    f"Please wait {wait_seconds} seconds before trying again."
                )

                # Log rate limit event
                self.audit_logger.log_rate_limit(
                    user_id=user_id,
                    queries_in_window=queries_in_window,
                    limit=self.rate_limit
                )

                return False, 0, error_message

            # Allow query and record timestamp
            user_times.append(current_time)
            remaining = self.rate_limit - len(user_times)

            return True, remaining, ""

    def reset_user(self, user_id: str) -> None:
        """
        Reset rate limit for a specific user.

        Args:
            user_id: User identifier
        """
        with self.lock:
            if user_id in self.query_times:
                del self.query_times[user_id]

    def get_user_status(self, user_id: str) -> Dict[str, int]:
        """
        Get current rate limit status for a user.

        Args:
            user_id: User identifier

        Returns:
            Dictionary with queries_used, queries_remaining, window_seconds
        """
        with self.lock:
            current_time = time.time()
            user_times = self.query_times.get(user_id, deque())

            # Remove expired timestamps
            while user_times and current_time - user_times[0] > self.window_seconds:
                user_times.popleft()

            queries_used = len(user_times)
            queries_remaining = max(0, self.rate_limit - queries_used)

            return {
                "queries_used": queries_used,
                "queries_remaining": queries_remaining,
                "window_seconds": self.window_seconds,
                "rate_limit": self.rate_limit
            }

    def cleanup_expired(self) -> None:
        """
        Clean up expired query timestamps for all users.

        Should be called periodically to prevent memory buildup.
        """
        with self.lock:
            current_time = time.time()
            users_to_remove = []

            for user_id, user_times in self.query_times.items():
                # Remove expired timestamps
                while user_times and current_time - user_times[0] > self.window_seconds:
                    user_times.popleft()

                # Mark user for removal if no recent queries
                if not user_times:
                    users_to_remove.append(user_id)

            # Remove users with no recent activity
            for user_id in users_to_remove:
                del self.query_times[user_id]


# Global rate limiter instance
_rate_limiter: Optional[RateLimiter] = None


def get_rate_limiter() -> RateLimiter:
    """
    Get or create the global rate limiter.

    Returns:
        RateLimiter instance
    """
    global _rate_limiter
    if _rate_limiter is None:
        _rate_limiter = RateLimiter()
    return _rate_limiter
