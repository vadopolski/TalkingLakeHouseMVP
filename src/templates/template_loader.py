"""
SQL template loader - loads templates from Git into memory.

Constitutional Principle III: All SQL queries must be generated from
pre-defined, vetted templates stored in version control.
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from config.settings import get_settings


class TemplateLoader:
    """
    Loads and manages SQL templates from the Git-versioned template library.

    Templates are loaded from templates/sql/ directory and cached in memory
    for fast access during query processing.
    """

    def __init__(self):
        """Initialize template loader."""
        self.settings = get_settings()
        self.template_dir = Path(self.settings.sql_template_dir)
        self.templates: Dict[str, Dict[str, Any]] = {}
        self.schema: Optional[Dict[str, Any]] = None
        self._load_schema()

    def _load_schema(self) -> None:
        """Load template schema definition."""
        schema_path = self.template_dir / "template_schema.json"
        if schema_path.exists():
            with open(schema_path, 'r') as f:
                self.schema = json.load(f)

    def load_template(self, template_id: str) -> Optional[Dict[str, Any]]:
        """
        Load a single template by ID.

        Args:
            template_id: Template identifier

        Returns:
            Template dictionary or None if not found
        """
        # Check cache first
        if template_id in self.templates:
            return self.templates[template_id]

        # Load from file
        template_file = self.template_dir / f"{template_id}.json"
        if not template_file.exists():
            return None

        try:
            with open(template_file, 'r') as f:
                template = json.load(f)
                self.templates[template_id] = template
                return template
        except Exception as e:
            print(f"Error loading template {template_id}: {e}")
            return None

    def load_all_templates(self) -> Dict[str, Dict[str, Any]]:
        """
        Load all templates from the template directory.

        Returns:
            Dictionary mapping template_id to template data
        """
        if not self.template_dir.exists():
            return {}

        templates = {}
        for template_file in self.template_dir.glob("*.json"):
            # Skip schema file
            if template_file.name == "template_schema.json":
                continue

            template_id = template_file.stem
            template = self.load_template(template_id)
            if template:
                templates[template_id] = template

        self.templates = templates
        return templates

    def get_templates_by_category(self, category: str) -> List[Dict[str, Any]]:
        """
        Get all templates for a specific category.

        Args:
            category: Category name (sales, traffic, conversion)

        Returns:
            List of templates in the category
        """
        return [
            template for template in self.templates.values()
            if template.get("category") == category
        ]

    def get_template_ids(self) -> List[str]:
        """
        Get list of all template IDs.

        Returns:
            List of template identifiers
        """
        return list(self.templates.keys())

    def validate_template(self, template: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Validate template against schema.

        Args:
            template: Template dictionary

        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check required fields
        required_fields = [
            "template_id", "description", "sql_structure",
            "parameters", "whitelisted_tables", "chart_type"
        ]

        for field in required_fields:
            if field not in template:
                return False, f"Missing required field: {field}"

        # Validate SQL is SELECT only
        sql = template["sql_structure"].strip().upper()
        if not sql.startswith("SELECT"):
            return False, "Template must contain SELECT query only"

        # Validate whitelisted tables
        allowed_tables = self.settings.whitelisted_tables
        for table in template.get("whitelisted_tables", []):
            if table not in allowed_tables:
                return False, f"Table '{table}' not in global whitelist"

        return True, ""

    def reload_templates(self) -> int:
        """
        Reload all templates from disk.

        Returns:
            Number of templates loaded
        """
        self.templates.clear()
        templates = self.load_all_templates()
        return len(templates)

    def get_template_metadata(self, template_id: str) -> Optional[Dict[str, Any]]:
        """
        Get template metadata without full template.

        Args:
            template_id: Template identifier

        Returns:
            Metadata dictionary or None
        """
        template = self.load_template(template_id)
        if not template:
            return None

        return {
            "template_id": template.get("template_id"),
            "description": template.get("description"),
            "category": template.get("category"),
            "chart_type": template.get("chart_type"),
            "example_questions": template.get("example_questions", [])
        }

    def search_templates(self, query: str) -> List[Dict[str, Any]]:
        """
        Search templates by description or example questions.

        Args:
            query: Search query

        Returns:
            List of matching template metadata
        """
        query_lower = query.lower()
        matches = []

        for template_id, template in self.templates.items():
            # Search in description
            if query_lower in template.get("description", "").lower():
                matches.append(self.get_template_metadata(template_id))
                continue

            # Search in example questions
            examples = template.get("example_questions", [])
            if any(query_lower in ex.lower() for ex in examples):
                matches.append(self.get_template_metadata(template_id))

        return matches


# Global template loader instance
_template_loader: Optional[TemplateLoader] = None


def get_template_loader() -> TemplateLoader:
    """
    Get or create the global template loader.

    Returns:
        TemplateLoader instance
    """
    global _template_loader
    if _template_loader is None:
        _template_loader = TemplateLoader()
        # Load templates on initialization
        _template_loader.load_all_templates()
    return _template_loader
