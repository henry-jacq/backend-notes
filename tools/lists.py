import re

# Match list items starting with -, *, +, or 1., 2., etc.
LIST_RE = re.compile(r'^\s*(?:[-*+]|\d+\.)\s+')

def check_content(content: str) -> list[tuple[int, str]]:
    """Check for list items that lack a preceding blank line, causing markdown engine parse issues.
    Returns (line_number, warning_message) pairs."""
    lines = content.splitlines()
    violations = []

    for idx, line in enumerate(lines):
        if LIST_RE.match(line):
            if idx > 0:
                prev_line = lines[idx - 1].strip()
                # A list item needs a preceding blank line if the previous line contains text
                # but is not a header, blockquote, table row, list item, or code block.
                if (prev_line and 
                    not LIST_RE.match(lines[idx - 1]) and 
                    not prev_line.startswith("#") and 
                    not prev_line.startswith("```") and
                    not prev_line.startswith(">") and
                    not prev_line.startswith("|")):
                    
                    violations.append((idx + 1, f"List item lacks a preceding blank line. Prev line: '{prev_line}'"))
    return violations

def fix_content(content: str) -> tuple[str, int]:
    """Insert blank lines before orphaned list items.
    Returns (fixed_content_str, changes_count)."""
    lines = content.splitlines()
    modified_lines = []
    changes = 0

    for idx, line in enumerate(lines):
        if LIST_RE.match(line):
            if idx > 0:
                prev_line = lines[idx - 1].strip()
                if (prev_line and 
                    not LIST_RE.match(lines[idx - 1]) and 
                    not prev_line.startswith("#") and 
                    not prev_line.startswith("```") and
                    not prev_line.startswith(">") and
                    not prev_line.startswith("|")):
                    
                    modified_lines.append("")
                    changes += 1
        modified_lines.append(line)
        
    return "\n".join(modified_lines), changes
