"""
Configuration settings for Sales & Website Analytics Chat Assistant.

This module manages database connections, LLM API keys, rate limits,
query timeouts, and other system configuration following constitutional
principles of safety and security.
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )

    # Application
    app_name: str = "Sales & Website Analytics Chat Assistant"
    app_version: str = "1.0.0"
    debug: bool = False

    # Database Configuration (Read-Only Credentials)
    database_url: str = "postgresql://readonly_user:password@localhost:5432/analytics_db"
    database_read_only: bool = True  # Enforce read-only mode
    database_pool_size: int = 10
    database_max_overflow: int = 20

    # LLM API Configuration
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2"
    llm_model: str = "gpt-4"  # or "claude-3-opus-20240229" or "ollama"
    llm_temperature: float = 0.1  # Low temperature for consistency
    llm_max_tokens: int = 500

    # Safety Controls
    query_timeout_seconds: int = 30  # Max query execution time
    default_row_limit: int = 100  # Default LIMIT for SELECT queries
    max_row_limit: int = 1000  # Maximum allowed LIMIT
    rate_limit_per_minute: int = 10  # Queries per user per minute

    # Whitelisted Tables (Constitutional Principle I & VI)
    whitelisted_tables: list[str] = [
        "sales_transactions",
        "website_visits"
    ]

    # Blocked SQL Keywords (Constitutional Principle VI)
    blocked_keywords: list[str] = [
        "DROP", "DELETE", "UPDATE", "INSERT", "TRUNCATE",
        "ALTER", "CREATE", "GRANT", "REVOKE", "EXEC",
        "EXECUTE", "MERGE", "REPLACE"
    ]

    # Template Library Path
    sql_template_dir: str = "templates/sql"
    few_shot_examples_path: str = "templates/few_shot_examples.json"

    # Logging & Audit
    log_level: str = "INFO"
    audit_log_path: str = "logs/audit.log"
    enable_query_logging: bool = True

    # CORS Settings
    cors_origins: list[str] = ["http://localhost:3000", "http://localhost:5173"]
    cors_allow_credentials: bool = True
    cors_allow_methods: list[str] = ["GET", "POST"]
    cors_allow_headers: list[str] = ["*"]

    # Chart Configuration
    default_chart_width: int = 800
    default_chart_height: int = 400
    supported_chart_types: list[str] = ["bar", "line", "pie", "scatter"]


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get application settings instance."""
    return settings
