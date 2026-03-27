"""LlamaParse-based PDF extraction."""

import time
import tempfile
from pathlib import Path

from .base import BaseExtractor, ExtractionResult


class LlamaParseExtractor(BaseExtractor):
    name = "llamaparse"

    def __init__(self, api_key: str):
        self.api_key = api_key

    def extract(self, pdf_path: Path, images_dir: Path = None) -> ExtractionResult:
        from llama_parse import LlamaParse

        parser = LlamaParse(
            api_key=self.api_key,
            result_type="markdown",
            auto_mode=True,
            extract_charts=True,
            system_prompt=(
                "Extract equations as LaTeX ($...$, $$...$$). "
                "Preserve table structure with markdown pipe syntax. "
                "Identify figures with descriptive captions. "
                "Maintain heading hierarchy."
            ),
        )

        start = time.time()
        documents = parser.load_data(str(pdf_path))
        elapsed = time.time() - start

        markdown = "\n\n".join(doc.text for doc in documents)

        # Extract images via PyMuPDF
        if images_dir is None:
            images_dir = Path(tempfile.mkdtemp()) / pdf_path.stem
        images = self.extract_images_pymupdf(pdf_path, images_dir)

        import fitz
        doc = fitz.open(pdf_path)
        page_count = len(doc)
        doc.close()

        return ExtractionResult(
            pdf_name=pdf_path.stem,
            markdown=markdown,
            images=images,
            page_count=page_count,
            elapsed_seconds=elapsed,
            extractor=self.name,
        )
