"""Process figures: wrap in <figure>/<figcaption>, generate alt text."""

import re
from pathlib import Path
from bs4 import BeautifulSoup, Tag


def process_figures(soup: BeautifulSoup, images_dir: Path = None,
                    alt_text_generator=None) -> BeautifulSoup:
    """Wrap images in <figure> elements with captions and alt text."""
    imgs = soup.find_all("img")

    for img in imgs:
        _wrap_in_figure(img, images_dir, alt_text_generator)

    return soup


def _wrap_in_figure(img: Tag, images_dir: Path = None,
                    alt_text_generator=None):
    """Wrap an <img> in <figure> with <figcaption>."""
    # Skip if already inside a <figure>
    if img.find_parent("figure"):
        return

    # Generate or improve alt text
    alt = img.get("alt", "")
    src = img.get("src", "")

    if (not alt or alt == src) and alt_text_generator and images_dir:
        # Try to find the image file and generate alt text
        img_file = _find_image_file(src, images_dir)
        if img_file:
            alt = alt_text_generator(img_file)
            img["alt"] = alt

    if not alt:
        img["alt"] = f"Figure from scientific paper"

    # Extract caption from surrounding text
    caption_text = _extract_caption(img)

    # Ensure a caption always exists
    if not caption_text:
        caption_text = alt if alt and alt != "Figure from scientific paper" else "Figure from scientific paper"

    # Create figure wrapper
    figure_html = f'<figure>'
    figure_html += str(img)
    figure_html += f'<figcaption>{caption_text}</figcaption>'
    figure_html += '</figure>'

    figure = BeautifulSoup(figure_html, "html.parser").find("figure")
    img.replace_with(figure)


def _find_image_file(src: str, images_dir: Path) -> Path | None:
    """Try to resolve an image src to a local file path."""
    if not images_dir or not images_dir.exists():
        return None

    # Try direct path
    p = images_dir / Path(src).name
    if p.exists():
        return p

    # Try matching by stem
    stem = Path(src).stem
    for f in images_dir.iterdir():
        if f.stem == stem:
            return f

    return None


def _extract_caption(img: Tag) -> str:
    """Try to find a figure caption near the image."""
    # Check for adjacent text with "Figure N" or "Fig. N"
    caption = ""

    # Check next sibling
    next_sib = img.find_next_sibling()
    if next_sib:
        text = next_sib.get_text(strip=True) if hasattr(next_sib, "get_text") else str(next_sib).strip()
        if re.match(r"^(Figure|Fig\.?)\s+\d+", text, re.IGNORECASE):
            caption = text

    # Check parent's next sibling
    if not caption and img.parent:
        next_sib = img.parent.find_next_sibling()
        if next_sib:
            text = next_sib.get_text(strip=True) if hasattr(next_sib, "get_text") else str(next_sib).strip()
            if re.match(r"^(Figure|Fig\.?)\s+\d+", text, re.IGNORECASE):
                caption = text

    # Check alt text for caption content (from markdown ![caption](url))
    if not caption:
        alt = img.get("alt", "")
        if alt and not alt.startswith("Figure from"):
            caption = alt

    return caption
