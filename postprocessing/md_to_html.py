"""Orchestrator: Markdown -> Accessible HTML pipeline."""

import re
from pathlib import Path

import markdown as md_lib
from bs4 import BeautifulSoup
from jinja2 import Environment, FileSystemLoader

import config
from .heading_processor import process_headings
from .math_processor import process_math
from .table_processor import process_tables
from .figure_processor import process_figures
from .accessibility import apply_accessibility

# Headings to skip when extracting the paper title
_SKIP_TITLE_PAT = re.compile(
    r"(^artificial\s*intelligence|social\s*work\s*series|evidence.based"
    r"|^abstract$|^keywords?:?$|^references$|^introduction$|^conclusion$"
    r"|^table of contents$|^journal of|^figures$|^equations$"
    r"|^method$|^results$|^discussion$|^recommendations$"
    r"|^study overview$|^test conditions$)",
    re.IGNORECASE,
)


def _read_css() -> str:
    """Read the accessible.css file for inlining into output HTML."""
    css_path = config.STATIC_DIR / "css" / "accessible.css"
    return css_path.read_text(encoding="utf-8")


def convert_markdown_to_html(
    md_text: str,
    title: str,
    approach: str = "llamaparse",
    images_dir: Path = None,
    alt_text_generator=None,
) -> str:
    """Convert markdown to fully accessible, self-contained HTML."""
    # Step 1: Markdown to raw HTML
    extensions = ["tables", "toc", "fenced_code", "attr_list", "md_in_html"]
    raw_html = md_lib.markdown(md_text, extensions=extensions)

    # Step 2: Parse and process
    soup = BeautifulSoup(raw_html, "html.parser")
    soup = process_math(soup)
    soup = process_tables(soup)
    soup = process_figures(soup, images_dir, alt_text_generator)
    soup = process_headings(soup)

    # Step 2b: Extract actual paper title from content headings
    for tag in ["h1", "h2"]:
        for h in soup.find_all(tag):
            if h.find_parent("nav"):
                continue
            candidate = h.get_text(strip=True)
            if len(candidate) > 20 and not _SKIP_TITLE_PAT.search(candidate):
                title = candidate
                break
        else:
            continue
        break

    # Step 3: Render into template with inline CSS
    env = Environment(
        loader=FileSystemLoader(str(config.TEMPLATE_DIR)),
        autoescape=False,
    )
    template = env.get_template("paper.html")

    rendered = template.render(
        title=title,
        content=str(soup),
        approach=approach,
        mathjax_cdn=config.MATHJAX_CDN,
        css_inline=_read_css(),
    )

    # Step 4: Final accessibility pass
    full_soup = BeautifulSoup(rendered, "html.parser")
    full_soup = apply_accessibility(full_soup, title)

    return str(full_soup)
