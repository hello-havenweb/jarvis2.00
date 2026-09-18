"""Simple and extensible email template engine."""

import re
from typing import Dict, Any, Optional
from string import Template


class TemplateRenderError(Exception):
    """Raised when template variable substitution fails."""
    pass


class EmailTemplate:
    """Represents a reusable subject and body template."""

    def __init__(
        self,
        name: str,
        subject_template: str,
        body_text_template: str = "",
        body_html_template: str = "",
    ) -> None:
        self.name = name
        self.subject_template = subject_template
        self.body_text_template = body_text_template
        self.body_html_template = body_html_template

    def render(self, context: Dict[str, Any], safe: bool = False) -> Dict[str, str]:
        """
        Renders subject and body with variable context.
        
        Supports $variable or ${variable} placeholders.
        """
        try:
            subj_tmpl = Template(self.subject_template)
            text_tmpl = Template(self.body_text_template)
            html_tmpl = Template(self.body_html_template)

            if safe:
                return {
                    "subject": subj_tmpl.safe_substitute(context),
                    "body_text": text_tmpl.safe_substitute(context),
                    "body_html": html_tmpl.safe_substitute(context),
                }
            else:
                return {
                    "subject": subj_tmpl.substitute(context),
                    "body_text": text_tmpl.substitute(context),
                    "body_html": html_tmpl.substitute(context),
                }
        except KeyError as e:
            raise TemplateRenderError(f"Missing required template key: {e}") from e


class TemplateRegistry:
    """Registry for managing named email templates."""

    def __init__(self) -> None:
        self._templates: Dict[str, EmailTemplate] = {}

    def register(self, template: EmailTemplate) -> None:
        self._templates[template.name] = template

    def get(self, name: str) -> EmailTemplate:
        if name not in self._templates:
            raise KeyError(f"Template '{name}' is not registered.")
        return self._templates[name]

    def render(self, name: str, context: Dict[str, Any], safe: bool = False) -> Dict[str, str]:
        return self.get(name).render(context, safe=safe)
