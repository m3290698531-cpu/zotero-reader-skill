#!/usr/bin/env python3
"""
Extract text content from a PDF file.
Usage: python extract_pdf_text.py <pdf_path> [--pages 1-10] [--output output.txt]
"""

import argparse
import sys


def extract_text(pdf_path, page_range=None):
    """Extract text from PDF using PyMuPDF (fitz)."""
    try:
        import fitz  # PyMuPDF
    except ImportError:
        print("ERROR: PyMuPDF not installed. Install with: pip install pymupdf", file=sys.stderr)
        sys.exit(1)

    doc = fitz.open(pdf_path)
    total_pages = len(doc)

    # Parse page range
    if page_range:
        if '-' in page_range:
            start, end = page_range.split('-')
            start = max(1, int(start))
            end = min(total_pages, int(end))
        else:
            start = int(page_range)
            end = start
    else:
        start = 1
        end = total_pages

    results = []
    for page_num in range(start - 1, end):
        page = doc[page_num]
        text = page.get_text()
        results.append({
            'page': page_num + 1,
            'text': text,
        })

    doc.close()
    return {
        'total_pages': total_pages,
        'extracted_from': start,
        'extracted_to': end,
        'pages': results,
    }


def main():
    parser = argparse.ArgumentParser(description='Extract text from PDF')
    parser.add_argument('pdf_path', help='Path to PDF file')
    parser.add_argument('--pages', help='Page range, e.g. "1-10" or "5" (default: all)')
    parser.add_argument('--output', help='Output file path (default: stdout)')
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    args = parser.parse_args()

    result = extract_text(args.pdf_path, args.pages)

    if args.json:
        import json
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        output = []
        for p in result['pages']:
            output.append(f"--- Page {p['page']} ---\n{p['text']}")
        text = '\n\n'.join(output)

        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(text)
            print(f"Extracted {len(result['pages'])} pages to {args.output}")
        else:
            print(text)


if __name__ == '__main__':
    main()
