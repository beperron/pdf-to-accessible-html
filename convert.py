"""Convert PDF files to WCAG 2.1 AA accessible HTML."""

import argparse
import os
import sys
from pathlib import Path

from extractors.llamaparse_extractor import LlamaParseExtractor
from postprocessing.md_to_html import convert_markdown_to_html
from evaluation.accessibility_audit import audit_file


def convert_pdf(pdf_path: Path, output_dir: Path, api_key: str):
    """Convert a single PDF to accessible HTML."""
    print(f"  Extracting: {pdf_path.name}")
    extractor = LlamaParseExtractor(api_key=api_key)
    result = extractor.extract(pdf_path)

    title = pdf_path.stem.replace("-", " ").replace("_", " ")
    html = convert_markdown_to_html(
        md_text=result.markdown,
        title=title,
        approach="LlamaParse",
    )

    # Save HTML
    html_path = output_dir / f"{pdf_path.stem}.html"
    html_path.write_text(html, encoding="utf-8")

    # Save markdown
    md_path = output_dir / f"{pdf_path.stem}.md"
    md_path.write_text(result.markdown, encoding="utf-8")

    # Audit
    audit = audit_file(html_path)
    passed = all(audit.values())
    status = "PASS" if passed else "FAIL"

    print(f"  Done: {result.page_count} pages, {result.elapsed_seconds:.1f}s, audit: {status}")

    if not passed:
        for check, ok in audit.items():
            if not ok:
                print(f"    FAIL: {check}")

    return passed


def main():
    parser = argparse.ArgumentParser(
        description="Convert PDFs to WCAG 2.1 AA accessible HTML."
    )
    parser.add_argument("input", help="PDF file or directory of PDFs")
    parser.add_argument(
        "-o", "--output", default="output",
        help="Output directory (default: ./output)",
    )
    parser.add_argument(
        "-k", "--api-key",
        default=os.environ.get("LLAMA_CLOUD_API_KEY", ""),
        help="LlamaParse API key (or set LLAMA_CLOUD_API_KEY env var)",
    )
    args = parser.parse_args()

    if not args.api_key:
        print("Error: provide an API key with -k or set LLAMA_CLOUD_API_KEY")
        print("Get a free key at https://cloud.llamaindex.ai")
        sys.exit(1)

    input_path = Path(args.input)
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    if input_path.is_file() and input_path.suffix.lower() == ".pdf":
        pdf_files = [input_path]
    elif input_path.is_dir():
        pdf_files = sorted(input_path.glob("*.pdf"))
    else:
        print(f"Error: {input_path} is not a PDF file or directory")
        sys.exit(1)

    if not pdf_files:
        print(f"No PDF files found in {input_path}")
        sys.exit(1)

    print(f"Converting {len(pdf_files)} PDF(s) -> {output_dir}/\n")

    all_passed = True
    for pdf_path in pdf_files:
        if not convert_pdf(pdf_path, output_dir, args.api_key):
            all_passed = False
        print()

    print(f"Output saved to {output_dir}/")
    if all_passed:
        print("All accessibility audits passed.")


if __name__ == "__main__":
    main()
