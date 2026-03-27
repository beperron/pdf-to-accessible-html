"""LlamaParse-based document extraction."""

import time
import tempfile
from pathlib import Path

from .base import BaseExtractor, ExtractionResult

SYSTEM_PROMPT = (
    "Extract equations as LaTeX ($...$, $$...$$). "
    "Preserve table structure with markdown pipe syntax. "
    "Identify figures with descriptive captions. "
    "Maintain heading hierarchy."
)

# Parsing modes and their approximate credit costs per page.
# See https://docs.cloud.llamaindex.ai/llamaparse/getting_started
MODES = {
    "fast": {
        "description": "Standard parsing (~3 credits/page)",
        "config": {
            "result_type": "markdown",
            "auto_mode": False,
            "extract_charts": True,
            "system_prompt": SYSTEM_PROMPT,
        },
    },
    "default": {
        "description": "Auto mode — upgrades complex pages automatically (~3-10 credits/page)",
        "config": {
            "result_type": "markdown",
            "auto_mode": True,
            "auto_mode_trigger_on_table_in_page": True,
            "auto_mode_trigger_on_image_in_page": True,
            "extract_charts": True,
            "annotate_links": True,
            "merge_tables_across_pages_in_markdown": True,
            "system_prompt": SYSTEM_PROMPT,
        },
    },
    "quality": {
        "description": "Agentic parsing — best accuracy for complex documents (~10 credits/page)",
        "config": {
            "result_type": "markdown",
            "preset": "agentic",
            "extract_charts": True,
            "annotate_links": True,
            "merge_tables_across_pages_in_markdown": True,
            "system_prompt": SYSTEM_PROMPT,
        },
    },
}


class LlamaParseExtractor(BaseExtractor):
    name = "llamaparse"

    def __init__(self, api_key: str, mode: str = "default"):
        self.api_key = api_key
        if mode not in MODES:
            raise ValueError(f"Unknown mode '{mode}'. Choose from: {', '.join(MODES)}")
        self.mode = mode

    def extract(self, file_path: Path, images_dir: Path = None) -> ExtractionResult:
        from llama_parse import LlamaParse

        config = MODES[self.mode]["config"]
        parser = LlamaParse(api_key=self.api_key, **config)

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
            page_count = len(documents) if documents else 1

        return ExtractionResult(
            pdf_name=file_path.stem,
            markdown=markdown,
            images=images,
            page_count=page_count,
            elapsed_seconds=elapsed,
            extractor=self.name,
        )
