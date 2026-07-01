import re
import yaml
import markdown
from datetime import datetime
from pathlib import Path
from tools.config import BASE_DIR, FILES_CONFIG, PART_NUMBERS_ROMAN
from tools.spelling import convert_content, clean_line_prose
from tools.sanitizer import sanitize_content

# Try to load CSS
css_path = BASE_DIR / "book.css"
if css_path.exists():
    BOOK_CSS = css_path.read_text(encoding="utf-8")
else:
    BOOK_CSS = ""

def parse_frontmatter(content: str):
    """Parse YAML frontmatter and return (metadata_dict, body_content)."""
    content = content.lstrip("\ufeff")  # strip BOM if present
    if not content.startswith("---"):
        return {}, content

    try:
        end_idx = content.index("---", 3)
    except ValueError:
        return {}, content

    yaml_block = content[3:end_idx].strip()
    body = content[end_idx + 3:].strip()

    try:
        metadata = yaml.safe_load(yaml_block) or {}
    except yaml.YAMLError:
        metadata = {}

    return metadata, body

def clean_summary(summary: str) -> str:
    """Clean the summary string by removing generic 'This document' prefix
    to fit professional book templates."""
    if not summary or summary.lower() == "no summary available":
        return ""
    
    # Run standard prose conversions to match Indian English
    summary = clean_line_prose(summary)
    
    # Capitalize the first letter if needed
    if summary and summary[0].islower():
        summary = summary[0].upper() + summary[1:]

    return summary.strip()

def extract_untruncated_summary(body_content: str) -> str:
    """Extract the first meaningful paragraph from the body content without truncation."""
    lines = body_content.splitlines()
    paragraph_lines = []
    found_heading = False

    for line in lines:
        stripped = line.strip()

        if not found_heading:
            if stripped.startswith("# "):
                found_heading = True
            continue

        if not paragraph_lines and not stripped:
            continue

        if stripped.startswith("## "):
            break

        if not stripped and paragraph_lines:
            break

        paragraph_lines.append(stripped)

    summary = " ".join(paragraph_lines)
    return summary.strip()

def clean_markdown_body(body: str) -> str:
    """Remove the first # heading (it's already in the chapter header)
    and clean up file:// links."""
    lines = body.splitlines()
    cleaned = []
    removed_heading = False

    for line in lines:
        if not removed_heading and line.strip().startswith("# "):
            removed_heading = True
            continue
        cleaned.append(line)

    text = "\n".join(cleaned)
    # Strip file:// links
    text = re.sub(r'\[([^\]]+)\]\(file:///[^)]+\)', r'\1', text)
    return text

def md_to_html(md_text: str) -> str:
    """Convert markdown text to HTML using standard extensions."""
    extensions = [
        "fenced_code",
        "tables",
        "sane_lists",
    ]
    return markdown.markdown(md_text, extensions=extensions)

def build_cover_page() -> str:
    """Generate the cover page HTML."""
    date_str = datetime.now().strftime("%B %Y")
    return f"""
    <div class="cover-page">
        <div class="book-title">BACKEND NOTES</div>
        <div class="book-subtitle">Systems Engineering</div>
        <hr class="book-divider">
        <p class="book-description">
            A structured knowledge base for building production backend systems.
            Engineering judgment over technology checklists.
        </p>
        <p class="book-meta">Generated {date_str}</p>
    </div>
    """

def build_toc(entries: list) -> str:
    """Generate the table of contents HTML with page counters."""
    html = '<div class="toc">\n<h1>CONTENTS</h1>\n'
    current_part = None

    for entry in entries:
        meta = entry["meta"]
        part_num = meta.get("part", 0)
        part_title = meta.get("part_title", "")
        doc_type = meta.get("type", "chapter")
        title = meta.get("title", "Untitled")
        chapter = meta.get("chapter")

        if part_num != current_part:
            current_part = part_num
            roman = PART_NUMBERS_ROMAN.get(part_num, str(part_num))
            html += f'<div class="toc-part">Part {roman}: {part_title}</div>\n'

        if doc_type != "part_intro" and chapter is not None:
            chapter_id = f"chap-{part_num}-{chapter}"
            html += (
                f'<div class="toc-chapter">'
                f'<a href="#{chapter_id}">'
                f'<span class="toc-num">{chapter}.</span> {title}'
                f'</a>'
                f'</div>\n'
            )

    html += "</div>\n"
    return html

