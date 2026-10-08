"""
Centralized log and diagnostic redaction layer.
Automatically sanitizes secrets, tokens, passwords, and sensitive keys from log messages.
"""

from __future__ import annotations
import re
import logging
from typing import List, Pattern, Any, Dict, Optional


DEFAULT_SENSITIVE_PATTERNS: List[str] = [
    # Key-value pairs: password=xyz, token: xyz, apikey: xyz, api_key: "xyz", secret=xyz
    # Negative lookahead avoids replacing format strings like %s or {}
    r"(?i)\b(?:password|passwd|pwd|token|apikey|api_key|secret|credential)\s*[:=]\s*['\"]?(?!%[sd]|{[\d\w]*})([^\s'\",;&]+)['\"]?",
    # Authorization header with Bearer or standalone Bearer <token>
    r"(?i)(?:\bauthorization\s*[:=]\s*)?\bbearer\s+['\"]?([A-Za-z0-9\-_=]+\.?[A-Za-z0-9\-_=]*\.?[A-Za-z0-9\-_=]*)['\"]?",
    # Authorization without bearer (e.g. Basic xxx or token xxx)
    r"(?i)\bauthorization\s*[:=]\s*(?!bearer\b)['\"]?(?!%[sd]|{[\d\w]*})([^\s'\",;&]+)['\"]?",
    # Command-line passwords: --password xxx, -p xxx, /p:xxx
    r"(?i)(?:--password|-p|/p:?)\s+['\"]?([^\s'\",;]+)['\"]?",
]


class LogRedactor:
    """Centralized redaction utility that masks sensitive data."""

    def __init__(self, additional_patterns: Optional[List[str]] = None):
        self._patterns: List[Pattern[str]] = []
        for pat in DEFAULT_SENSITIVE_PATTERNS:
            self._patterns.append(re.compile(pat))
        if additional_patterns:
            for pat in additional_patterns:
                self._patterns.append(re.compile(pat))

    def add_pattern(self, pattern: str) -> None:
        """Add an additional regex pattern for redaction."""
        self._patterns.append(re.compile(pattern))

    def redact(self, text: str) -> str:
        """Redacts sensitive values found in text, replacing with [REDACTED]."""
        if not text:
            return text
        sanitized = text
        for pattern in self._patterns:
            def _repl(match: re.Match) -> str:
                full = match.group(0)
                # Replace the captured secret group (group 1) with [REDACTED]
                if match.lastindex and match.lastindex >= 1:
                    secret_val = match.group(1)
                    if secret_val:
                        return full.replace(secret_val, "[REDACTED]")
                return "[REDACTED]"

            sanitized = pattern.sub(_repl, sanitized)
        return sanitized

    def redact_dict(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively redacts dictionary keys and string values."""
        redacted: Dict[str, Any] = {}
        sensitive_keys = {
            "password", "token", "secret", "apikey", "api_key",
            "authorization", "credential", "private_key"
        }
        for k, v in data.items():
            if any(s in k.lower() for s in sensitive_keys):
                redacted[k] = "[REDACTED]"
            elif isinstance(v, str):
                redacted[k] = self.redact(v)
            elif isinstance(v, dict):
                redacted[k] = self.redact_dict(v)
            elif isinstance(v, list):
                redacted[k] = [self.redact(item) if isinstance(item, str) else item for item in v]
            else:
                redacted[k] = v
        return redacted


_GLOBAL_REDACTOR = LogRedactor()


def get_global_redactor() -> LogRedactor:
    return _GLOBAL_REDACTOR


class RedactingFormatter(logging.Formatter):
    """Logging formatter that ensures the final formatted message is always sanitized."""

    def __init__(self, fmt: Optional[str] = None, datefmt: Optional[str] = None, redactor: Optional[LogRedactor] = None):
        super().__init__(fmt=fmt, datefmt=datefmt)
        self.redactor = redactor or get_global_redactor()

    def format(self, record: logging.LogRecord) -> str:
        formatted = super().format(record)
        return self.redactor.redact(formatted)


class RedactingFilter(logging.Filter):
    """Logging filter that redacts record attributes before formatting."""

    def __init__(self, redactor: Optional[LogRedactor] = None):
        super().__init__()
        self.redactor = redactor or get_global_redactor()

    def filter(self, record: logging.LogRecord) -> bool:
        if isinstance(record.msg, str):
            record.msg = self.redactor.redact(record.msg)
        return True
