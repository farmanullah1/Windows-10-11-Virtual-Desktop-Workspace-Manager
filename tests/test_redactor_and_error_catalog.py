"""
Unit tests for centralized log redaction and standardized error catalog.
"""

import logging
from app.logging.redactor import LogRedactor, RedactingFilter, RedactingFormatter
from app.models.error_codes import ERROR_CATALOG, get_error, ErrorCategory


def test_log_redactor_patterns():
    redactor = LogRedactor()

    # Secret key patterns
    sample1 = "Connecting with password=SuperSecret123 to database"
    assert redactor.redact(sample1) == "Connecting with password=[REDACTED] to database"

    sample2 = "Using api_key: 'abc-xyz-987' for requests"
    assert redactor.redact(sample2) == "Using api_key: '[REDACTED]' for requests"

    sample3 = "Header Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"
    assert "Bearer [REDACTED]" in redactor.redact(sample3)

    sample4 = "Executable args: mytool.exe --password mypass123 --user admin"
    assert "--password [REDACTED]" in redactor.redact(sample4)


def test_log_redactor_dict():
    redactor = LogRedactor()
    data = {
        "user": "test_user",
        "password": "secret_password",
        "nested": {
            "token": "secret_token_123",
            "normal": "normal_value"
        }
    }
    redacted = redactor.redact_dict(data)
    assert redacted["password"] == "[REDACTED]"
    assert redacted["nested"]["token"] == "[REDACTED]"
    assert redacted["nested"]["normal"] == "normal_value"


def test_redacting_formatter():
    formatter = RedactingFormatter("%(levelname)s - %(message)s")

    record = logging.LogRecord(
        name="test",
        level=logging.INFO,
        pathname="",
        lineno=0,
        msg="Launched with token=%s and password=%s",
        args=("secret_token_abc", "pass123"),
        exc_info=None
    )
    formatted = formatter.format(record)
    assert "token=[REDACTED]" in formatted
    assert "password=[REDACTED]" in formatted
    assert "secret_token_abc" not in formatted
    assert "pass123" not in formatted


def test_redacting_filter():
    redactor = LogRedactor()
    f = RedactingFilter(redactor)

    record = logging.LogRecord(
        name="test",
        level=logging.INFO,
        pathname="",
        lineno=0,
        msg="Launched with secret=my_api_key_secret",
        args=(),
        exc_info=None
    )
    assert f.filter(record) is True
    assert record.msg == "Launched with secret=[REDACTED]"


def test_error_catalog_lookup():
    vdm_err = get_error("VDM-001")
    assert vdm_err.category == ErrorCategory.VDM
    assert "Provider Unavailable" in vdm_err.title
    assert "[VDM-001]" in vdm_err.format_log()
    assert "Recommendation:" in vdm_err.format_user("COM failure")

    # Unknown fallback
    unk_err = get_error("UNKNOWN-999")
    assert unk_err.code == "UNKNOWN-999"
    assert "Unknown Error" in unk_err.title
