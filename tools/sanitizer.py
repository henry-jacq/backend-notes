import re

UNICODE_REPLACEMENTS = {
    "→": "->",
    "←": "<-",
    "⇒": "=>",
    "⇐": "<=",
}

def sanitize_content(content: str) -> str:
    """Sanitize prohibited Unicode symbols with ASCII alternatives to prevent PDF drawing errors."""
    for uni, ascii_alt in UNICODE_REPLACEMENTS.items():
        content = content.replace(uni, ascii_alt)
    return content

def check_content(content: str) -> list[tuple[int, str]]:
    """Check for illegal Unicode arrows in document content.
    Returns (line_number, warning_message) pairs."""
    violations = []
    for idx, line in enumerate(content.splitlines(), 1):
        for uni, ascii_alt in UNICODE_REPLACEMENTS.items():
            if uni in line:
                violations.append((idx, f"Prohibited Unicode arrow '{uni}' found. Use ASCII variant '{ascii_alt}' instead."))
    return violations
