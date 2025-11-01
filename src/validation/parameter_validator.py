"""
Parameter validation framework with type and range checking.

Constitutional Principle VI: All template parameters must be validated against
type and range constraints before query execution.
"""

import re
from datetime import datetime, date
from typing import Any, Dict, List, Optional


class ParameterValidator:
    """
    Validates query parameters against type and range constraints.

    Prevents SQL injection and ensures data integrity by validating:
    - Data types (date, string, integer, float, boolean)
    - Value ranges (min/max)
    - String patterns (regex)
    - Allowed values (whitelists)
    """

    def validate_parameter(
        self,
        param_name: str,
        param_value: Any,
        param_type: str,
        required: bool = True,
        validation_rules: Optional[Dict[str, Any]] = None
    ) -> tuple[bool, str, Any]:
        """
        Validate a single parameter.

        Args:
            param_name: Parameter name
            param_value: Parameter value to validate
            param_type: Expected type (date, string, integer, float, boolean)
            required: Whether parameter is required
            validation_rules: Additional validation rules

        Returns:
            Tuple of (is_valid, error_message, sanitized_value)
        """
        # Check if required parameter is missing
        if required and param_value is None:
            return False, f"Required parameter '{param_name}' is missing", None

        # Allow None for optional parameters
        if not required and param_value is None:
            return True, "", None

        validation_rules = validation_rules or {}

        # Type-specific validation
        if param_type == "date":
            return self._validate_date(param_name, param_value, validation_rules)
        elif param_type == "string":
            return self._validate_string(param_name, param_value, validation_rules)
        elif param_type == "integer":
            return self._validate_integer(param_name, param_value, validation_rules)
        elif param_type == "float":
            return self._validate_float(param_name, param_value, validation_rules)
        elif param_type == "boolean":
            return self._validate_boolean(param_name, param_value, validation_rules)
        else:
            return False, f"Unknown parameter type: {param_type}", None

    def _validate_date(
        self,
        param_name: str,
        value: Any,
        rules: Dict[str, Any]
    ) -> tuple[bool, str, Optional[date]]:
        """Validate date parameter."""
        # Convert string to date if needed
        if isinstance(value, str):
            try:
                value = datetime.fromisoformat(value).date()
            except ValueError:
                return False, f"Parameter '{param_name}' must be a valid ISO date (YYYY-MM-DD)", None
        elif isinstance(value, datetime):
            value = value.date()
        elif not isinstance(value, date):
            return False, f"Parameter '{param_name}' must be a date", None

        # Check min/max constraints
        if "min_value" in rules:
            min_date = datetime.fromisoformat(rules["min_value"]).date()
            if value < min_date:
                return False, f"Parameter '{param_name}' must be >= {min_date}", None

        if "max_value" in rules:
            max_date = datetime.fromisoformat(rules["max_value"]).date()
            if value > max_date:
                return False, f"Parameter '{param_name}' must be <= {max_date}", None

        return True, "", value

    def _validate_string(
        self,
        param_name: str,
        value: Any,
        rules: Dict[str, Any]
    ) -> tuple[bool, str, Optional[str]]:
        """Validate string parameter."""
        if not isinstance(value, str):
            return False, f"Parameter '{param_name}' must be a string", None

        # Check allowed values whitelist
        if "allowed_values" in rules:
            if value not in rules["allowed_values"]:
                return False, f"Parameter '{param_name}' must be one of: {', '.join(rules['allowed_values'])}", None

        # Check pattern (regex)
        if "pattern" in rules:
            if not re.match(rules["pattern"], value):
                return False, f"Parameter '{param_name}' does not match required pattern", None

        # Check length constraints
        if "min_value" in rules and len(value) < rules["min_value"]:
            return False, f"Parameter '{param_name}' must be at least {rules['min_value']} characters", None

        if "max_value" in rules and len(value) > rules["max_value"]:
            return False, f"Parameter '{param_name}' must be at most {rules['max_value']} characters", None

        # Sanitize: Remove potentially dangerous characters
        # Only allow alphanumeric, spaces, hyphens, underscores
        sanitized = re.sub(r'[^a-zA-Z0-9\s\-_]', '', value)

        return True, "", sanitized

    def _validate_integer(
        self,
        param_name: str,
        value: Any,
        rules: Dict[str, Any]
    ) -> tuple[bool, str, Optional[int]]:
        """Validate integer parameter."""
        try:
            value = int(value)
        except (ValueError, TypeError):
            return False, f"Parameter '{param_name}' must be an integer", None

        # Check min/max constraints
        if "min_value" in rules and value < rules["min_value"]:
            return False, f"Parameter '{param_name}' must be >= {rules['min_value']}", None

        if "max_value" in rules and value > rules["max_value"]:
            return False, f"Parameter '{param_name}' must be <= {rules['max_value']}", None

        return True, "", value

    def _validate_float(
        self,
        param_name: str,
        value: Any,
        rules: Dict[str, Any]
    ) -> tuple[bool, str, Optional[float]]:
        """Validate float parameter."""
        try:
            value = float(value)
        except (ValueError, TypeError):
            return False, f"Parameter '{param_name}' must be a number", None

        # Check min/max constraints
        if "min_value" in rules and value < rules["min_value"]:
            return False, f"Parameter '{param_name}' must be >= {rules['min_value']}", None

        if "max_value" in rules and value > rules["max_value"]:
            return False, f"Parameter '{param_name}' must be <= {rules['max_value']}", None

        return True, "", value

    def _validate_boolean(
        self,
        param_name: str,
        value: Any,
        rules: Dict[str, Any]
    ) -> tuple[bool, str, Optional[bool]]:
        """Validate boolean parameter."""
        if isinstance(value, bool):
            return True, "", value

        if isinstance(value, str):
            if value.lower() in ("true", "yes", "1"):
                return True, "", True
            elif value.lower() in ("false", "no", "0"):
                return True, "", False

        return False, f"Parameter '{param_name}' must be a boolean", None

    def validate_parameters(
        self,
        parameters: Dict[str, Any],
        parameter_definitions: List[Dict[str, Any]]
    ) -> tuple[bool, str, Dict[str, Any]]:
        """
        Validate all parameters against their definitions.

        Args:
            parameters: Dictionary of parameter values
            parameter_definitions: List of parameter definition dicts

        Returns:
            Tuple of (is_valid, error_message, sanitized_parameters)
        """
        sanitized = {}

        for param_def in parameter_definitions:
            param_name = param_def["name"]
            param_type = param_def["type"]
            required = param_def.get("required", True)
            validation_rules = param_def.get("validation", {})

            param_value = parameters.get(param_name)

            valid, error, sanitized_value = self.validate_parameter(
                param_name=param_name,
                param_value=param_value,
                param_type=param_type,
                required=required,
                validation_rules=validation_rules
            )

            if not valid:
                return False, error, {}

            if sanitized_value is not None:
                sanitized[param_name] = sanitized_value

        return True, "", sanitized


# Global validator instance
_parameter_validator: ParameterValidator | None = None


def get_parameter_validator() -> ParameterValidator:
    """
    Get or create the global parameter validator.

    Returns:
        ParameterValidator instance
    """
    global _parameter_validator
    if _parameter_validator is None:
        _parameter_validator = ParameterValidator()
    return _parameter_validator
