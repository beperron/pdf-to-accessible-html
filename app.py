"""Streamlit interface for Documents to Accessible HTML."""

import os
import tempfile
from pathlib import Path

import streamlit as st

from extractors.llamaparse_extractor import LlamaParseExtractor, MODES
from postprocessing.md_to_html import convert_markdown_to_html
from evaluation.accessibility_audit import audit_file

SUPPORTED_EXTENSIONS = [
    "pdf", "docx", "doc", "pptx", "ppt", "xlsx", "xls",
    "html", "htm", "txt", "rtf", "epub", "md",
    "jpg", "jpeg", "png", "gif", "bmp", "tiff", "webp",
]

AUDIT_LABELS = {
    "lang_attribute": "Language attribute",
    "skip_navigation": "Skip navigation link",
    "main_landmark": "Main landmark",
    "images_have_alt": "Images have alt text",
    "tables_have_caption": "Tables have captions",
    "th_have_scope": "Table headers have scope",
    "heading_hierarchy": "Heading hierarchy",
    "title_element": "Title element",
}


def run_conversion(uploaded_file, api_key: str, mode: str) -> dict:
    """Convert an uploaded file and return results."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)

        # Write uploaded file to disk
        input_path = tmp_path / uploaded_file.name
        input_path.write_bytes(uploaded_file.getvalue())

        # Extract
        extractor = LlamaParseExtractor(api_key=api_key, mode=mode)
        result = extractor.extract(input_path)

        # Convert to accessible HTML
        title = input_path.stem.replace("-", " ").replace("_", " ")
        html = convert_markdown_to_html(
            md_text=result.markdown,
            title=title,
            approach="LlamaParse",
        )

        # Write HTML to temp file for audit
        html_path = tmp_path / f"{input_path.stem}.html"
        html_path.write_text(html, encoding="utf-8")
        audit = audit_file(html_path)

        return {
            "filename": uploaded_file.name,
            "title": title,
            "html": html,
            "markdown": result.markdown,
            "page_count": result.page_count,
            "elapsed_seconds": result.elapsed_seconds,
            "audit": audit,
            "all_passed": all(audit.values()),
        }


# --- Page config ---

st.set_page_config(
    page_title="Documents to Accessible HTML",
    page_icon=":rainbow:",
    layout="wide",
)

# --- Custom CSS ---

st.markdown("""
<style>
    /* Hero section */
    .hero-container {
        text-align: center;
        padding: 1rem 0 0.5rem 0;
    }
    .hero-container img {
        max-width: 320px;
        margin-bottom: 0.5rem;
    }
    .hero-title {
        font-size: 2.2rem;
        font-weight: 700;
        margin: 0.25rem 0;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    .hero-subtitle {
        font-size: 1.1rem;
        color: #6b7280;
        margin-bottom: 1.5rem;
        line-height: 1.5;
    }

    /* Upload area */
    [data-testid="stFileUploader"] {
        border-radius: 12px;
    }
    [data-testid="stFileUploader"] section {
        padding: 1rem;
    }

    /* Result cards */
    .audit-pass {
        background: linear-gradient(135deg, #d1fae5, #a7f3d0);
        padding: 0.75rem 1rem;
        border-radius: 8px;
        border-left: 4px solid #059669;
        margin: 0.5rem 0;
    }
    .audit-fail {
        background: linear-gradient(135deg, #fee2e2, #fecaca);
        padding: 0.75rem 1rem;
        border-radius: 8px;
        border-left: 4px solid #dc2626;
        margin: 0.5rem 0;
    }

    /* Sidebar polish */
    [data-testid="stSidebar"] {
        padding-top: 1.5rem;
    }
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
        font-size: 0.9rem;
    }

    /* Metric styling */
    [data-testid="stMetric"] {
        text-align: center;
    }

    /* Reduce top padding */
    .block-container {
        padding-top: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# --- Sidebar ---

with st.sidebar:
    st.image("assets/parsing.png", width=200)
    st.markdown("#### Settings")

    api_key = st.text_input(
        "LlamaParse API Key",
        value=os.environ.get("LLAMA_CLOUD_API_KEY", ""),
        type="password",
        help="Get a free key at [cloud.llamaindex.ai](https://cloud.llamaindex.ai)",
    )

    mode = st.radio(
        "Parsing mode",
        options=list(MODES.keys()),
        index=1,  # default
        format_func=lambda m: {
            "fast": "Fast  (~3 credits/page)",
            "default": "Default  (~3-10 credits/page)",
            "quality": "Quality  (~10 credits/page)",
        }[m],
        help=(
            "**Fast** — simple, text-heavy documents.  \n"
            "**Default** — most documents. Auto-upgrades complex pages.  \n"
            "**Quality** — research papers, dense tables, equations."
        ),
    )

    st.divider()

    st.markdown(
        "**How it works**\n\n"
        "1. Upload a document\n"
        "2. We extract content via [LlamaParse](https://docs.cloud.llamaindex.ai/llamaparse/getting_started)\n"
        "3. A 5-stage pipeline adds accessibility features\n"
        "4. Every file is audited against 8 WCAG 2.1 AA checks"
    )

    st.divider()
    st.caption(
        "Powered by [LlamaParse](https://docs.cloud.llamaindex.ai/llamaparse/getting_started)  \n"
        "Free tier: ~3,300 pages/month  \n"
        "[GitHub](https://github.com/beperron/pdf-to-accessible-html)"
    )

# --- Hero section ---

col_left, col_center, col_right = st.columns([1, 2, 1])
with col_center:
    st.markdown("""
    <div class="hero-container">
        <div class="hero-title">Documents to Accessible HTML</div>
        <div class="hero-subtitle">
            Convert PDFs, PowerPoints, Word docs, and more to<br>
            WCAG 2.1 AA compliant, screen-reader-compatible HTML
        </div>
    </div>
    """, unsafe_allow_html=True)

# --- Upload area ---

uploaded_files = st.file_uploader(
    "Choose files to convert",
    type=SUPPORTED_EXTENSIONS,
    accept_multiple_files=True,
    help="PDF, PowerPoint, Word, Excel, images, and more.",
    label_visibility="collapsed",
)

if not uploaded_files:
    st.markdown(
        "<div style='text-align: center; color: #9ca3af; padding: 0.5rem 0;'>"
        "Drag and drop files above, or click to browse.  "
        "Supports PDF, PPTX, DOCX, XLSX, RTF, EPUB, and images."
        "</div>",
        unsafe_allow_html=True,
    )

if uploaded_files and not api_key:
    st.warning(
        "Enter your LlamaParse API key in the sidebar to get started.  \n"
        "Get a free key at [cloud.llamaindex.ai](https://cloud.llamaindex.ai)."
    )

if uploaded_files and api_key:
    if st.button("Convert", type="primary", use_container_width=True):
        results = []

        progress = st.progress(0, text="Starting conversion...")

        for i, uploaded_file in enumerate(uploaded_files):
            progress.progress(
                i / len(uploaded_files),
                text=f"Converting {uploaded_file.name}...",
            )
            try:
                result = run_conversion(uploaded_file, api_key, mode)
                results.append(result)
            except Exception as e:
                st.error(f"Failed to convert {uploaded_file.name}: {e}")

        progress.progress(1.0, text="Done!")

        st.session_state["results"] = results

# --- Display results ---

if "results" in st.session_state:
    results = st.session_state["results"]

    st.divider()

    for result in results:
        with st.container(border=True):
            # Header row with filename and metrics
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                st.subheader(result["filename"])
            with col2:
                st.metric("Pages", result["page_count"])
            with col3:
                st.metric("Time", f"{result['elapsed_seconds']:.1f}s")

            # Audit results
            if result["all_passed"]:
                st.markdown(
                    '<div class="audit-pass">'
                    "All 8 WCAG 2.1 AA checks passed"
                    "</div>",
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    '<div class="audit-fail">'
                    "Some accessibility checks failed"
                    "</div>",
                    unsafe_allow_html=True,
                )

            with st.expander("Audit details"):
                cols = st.columns(4)
                for i, (check, passed) in enumerate(result["audit"].items()):
                    label = AUDIT_LABELS.get(check, check)
                    icon = "white_check_mark" if passed else "x"
                    cols[i % 4].markdown(f":{icon}: {label}")

            # Preview and download
            tab_preview, tab_markdown = st.tabs(["HTML Preview", "Markdown"])

            with tab_preview:
                st.components.v1.html(result["html"], height=600, scrolling=True)

            with tab_markdown:
                st.code(result["markdown"], language="markdown")

            # Download buttons
            col_dl1, col_dl2, _ = st.columns([1, 1, 2])
            stem = Path(result["filename"]).stem
            with col_dl1:
                st.download_button(
                    "Download HTML",
                    data=result["html"],
                    file_name=f"{stem}.html",
                    mime="text/html",
                )
            with col_dl2:
                st.download_button(
                    "Download Markdown",
                    data=result["markdown"],
                    file_name=f"{stem}.md",
                    mime="text/markdown",
                )
