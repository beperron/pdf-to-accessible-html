"""Repair and normalize heading hierarchy for accessibility."""

import re
from collections import Counter
from bs4 import BeautifulSoup, Tag

# Patterns that indicate PDF headers/footers, not real content headings
HEADER_FOOTER_PATTERNS = re.compile(
    r"(^Journal of|^Research on Social Work|^JOURNAL OF"
    r"|^Summer \d{4}|^Fall \d{4}|^Winter \d{4}|^Spring \d{4}"
    r"|^\d+\s*$"  # bare page numbers
    r"|^[A-Z\s]{20,}$"  # ALL CAPS journal names
    r"|EVIDENCE.BASED SOCIAL WORK"
    r"|Society for Social Work"
    r"|\d+\(\d+\)$)",  # volume(issue) like "35(6)"
    re.IGNORECASE,
)

# Spaced-out text like "A B S T R A C T" or "K E Y W O R D S"
SPACED_TEXT = re.compile(r"^([A-Z] ){3,}")

# Series/journal headers that should not be paper titles
SERIES_HEADERS = re.compile(
    r"(artificial\s*intelligence|social\s*work\s*series"
    r"|evidence.based\s*social\s*work"
    r"|abstract$|keywords?$|references$)",
    re.IGNORECASE,
)


def process_headings(soup: BeautifulSoup) -> BeautifulSoup:
    """Ensure proper heading hierarchy: single h1, sequential levels, IDs."""
    headings = soup.find_all(re.compile(r"^h[1-6]$"))
    if not headings:
        return soup

    # Step 1: Remove PDF header/footer headings (repeated journal names, dates)
    _remove_header_footer_headings(soup)

    # Step 2: Deduplicate repeated h1s — keep the first unique one as h1,
    # demote exact duplicates
    _deduplicate_headings(soup)

    # Step 3: Fix spaced-out text ("A B S T R A C T" → "ABSTRACT")
    _fix_spaced_headings(soup)

    # Re-gather after removals
    headings = soup.find_all(re.compile(r"^h[1-6]$"))
    if not headings:
        return soup

    # Step 4: Ensure single h1, and it should be the actual paper title
    h1s = soup.find_all("h1")
    if not h1s and headings:
        headings[0].name = "h1"
    elif len(h1s) >= 1:
        # Find the best h1 — skip series headers, journal names, "Abstract", etc.
        best_h1 = None
        for h1 in h1s:
            text = h1.get_text(strip=True)
            if not SERIES_HEADERS.search(text) and len(text) > 10:
                best_h1 = h1
                break
        if best_h1 is None:
            best_h1 = h1s[0]  # fallback to first
        # Demote all others
        for h1 in h1s:
            if h1 is not best_h1:
                h1.name = "h2"

    # Step 5: Repair skipped levels
    headings = soup.find_all(re.compile(r"^h[1-6]$"))
    if len(headings) > 1:
        levels = [int(h.name[1]) for h in headings]
        remapped = _fix_hierarchy(levels)
        for heading, new_level in zip(headings, remapped):
            heading.name = f"h{new_level}"

    # Step 6: Truncate headings longer than 120 characters
    _truncate_long_headings(soup)

    _add_ids(headings)
    return soup


def _truncate_long_headings(soup: BeautifulSoup):
    """Truncate headings to max 120 characters at a word boundary."""
    max_len = 115  # slightly under 120 to account for "..."
    for h in soup.find_all(re.compile(r"^h[1-6]$")):
        text = h.get_text(strip=True)
        if len(text) > max_len:
            # Truncate at last space before limit
            truncated = text[:max_len].rsplit(" ", 1)[0]
            if not truncated:
                truncated = text[:max_len]
            h.string = truncated + "..."


def _remove_header_footer_headings(soup: BeautifulSoup):
    """Remove headings that are PDF headers/footers."""
    for h in soup.find_all(re.compile(r"^h[1-6]$")):
        text = h.get_text(strip=True)
        if HEADER_FOOTER_PATTERNS.search(text):
            # Convert to a non-heading paragraph to preserve text if needed
            h.name = "p"
            h["class"] = h.get("class", []) + ["pdf-header"]


def _deduplicate_headings(soup: BeautifulSoup):
    """Demote exact duplicate headings — keep first occurrence at its level."""
    headings = soup.find_all(re.compile(r"^h[1-6]$"))
    seen_texts = {}
    for h in headings:
        text = h.get_text(strip=True).lower()
        if text in seen_texts:
            seen_texts[text] += 1
            # If it's appeared 3+ times, it's likely a repeated header — remove
            if seen_texts[text] >= 3:
                h.name = "p"
                h["class"] = h.get("class", []) + ["pdf-header"]
        else:
            seen_texts[text] = 1


def _fix_spaced_headings(soup: BeautifulSoup):
    """Fix spaced-out headings like 'A B S T R A C T' → 'Abstract'."""
    for h in soup.find_all(re.compile(r"^h[1-6]$")):
        text = h.get_text(strip=True)
        if SPACED_TEXT.match(text):
            collapsed = text.replace(" ", "")
            h.string = collapsed.title()


def _fix_hierarchy(levels: list[int]) -> list[int]:
    """Remap heading levels so none are skipped."""
    if not levels:
        return levels

    result = []
    stack = [0]
    for lvl in levels:
        if lvl <= stack[-1]:
            while len(stack) > 1 and stack[-1] >= lvl:
                stack.pop()
            result.append(lvl)
            stack.append(lvl)
        else:
            new_lvl = min(lvl, stack[-1] + 1)
            result.append(new_lvl)
            stack.append(new_lvl)

    # Ensure first heading is h1
    if result and result[0] != 1:
        offset = result[0] - 1
        result = [max(1, r - offset) for r in result]

    return result


def _add_ids(headings: list[Tag]):
    """Add slugified IDs for TOC anchor linking."""
    seen = {}
    for h in headings:
        text = h.get_text(strip=True)
        slug = re.sub(r"[^\w\s-]", "", text.lower())
        slug = re.sub(r"[\s]+", "-", slug).strip("-")
        if not slug:
            slug = "section"

        if slug in seen:
            seen[slug] += 1
            slug = f"{slug}-{seen[slug]}"
        else:
            seen[slug] = 0

        h["id"] = slug
