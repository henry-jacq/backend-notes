import unittest
from pathlib import Path
from tools.config import BASE_DIR, FILES_CONFIG
from tools.pdf_builder import parse_frontmatter
from tools.spelling import check_content as spelling_check
from tools.sanitizer import check_content as sanitizer_check
from tools.lists import check_content as lists_check

class TestBookDocuments(unittest.TestCase):
    """Validation test suite to maintain high document formatting and spelling standards."""

    def test_frontmatter_integrity(self):
        """Verify that all configured files contain valid YAML frontmatter and required fields."""
        for rel_path, part, part_title, chapter, doc_type in FILES_CONFIG:
            filepath = BASE_DIR / rel_path
            with self.subTest(file=rel_path):
                self.assertTrue(filepath.exists(), f"File {rel_path} does not exist.")
                content = filepath.read_text(encoding="utf-8")
                
                # Check that it starts with YAML frontmatter delimiters
                self.assertTrue(
                    content.startswith("---"), 
                    f"File {rel_path} is missing frontmatter headers."
                )
                
                meta, body = parse_frontmatter(content)
                self.assertIsNotNone(meta, f"Failed to parse frontmatter in {rel_path}.")
                self.assertIn("title", meta, f"Missing 'title' in frontmatter of {rel_path}.")
                self.assertIn("part", meta, f"Missing 'part' in frontmatter of {rel_path}.")
                self.assertIn("part_title", meta, f"Missing 'part_title' in frontmatter of {rel_path}.")
                
                if doc_type == "chapter":
                    self.assertIn("chapter", meta, f"Missing 'chapter' number in frontmatter of {rel_path}.")
                    self.assertEqual(meta["chapter"], chapter, f"Chapter number mismatch in {rel_path}.")

    def test_unicode_arrow_safety(self):
        """Verify that markdown files contain no prohibited Unicode characters (which fail PDF rendering)."""
        violations_count = 0
        for rel_path, _, _, _, _ in FILES_CONFIG:
            filepath = BASE_DIR / rel_path
            if not filepath.exists():
                continue
            
            content = filepath.read_text(encoding="utf-8")
            violations = sanitizer_check(content)
            
            if violations:
                violations_count += len(violations)
                print(f"\n[Unicode Violation] {rel_path}:")
                for line_num, msg in violations:
                    print(f"  Line {line_num}: {msg}")
                    
        self.assertEqual(violations_count, 0, f"Found {violations_count} Unicode violations. Run sanitizer to fix.")

    def test_markdown_list_spacing(self):
        """Verify that all list blocks have a preceding empty line before them (required by Python-Markdown)."""
        violations_count = 0
        for rel_path, _, _, _, _ in FILES_CONFIG:
            filepath = BASE_DIR / rel_path
            if not filepath.exists():
                continue
            
            content = filepath.read_text(encoding="utf-8")
            violations = lists_check(content)
            
            if violations:
                violations_count += len(violations)
                print(f"\n[List Spacing Violation] {rel_path}:")
                for line_num, msg in violations:
                    print(f"  Line {line_num}: {msg}")
                    
        self.assertEqual(violations_count, 0, f"Found {violations_count} list spacing violations. Run list layout fixer to fix.")

    def test_indian_english_spelling_compliance(self):
        """Verify that prose text follows Indian English spelling (avoiding US variants optimize, behavior, center, etc.)."""
        violations_count = 0
        for rel_path, _, _, _, _ in FILES_CONFIG:
            filepath = BASE_DIR / rel_path
            if not filepath.exists():
                continue
            
            content = filepath.read_text(encoding="utf-8")
            violations = spelling_check(content)
            
            if violations:
                violations_count += len(violations)
                print(f"\n[Spelling Violation (American English)] {rel_path}:")
                for line_num, msg in violations:
                    print(f"  Line {line_num}: {msg}")
                    
        self.assertEqual(violations_count, 0, f"Found {violations_count} spelling violations. Run spelling converter to fix.")

if __name__ == "__main__":
    unittest.main()
