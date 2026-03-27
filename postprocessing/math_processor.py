"""Process LaTeX math expressions for MathJax rendering + accessibility."""

import re
from bs4 import BeautifulSoup, NavigableString

# Patterns that indicate code, not math
CODE_INDICATORS = re.compile(
    r"(\.to_excel|\.to_csv|\.read_|\.DataFrame|\.apply|\.groupby|\.merge"
    r"|\.xlsx|\.csv|\.json|\.py|\.txt|\.pdf"
    r"|import\s|from\s|def\s|class\s|return\s|print\("
    r"|pd\.|np\.|df\.|os\.|sys\."
    r"|==|!=|<=|>=|\.append|\.split|\.join"
    r"|http://|https://|www\."
    r"|response\.|request\.|send\(|choices\[)",
    re.IGNORECASE,
)

# Patterns that indicate genuine LaTeX math
MATH_INDICATORS = re.compile(
    r"(\\frac|\\sum|\\int|\\prod|\\lim|\\sqrt|\\alpha|\\beta|\\gamma|\\delta"
    r"|\\theta|\\lambda|\\sigma|\\mu|\\pi|\\infty|\\partial|\\nabla"
    r"|\\begin\{|\\end\{|\\mathbb|\\mathcal|\\mathbf|\\mathrm"
    r"|\\left|\\right|\\over|\\cdot|\\times|\\leq|\\geq|\\neq"
    r"|\\hat|\\bar|\\tilde|\\vec|\\dot"
    r"|\^{|_{|\\log|\\exp|\\sin|\\cos|\\tan"
    r"|[=+\-*/^_]{2,})",  # math operators
)


def _is_likely_math(content: str) -> bool:
    """Heuristic: is this content between math delimiters actually math?"""
    content = content.strip()
    if not content:
        return False
    # If it has code indicators, it's probably code
    if CODE_INDICATORS.search(content):
        return False
    # If it's \text{...} wrapping a long string, probably misidentified code
    text_match = re.match(r"^\s*\\text\{(.+)\}\s*$", content, re.DOTALL)
    if text_match and len(text_match.group(1)) > 30:
        return False
    # Multiple \text{} blocks chained = probably pseudocode, not math
    text_blocks = re.findall(r"\\text\{[^}]+\}", content)
    if len(text_blocks) >= 3:
        return False
    # If it has LaTeX math commands, it's math
    if MATH_INDICATORS.search(content):
        return True
    # Short content with simple symbols — likely math (e.g., "x^2", "n=1")
    if len(content) < 80 and re.search(r"[=^_{}\\]", content):
        return True
    # Default: if delimiters were present, treat as math
    return True


def process_math(soup: BeautifulSoup) -> BeautifulSoup:
    """Wrap LaTeX expressions in appropriate containers for MathJax."""
    body = soup.find("body") or soup
    _process_node(body)
    # Fix double-nested math containers from multiple processing passes
    _fix_double_nesting(soup)
    return soup


def _fix_double_nesting(soup: BeautifulSoup):
    """Remove double-nested math-display and math-inline containers."""
    # Fix <div class="math-display"><div class="math-display">...</div></div>
    for outer in soup.find_all("div", class_="math-display"):
        inner = outer.find("div", class_="math-display")
        if inner:
            outer.replace_with(inner)

    # Fix <span class="math-inline"><span class="math-inline">...</span></span>
    for outer in soup.find_all("span", class_="math-inline"):
        inner = outer.find("span", class_="math-inline")
        if inner:
            outer.replace_with(inner)


def _process_node(element):
    """Recursively process text nodes to wrap math expressions."""
    if isinstance(element, NavigableString):
        return
    # Don't process inside code/pre/math blocks
    if element.name in ("code", "pre", "script", "style"):
        return
    # Don't re-process content already in math containers
    if element.get("class") and ("math-display" in element.get("class", []) or
                                  "math-inline" in element.get("class", [])):
        return

    for child in list(element.children):
        if isinstance(child, NavigableString):
            text = str(child)
            if _has_math(text):
                new_html = _wrap_math(text)
                if new_html != text:
                    from bs4 import BeautifulSoup as BS
                    fragment = BS(new_html, "html.parser")
                    child.replace_with(fragment)
        else:
            _process_node(child)


def _has_math(text: str) -> bool:
    """Quick check if text likely contains LaTeX math."""
    return any(delim in text for delim in ["$", "\\(", "\\)", "\\[", "\\]"])


def _wrap_display(match: re.Match) -> str:
    """Wrap a display math match, but only if it looks like real math."""
    content = match.group(1)
    if _is_likely_math(content):
        return f'<div class="math-display" role="math" aria-label="Mathematical equation">\\[{content}\\]</div>'
    return f'<pre><code>{content.strip()}</code></pre>'


def _wrap_inline(match: re.Match) -> str:
    """Wrap an inline math match, but only if it looks like real math."""
    content = match.group(1)
    if _is_likely_math(content):
        return f'<span class="math-inline">\\({content}\\)</span>'
    return f'<code>{content.strip()}</code>'


def _wrap_math(text: str) -> str:
    """Wrap LaTeX expressions in span/div containers."""
    # Display math: $$...$$
    text = re.sub(r"\$\$(.*?)\$\$", _wrap_display, text, flags=re.DOTALL)
    # Display math: \[...\]
    text = re.sub(r"\\\[(.*?)\\\]", _wrap_display, text, flags=re.DOTALL)
    # Inline math: $...$ (not $$)
    text = re.sub(r"(?<!\$)\$(?!\$)(.*?)(?<!\$)\$(?!\$)", _wrap_inline, text)
    # Inline math: \(...\)
    text = re.sub(r"\\\((.*?)\\\)", _wrap_inline, text)
    # Space-padded paren math: ( \text{...} ) or ( x^2 )
    text = re.sub(
        r"\(\s*(\\(?:text|frac|sum|int|alpha|beta|gamma|delta|theta|sigma|mu|log|exp)[^)]{1,80})\s*\)",
        _wrap_inline_paren,
        text,
    )
    return text


def _wrap_inline_paren(match: re.Match) -> str:
    """Wrap space-padded paren math like ( \\text{IDF}(t) )."""
    content = match.group(1).strip()
    if _is_likely_math(content):
        return f'<span class="math-inline">\\({content}\\)</span>'
    return f'({content})'


def generate_mathml_fallback(latex: str) -> str:
    """Generate MathML from LaTeX for <noscript> fallback."""
    try:
        import latex2mathml.converter
        return latex2mathml.converter.convert(latex)
    except Exception:
        return f'<code class="math-fallback">{latex}</code>'