def build_part_divider(part_num: int, part_title: str, summary: str = "") -> str:
    """Generate a part divider page."""
    roman = PART_NUMBERS_ROMAN.get(part_num, str(part_num))
    summary_html = ""
    clean_sum = clean_summary(summary)
    if clean_sum:
        summary_html = f'<p class="part-summary">{clean_sum}</p>'

    return f"""
    <div class="part-divider">
        <div class="part-number">PART {roman}</div>
        <div class="part-title">{part_title}</div>
        <hr class="part-rule">
        {summary_html}
    </div>
    """

def build_part_intro(meta: dict, html_content: str) -> str:
    """Generate a part introduction section (from README)."""
    return f"""
    <div class="part-intro">
        <div class="part-intro-label">PART OVERVIEW</div>
        {html_content}
    </div>
    """

def build_chapter(meta: dict, html_content: str) -> str:
    """Generate a chapter section."""
    title = meta.get("title", "Untitled")
    chapter = meta.get("chapter", "")
    part = meta.get("part", 0)

    roman = PART_NUMBERS_ROMAN.get(part, "")
    chapter_id = f"chap-{part}-{chapter}"

    return f"""
    <div class="chapter" id="{chapter_id}">
        <div class="chapter-header">
            <div class="chapter-label">PART {roman} - CHAPTER {chapter}</div>
            <div class="chapter-title">{title}</div>
        </div>
        {html_content}
    </div>
    """

def build_full_html(entries: list) -> str:
    """Assemble the complete HTML document."""
    cover = build_cover_page()
    toc = build_toc(entries)

    content_sections = []
    current_part = None

    for entry in entries:
        meta = entry["meta"]
        html_content = entry["html"]
        part_num = meta.get("part", 0)
        part_title = meta.get("part_title", "")
        doc_type = meta.get("type", "chapter")
        summary = meta.get("summary", "")

        if part_num != current_part:
            current_part = part_num
            content_sections.append(
                build_part_divider(part_num, part_title, summary)
            )

        if doc_type == "part_intro":
            content_sections.append(build_part_intro(meta, html_content))
        else:
            content_sections.append(build_chapter(meta, html_content))

    body_content = "\n".join(content_sections)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Backend Notes: Systems Engineering</title>
    <style>
{BOOK_CSS}
    </style>
</head>
<body>
    {cover}
    {toc}
    {body_content}
</body>
</html>
"""

def generate_book_pdf(output_path: Path, html_only: bool = False) -> None:
    """Read markdown notes, sanitize, format, and generate the book."""
    entries = []

    for rel_path, part, part_title, chapter, doc_type in FILES_CONFIG:
        filepath = BASE_DIR / rel_path
        if not filepath.exists():
            continue

        content = filepath.read_text(encoding="utf-8")
        meta, body = parse_frontmatter(content)

        meta.setdefault("part", part)
        meta.setdefault("part_title", part_title)
        meta.setdefault("type", doc_type)
        if chapter is not None:
            meta.setdefault("chapter", chapter)

        if "title" not in meta:
            for line in body.splitlines():
                if line.strip().startswith("# "):
                    meta["title"] = line.strip()[2:].strip()
                    break

        # Process / Clean content for PDF builder:
        # 1. Auto-sanitize unicode
        body = sanitize_content(body)
        
        # 2. Auto-convert spelling to InE
        body = convert_content(body)
        
        # 3. Dynamic untruncated summary
        full_summary = extract_untruncated_summary(body)
        if full_summary:
            meta["summary"] = full_summary

        cleaned_body = clean_markdown_body(body)
        html_content = md_to_html(cleaned_body)

        entries.append({
            "path": rel_path,
            "meta": meta,
            "html": html_content,
        })

    full_html = build_full_html(entries)

    if html_only:
        html_output = output_path.with_suffix(".html")
        html_output.write_text(full_html, encoding="utf-8")
        print(f"  [OK] HTML saved to: {html_output}")
        return

    # Render PDF using WeasyPrint
    import weasyprint
    print("Converting HTML to PDF with WeasyPrint...")
    weasyprint.HTML(string=full_html, base_url=str(BASE_DIR)).write_pdf(str(output_path))
    print(f"  [OK] PDF generated: {output_path}")
