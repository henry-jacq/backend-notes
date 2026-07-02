#!/usr/bin/env python3
"""
Backend Notes: PDF Book Compiler and Validator

This script acts as the main entry point to format, validate and compile
the repository markdown notes into a premium PDF book.

Usage:
    python build_book.py                   # Compile the PDF book
    python build_book.py --check           # Check formatting and spelling compliance
    python build_book.py --fix             # Automatically fix layout/spelling in files
    python build_book.py --html-only       # Debug output to HTML only
"""

import sys
import argparse
from pathlib import Path
import unittest

# Import our modular tooling
from tools.config import BASE_DIR, FILES_CONFIG
from tools.pdf_builder import generate_book_pdf
from tools.sanitizer import sanitize_content
from tools.lists import fix_content as fix_list_content
from tools.spelling import convert_content as convert_spelling_content

def run_compliance_checks():
    """Execute the unittest validation suite."""
    print("=" * 60)
    print("  Running Compliance and Validation Checks")
    print("=" * 60)
    
    # Import and load TestBookDocuments
    from tools.tests import TestBookDocuments
    suite = unittest.TestLoader().loadTestsFromTestCase(TestBookDocuments)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    if not result.wasSuccessful():
        print("\n[ERROR] Validation checks failed. Run with --fix or check warnings above.")
        sys.exit(1)
    else:
        print("\n[SUCCESS] All document formatting and InE spelling checks passed!")

def run_auto_fixes():
    """Automatically fix spelling, list layout and unicode arrows inside source files."""
    print("=" * 60)
    print("  Running Layout and Spelling Auto-Fixer")
    print("=" * 60)
    
    fixes_applied = 0
    
    for rel_path, _, _, _, _ in FILES_CONFIG:
        filepath = BASE_DIR / rel_path
        if not filepath.exists():
            continue
            
        content = filepath.read_text(encoding="utf-8")
        modified = False
        
        # 1. Fix Unicode arrows
        sanitized = sanitize_content(content)
        if sanitized != content:
            content = sanitized
            modified = True
            
        # 2. Fix unbroken lists
        fixed_lists, list_changes = fix_list_content(content)
        if list_changes > 0:
            content = fixed_lists
            modified = True
            
        # 3. Convert US spellings to InE
        converted_spelling = convert_spelling_content(content)
        if converted_spelling != content:
            content = converted_spelling
            modified = True
            
        if modified:
            filepath.write_text(content, encoding="utf-8")
            print(f"  [FIXED] Layout & spelling updated in: {rel_path}")
            fixes_applied += 1
            
    print(f"\nDone. Cleaned and formatted {fixes_applied} files.")

def main():
    parser = argparse.ArgumentParser(
        description="Compile and Validate Backend Notes Book"
    )
    parser.add_argument(
        "--output", "-o",
        default="backend_notes.pdf",
        help="Output PDF path (default: backend_notes.pdf)"
    )
    parser.add_argument(
        "--html-only",
        action="store_true",
        help="Generate only HTML output for debugging"
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Run document formatting and spelling tests"
    )
    parser.add_argument(
        "--fix",
        action="store_true",
        help="Automatically fix formatting and InE spelling inside source markdown files"
    )
    args = parser.parse_args()
    
    if args.check:
        run_compliance_checks()
        return
        
    if args.fix:
        run_auto_fixes()
        return

    # Default: build the book PDF
    output_path = Path(args.output).resolve()
    print("=" * 60)
    print("  Backend Notes -- PDF Book Compiler")
    print("=" * 60)
    print(f"Target: {output_path}")
    print()
    
    try:
        import logging
        logging.basicConfig(level=logging.WARNING)
        generate_book_pdf(output_path, html_only=args.html_only)
    except Exception as e:
        print(f"\n[ERROR] Failed to compile book: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
