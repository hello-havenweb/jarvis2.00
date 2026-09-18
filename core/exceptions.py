"""JARVIS custom exceptions."""


class JarvisError(Exception):
    """Base exception for JARVIS."""


class ConfigurationError(JarvisError):
    """Configuration-related error."""


class AIProviderError(JarvisError):
    """AI provider communication error."""


class PermissionDeniedError(JarvisError):
    """Action blocked by permission system."""


class ToolExecutionError(JarvisError):
    """Tool execution failed."""


class ToolNotFoundError(JarvisError):
    """Requested tool not found in registry."""


class AudioError(JarvisError):
    """Audio subsystem error."""


class BrowserError(JarvisError):
    """Browser automation error."""


class EmailError(JarvisError):
    """Email operation error."""


class HAVENError(JarvisError):
    """HAVEN data error."""


class BatchProcessingError(JarvisError):
    """Batch processing error."""


class DatabaseError(JarvisError):
    """Database operation error."""


class MemoryError_(JarvisError):
    """Memory subsystem error (named to avoid shadowing built-in)."""


class ValidationError(JarvisError):
    """Input validation error."""
