"""Automated WCAG 2.1 AA accessibility checks on output HTML."""

import re
from pathlib import Path
from bs4 import BeautifulSoup


def audit_file(html_path: Path) -> dict[str, bool]:
    """Run accessibility checks on an HTML file. Returns {check_name: passed}."""
    html = html_path.read_text(encoding="utf-8")
    soup = BeautifulSoup(html, "html.parser")

    return {
        "lang_attribute": _check_lang(soup),
        "skip_navigation": _check_skip_nav(soup),
        "main_landmark": _check_main(soup),
        "images_have_alt": _check_img_alt(soup),
        "tables_have_caption": _check_table_caption(soup),
        "th_have_scope": _check_th_scope(soup),
        "heading_hierarchy": _check_heading_hierarchy(soup),
        "title_element": _check_title(soup),
    }


def _check_lang(soup: BeautifulSoup) -> bool:
    html = soup.find("html")
    return bool(html and html.get("lang"))


def _check_skip_nav(soup: BeautifulSoup) -> bool:
    link = soup.find("a", class_="skip-link")
    if link:
        return True
    # Also check for any link targeting #main
    return bool(soup.find("a", href=re.compile(r"#main")))


def _check_main(soup: BeautifulSoup) -> bool:
    return bool(soup.find("main"))


def _check_img_alt(soup: BeautifulSoup) -> bool:
    imgs = soup.find_all("img")
    if not imgs:
        return True  # No images = no violations
    return all(img.get("alt") for img in imgs)


def _check_table_caption(soup: BeautifulSoup) -> bool:
    tables = soup.find_all("table")
    if not tables:
        return True
    return all(
        t.find("caption") or t.get("aria-label")
        for t in tables
    )


def _check_th_scope(soup: BeautifulSoup) -> bool:
    ths = soup.find_all("th")
    if not ths:
        return True
    return all(th.get("scope") for th in ths)


def _check_heading_hierarchy(soup: BeautifulSoup) -> bool:
    # Skip headings inside <nav> (e.g. TOC) — they are independent
    headings = [
        h for h in soup.find_all(re.compile(r"^h[1-6]$"))
        if not h.find_parent("nav")
    ]
    if len(headings) <= 1:
        return True

    levels = [int(h.name[1]) for h in headings]

    # Check no level is skipped going down
    for i in range(1, len(levels)):
        if levels[i] > levels[i - 1] + 1:
            return False
    return True


def _check_title(soup: BeautifulSoup) -> bool:
    return bool(soup.find("title") and soup.find("title").string)


def audit_all(html_dir: Path) -> list[dict]:
    """Audit all HTML files in a directory tree."""
    results = []
    for html_file in sorted(html_dir.rglob("*.html")):
        if html_file.name == "index.html":
            continue
        checks = audit_file(html_file)
        # Determine approach from path
        approach = html_file.parent.name
        results.append({
            "name": html_file.stem,
            "approach": approach,
            "checks": checks,
            "all_passed": all(checks.values()),
        })
    return results
