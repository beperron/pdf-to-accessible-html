"""Base extractor interface and shared data structures."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class ExtractionResult:
    """Result from a single document extraction."""
    pdf_name: str  # kept for backwards compatibility; holds any document stem
    markdown: str
    images: list[Path] = field(default_factory=list)
    page_count: int = 0
    elapsed_seconds: float = 0.0
    extractor: str = ""

    def save_markdown(self, output_path: Path):
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(self.markdown, encoding="utf-8")

    def save_images(self, output_dir: Path):
        output_dir.mkdir(parents=True, exist_ok=True)
        # Images are already saved during extraction; this records the dir
        return output_dir


class BaseExtractor(ABC):
    """Abstract base for document extraction approaches."""

    name: str = "base"

    @abstractmethod
    def extract(self, file_path: Path) -> ExtractionResult:
        """Extract markdown + images from a document."""
        ...

    def extract_images_pymupdf(self, pdf_path: Path, output_dir: Path) -> list[Path]:
        """Extract embedded images from PDF using PyMuPDF."""
        import fitz

        output_dir.mkdir(parents=True, exist_ok=True)
        saved = []
        doc = fitz.open(pdf_path)
        seen_xrefs = set()

        for page_num in range(len(doc)):
            page = doc[page_num]
            for img_info in page.get_images(full=True):
                xref = img_info[0]
                if xref in seen_xrefs:
                    continue
                seen_xrefs.add(xref)

                base_image = doc.extract_image(xref)
                if base_image["image"] is None:
                    continue

                ext = base_image.get("ext", "png")
                img_path = output_dir / f"page{page_num + 1}_img{xref}.{ext}"
                img_path.write_bytes(base_image["image"])
                saved.append(img_path)

        doc.close()
        return saved
