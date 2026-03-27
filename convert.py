"""Convert documents to WCAG 2.1 AA accessible HTML."""

import argparse
import os
import sys
from pathlib import Path

from extractors.llamaparse_extractor import LlamaParseExtractor
from postprocessing.md_to_html import convert_markdown_to_html
from evaluation.accessibility_audit import audit_file

SUPPORTED_EXTENSIONS = {
    ".pdf", ".docx", ".doc", ".pptx", ".ppt", ".xlsx", ".xls",
    ".html", ".htm", ".txt", ".rtf", ".epub", ".md",
    ".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".webp",
}


def convert_file(file_path: Path, output_dir: Path, api_key: str):
    """Convert a single document to accessible HTML."""
    print(f"  Extracting: {file_path.name}")
    extractor = LlamaParseExtractor(api_key=api_key)
    result = extractor.extract(file_path)

    title = file_path.stem.replace("-", " ").replace("_", " ")
    html = convert_markdown_to_html(
        md_text=result.markdown,
        title=title,
        approach="LlamaParse",
    )

    # Save HTML
    html_path = output_dir / f"{file_path.stem}.html"
    html_path.write_text(html, encoding="utf-8")

    # Save markdown
    md_path = output_dir / f"{file_path.stem}.md"
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


def find_files(input_path: Path) -> list[Path]:
    """Find supported files from a path (file or directory)."""
    if input_path.is_file():
        if input_path.suffix.lower() in SUPPORTED_EXTENSIONS:
            return [input_path]
        else:
            print(f"Error: {input_path.suffix} is not a supported file type")
            print(f"Supported: {', '.join(sorted(SUPPORTED_EXTENSIONS))}")
            sys.exit(1)
    elif input_path.is_dir():
        files = []
        for ext in SUPPORTED_EXTENSIONS:
            files.extend(input_path.glob(f"*{ext}"))
        return sorted(set(files))
    else:
        print(f"Error: {input_path} does not exist")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Convert documents to WCAG 2.1 AA accessible HTML."
    )
    parser.add_argument("input", help="Document file or directory of documents")
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

    files = find_files(input_path)

    if not files:
        print(f"No supported files found in {input_path}")
        sys.exit(1)

    print(f"Converting {len(files)} file(s) -> {output_dir}/\n")

    all_passed = True
    for file_path in files:
        if not convert_file(file_path, output_dir, args.api_key):
            all_passed = False
        print()

    print(f"Output saved to {output_dir}/")
    if all_passed:
        print("All accessibility audits passed.")


if __name__ == "__main__":
    main()
