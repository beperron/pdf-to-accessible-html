"""Make tables accessible: <thead>, <th scope>, <caption>."""

import re
from bs4 import BeautifulSoup, Tag


def process_tables(soup: BeautifulSoup) -> BeautifulSoup:
    """Add accessibility markup to all tables."""
    tables = soup.find_all("table")

    for table in tables:
        _add_thead(table)
        _add_scope(table)
        _add_caption(table)
        _ensure_caption(table)
        _add_role(table)

    return soup


def _add_thead(table: Tag):
    """Wrap the first row in <thead> if not already present."""
    if table.find("thead"):
        return

    rows = table.find_all("tr")
    if not rows:
        return

    first_row = rows[0]

    # Check if the first row looks like a header (all cells are <th> or
    # contain bold/strong text, or are in the first row of a simple table)
    cells = first_row.find_all(["td", "th"])
    is_header = all(c.name == "th" for c in cells) or len(rows) > 1

    if is_header:
        # Convert <td> to <th> in the first row
        for cell in cells:
            cell.name = "th"
            cell["scope"] = "col"

        thead = soup_tag(table, "thead")
        first_row.wrap(thead)

        # Wrap remaining rows in <tbody> if not present
        if not table.find("tbody"):
            tbody = soup_tag(table, "tbody")
            remaining = table.find_all("tr")
            if remaining:
                first_remaining = remaining[0]
                first_remaining.wrap(tbody)
                for row in remaining[1:]:
                    tbody.append(row)


def soup_tag(context: Tag, name: str) -> Tag:
    """Create a new tag in the context's document."""
    return context.find_parent() and context.find_parent().new_tag(name) or \
           BeautifulSoup(f"<{name}></{name}>", "html.parser").find(name)


def _add_scope(table: Tag):
    """Add scope attributes to <th> elements."""
    # Header cells in <thead> get scope="col"
    thead = table.find("thead")
    if thead:
        for th in thead.find_all("th"):
            if not th.get("scope"):
                th["scope"] = "col"

    # First-column cells that look like row headers
    tbody = table.find("tbody") or table
    for row in tbody.find_all("tr"):
        cells = row.find_all(["td", "th"])
        if cells and cells[0].name == "th":
            if not cells[0].get("scope"):
                cells[0]["scope"] = "row"


def _add_caption(table: Tag):
    """Extract preceding table title text into a <caption> element."""
    if table.find("caption"):
        return

    # Look for preceding element with "Table N" text
    prev = table.find_previous_sibling()
    if prev and prev.string:
        text = prev.get_text(strip=True)
        if re.match(r"^Table\s+\d+", text, re.IGNORECASE):
            caption = BeautifulSoup(f"<caption>{text}</caption>", "html.parser").find("caption")
            table.insert(0, caption)
            prev.decompose()
            return

    # Also check if parent has a "Table N" preceding text node
    prev = table.find_previous(string=re.compile(r"Table\s+\d+", re.IGNORECASE))
    if prev and prev.find_parent() != table:
        text = prev.strip()
        if re.match(r"^Table\s+\d+", text, re.IGNORECASE):
            caption = BeautifulSoup(f"<caption>{text}</caption>", "html.parser").find("caption")
            table.insert(0, caption)


def _ensure_caption(table: Tag):
    """Ensure every table has a caption — generate from headers if needed."""
    if table.find("caption"):
        return
    if table.get("aria-label"):
        return

    # Try to build a caption from column headers
    thead = table.find("thead")
    if thead:
        headers = [th.get_text(strip=True) for th in thead.find_all("th")]
        headers = [h for h in headers if h and len(h) < 50]
        if headers:
            desc = "Table with columns: " + ", ".join(headers[:5])
            if len(headers) > 5:
                desc += f", and {len(headers) - 5} more"
            caption = BeautifulSoup(f"<caption>{desc}</caption>", "html.parser").find("caption")
            table.insert(0, caption)
            return

    # Fallback: generic caption with row/column counts
    rows = table.find_all("tr")
    cols = rows[0].find_all(["td", "th"]) if rows else []
    caption_text = f"Data table ({len(rows)} rows, {len(cols)} columns)"
    caption = BeautifulSoup(f"<caption>{caption_text}</caption>", "html.parser").find("caption")
    table.insert(0, caption)


def _add_role(table: Tag):
    """Add appropriate ARIA roles."""
    if not table.get("role"):
        table["role"] = "table"
