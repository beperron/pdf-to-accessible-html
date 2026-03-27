"""Final WCAG 2.1 AA accessibility pass."""

import re
from bs4 import BeautifulSoup, Tag


def apply_accessibility(soup: BeautifulSoup, title: str = "Document") -> BeautifulSoup:
    """Apply all accessibility enhancements to the HTML document."""
    _ensure_lang(soup)
    _add_skip_link(soup)
    _add_landmarks(soup, title)
    _generate_toc(soup)
    _verify_images(soup)
    _verify_tables(soup)
    _fix_links(soup)
    return soup


def _ensure_lang(soup: BeautifulSoup):
    """Ensure <html> has lang attribute."""
    html = soup.find("html")
    if html and not html.get("lang"):
        html["lang"] = "en"


def _add_skip_link(soup: BeautifulSoup):
    """Add 'Skip to main content' as first focusable element."""
    body = soup.find("body")
    if not body:
        return

    # Check if skip link already exists
    existing = body.find("a", class_="skip-link")
    if existing:
        return

    skip = BeautifulSoup(
        '<a href="#main-content" class="skip-link">Skip to main content</a>',
        "html.parser"
    )
    body.insert(0, skip)


def _add_landmarks(soup: BeautifulSoup, title: str):
    """Wrap content in proper landmark elements."""
    body = soup.find("body")
    if not body:
        return

    # Find or create <main>
    main = soup.find("main")
    if not main:
        main = soup.new_tag("main", id="main-content", role="main")
        # Move all body children (except skip link and nav) into main
        skip = body.find("a", class_="skip-link")
        nav = body.find("nav")
        children = list(body.children)
        body.append(main)
        for child in children:
            if child is skip or child is nav or child is main:
                continue
            main.append(child.extract())

    if not main.get("id"):
        main["id"] = "main-content"

    # Wrap main in <article> for paper content
    if not soup.find("article"):
        article = soup.new_tag("article", attrs={"aria-label": title})
        main_children = list(main.children)
        main.append(article)
        for child in main_children:
            if child is article:
                continue
            article.append(child.extract())


def _generate_toc(soup: BeautifulSoup):
    """Generate a table of contents nav from headings."""
    headings = soup.find_all(re.compile(r"^h[2-3]$"))
    if len(headings) < 3:
        return  # Too few headings for a TOC

    toc_items = []
    for h in headings:
        level = int(h.name[1])
        hid = h.get("id", "")
        text = h.get_text(strip=True)
        if hid and text:
            indent = "  " * (level - 2)
            toc_items.append(f'{indent}<li><a href="#{hid}">{text}</a></li>')

    if not toc_items:
        return

    toc_html = (
        '<nav aria-label="Table of Contents" class="toc">\n'
        '<h2 id="toc">Table of Contents</h2>\n'
        '<ul>\n' + "\n".join(toc_items) + '\n</ul>\n</nav>'
    )

    toc = BeautifulSoup(toc_html, "html.parser")

    # Insert before main content
    main = soup.find("main")
    if main:
        main.insert(0, toc)


def _verify_images(soup: BeautifulSoup):
    """Ensure all images have alt text."""
    for img in soup.find_all("img"):
        if not img.get("alt"):
            img["alt"] = "Scientific figure"


def _verify_tables(soup: BeautifulSoup):
    """Ensure all tables have captions or aria-labels."""
    for table in soup.find_all("table"):
        if not table.find("caption") and not table.get("aria-label"):
            table["aria-label"] = "Data table"


def _make_link_descriptive(href: str) -> str:
    """Generate descriptive link text from a URL."""
    if not href:
        return "External link"

    # DOI links
    doi_match = re.match(r"https?://doi\.org/(.*)", href)
    if doi_match:
        return f"Reference (DOI: {doi_match.group(1)})"

    # arXiv links
    arxiv_match = re.match(r"https?://arxiv\.org/abs/(.*)", href)
    if arxiv_match:
        return f"arXiv paper {arxiv_match.group(1)}"

    # Known domains with friendly names
    domain = href.split("//", 1)[-1].split("/", 1)[0] if "//" in href else ""
    domain_names = {
        "www.python.org": "Python official website",
        "python.org": "Python official website",
        "code.visualstudio.com": "Visual Studio Code website",
        "platform.openai.com": "OpenAI API documentation",
        "www.census.gov": "U.S. Census Bureau",
        "www.ncbi.nlm.nih.gov": "NCBI (National Center for Biotechnology Information)",
        "github.com": "GitHub repository",
        "huggingface.co": "Hugging Face model page",
        "llamaindex.ai": "LlamaIndex website",
    }
    if domain in domain_names:
        return domain_names[domain]

    # Generic: use cleaned domain
    if domain:
        clean = domain.replace("www.", "")
        return f"Visit {clean} (external link)"

    return "External link"


def _fix_links(soup: BeautifulSoup):
    """Ensure all links have descriptive visible text and title attributes."""
    for a in soup.find_all("a"):
        href = a.get("href", "")
        text = a.get_text(strip=True)

        # Skip anchor links (TOC, skip nav) — just add title
        if href.startswith("#"):
            if not a.get("title"):
                a["title"] = f"Jump to {text}" if text else "Jump to section"
            continue

        # Fix bare URLs used as link text
        is_bare_url = text.startswith("http://") or text.startswith("https://")
        is_empty = not text
        is_generic = text.lower() in ("here", "click here", "link", "this", "more", "read more")

        if is_bare_url or is_empty or is_generic:
            descriptive = _make_link_descriptive(href)
            a.string = descriptive
            a["title"] = descriptive
        elif not a.get("title"):
            a["title"] = text if text else "Link"
