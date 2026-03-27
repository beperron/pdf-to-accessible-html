"""LlamaParse-based document extraction."""

import time
import tempfile
from pathlib import Path

from .base import BaseExtractor, ExtractionResult


class LlamaParseExtractor(BaseExtractor):
    name = "llamaparse"

    def __init__(self, api_key: str):
        self.api_key = api_key

    def extract(self, file_path: Path, images_dir: Path = None) -> ExtractionResult:
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
        documents = parser.load_data(str(file_path))
        elapsed = time.time() - start

        markdown = "\n\n".join(doc.text for doc in documents)

        # Extract images and page count via PyMuPDF (PDF only)
        images = []
        page_count = 0
        if file_path.suffix.lower() == ".pdf":
            if images_dir is None:
                images_dir = Path(tempfile.mkdtemp()) / file_path.stem
            images = self.extract_images_pymupdf(file_path, images_dir)

            import fitz
            doc = fitz.open(file_path)
            page_count = len(doc)
            doc.close()
        else:
            # Estimate page count from LlamaParse document chunks
            page_count = len(documents) if documents else 1

        return ExtractionResult(
            pdf_name=file_path.stem,
            markdown=markdown,
            images=images,
            page_count=page_count,
            elapsed_seconds=elapsed,
            extractor=self.name,
        )
