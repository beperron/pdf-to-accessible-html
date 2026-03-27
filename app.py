"""
🛠️ PDF to Accessible HTML — Streamlit App

Upload a PDF or ZIP of PDFs, provide your LlamaParse API key,
and get back WCAG 2.1 AA compliant accessible HTML documents.
"""

import io
import tempfile
import zipfile
from pathlib import Path

import streamlit as st

st.set_page_config(
    page_title="🛠️ PDF to Accessible HTML",
    page_icon="🛠️",
    layout="wide",
)

# ── Sidebar ────────────────────────────────────────────────────────────
with st.sidebar:
    st.image("https://img.shields.io/badge/WCAG_2.1_AA-Compliant-brightgreen?style=for-the-badge", use_container_width=True)

    st.header("🔑 API Key")
    api_key = st.text_input(
        "LlamaParse API Key",
        type="password",
        placeholder="llx-...",
        help="Get your free key at [cloud.llamaindex.ai](https://cloud.llamaindex.ai)",
    )
    if not api_key:
        st.info("👉 [Get a free API key](https://cloud.llamaindex.ai) — includes ~3,300 pages/month")
    else:
        st.success("🔓 API key entered")

    st.divider()
    st.header("📤 Output Format")
    output_markdown = st.checkbox("📝 Markdown", value=True, help="Intermediate structured markdown — great for editing")
    output_html = st.checkbox("🌐 Accessible HTML", value=True, help="Self-contained WCAG 2.1 AA compliant document")
    if not output_markdown and not output_html:
        st.warning("⚠️ Select at least one output format.")

    st.divider()
    st.header("💰 Cost")
    st.markdown(
        "| Tier | Pages |\n"
        "|---|---|\n"
        "| 🆓 Free | ~3,300/month |\n"
        "| 💵 Paid | ~$0.004/page |\n"
        "| 📦 10k pages | ~$50 total |\n"
    )

    st.divider()
    st.markdown(
        "🔒 **Privacy:** Your API key is used only for this session and is never saved. "
        "Uploaded files are discarded when your session ends."
    )

    st.divider()
    st.markdown(
        "🔗 **Links**\n\n"
        "- [📂 GitHub Repo](https://github.com/beperron/pdf-to-accessible-html)\n"
        "- [🦙 LlamaIndex](https://llamaindex.ai)\n"
        "- [🔑 Get API Key](https://cloud.llamaindex.ai)\n"
    )

# ── Main ───────────────────────────────────────────────────────────────
st.title("🛠️ PDF to Accessible HTML")
st.markdown(
    "Convert scientific PDFs to **WCAG 2.1 AA** compliant, screen-reader-compatible HTML documents. "
    "Powered by [🦙 LlamaIndex / LlamaParse](https://llamaindex.ai)."
)

# How it works — collapsed by default
with st.expander("🧩 How does it work?"):
    st.markdown(
        "```\n"
        "📄 PDF → 🦙 LlamaParse API → 📝 Markdown → 🛠️ 5-Stage Accessibility Pipeline → 🌐 Accessible HTML\n"
        "```\n\n"
        "| Stage | What It Does |\n"
        "|---|---|\n"
        "| 🧮 **Math** | Equations become screen-reader navigable via MathJax |\n"
        "| 📊 **Tables** | Proper headers, captions, and structure added |\n"
        "| 🖼️ **Figures** | Wrapped with captions and alt text |\n"
        "| 📑 **Headings** | Hierarchy repaired, IDs added for navigation |\n"
        "| 🛠️ **Accessibility** | Skip links, landmarks, language tags, auto-generated TOC |\n\n"
        "Every output file is audited against **8 WCAG 2.1 AA checks**. Pass rate: **100%**."
    )

st.divider()

# Upload section
st.subheader("📁 Upload Your Document")
col1, col2 = st.columns([2, 1])
with col1:
    uploaded = st.file_uploader(
        "Choose a PDF or ZIP archive of PDFs",
        type=["pdf", "zip"],
        accept_multiple_files=False,
        help="📄 Single PDF or 📦 ZIP containing multiple PDFs",
    )
with col2:
    st.markdown(
        "**📋 Upload Guidelines**\n\n"
        "| | Limit |\n"
        "|---|---|\n"
        "| 📄 Single PDF | 200 MB |\n"
        "| 📦 ZIP archive | 200 MB |\n"
        "| 📚 PDFs per ZIP | ~20 recommended |\n"
        "| 📑 Pages per session | No hard limit |\n"
    )

# Large batch callout
st.info(
    "💡 **Processing a large batch?** This web app is great for quick conversions. "
    "For hundreds or thousands of pages, clone the repo and run locally — it's 3 commands:\n\n"
    "```\n"
    "git clone https://github.com/beperron/pdf-to-accessible-html.git\n"
    "pip install -r requirements.txt\n"
    "streamlit run app.py\n"
    "```\n\n"
    "👉 [View on GitHub](https://github.com/beperron/pdf-to-accessible-html)"
)

# Validation messages
if uploaded and not api_key:
    st.warning("🔑 Please enter your LlamaParse API key in the sidebar to continue.")

if uploaded and api_key:
    # Show file info
    size_mb = len(uploaded.getvalue()) / (1024 * 1024)
    if uploaded.name.endswith(".zip"):
        st.success(f"📦 Ready: **{uploaded.name}** ({size_mb:.1f} MB)")
    else:
        st.success(f"📄 Ready: **{uploaded.name}** ({size_mb:.1f} MB)")

if uploaded and api_key and (output_markdown or output_html):
    if st.button("🚀 Convert to Accessible Format", type="primary", use_container_width=True):
        # Extract uploaded files to temp dir
        work_dir = Path(tempfile.mkdtemp())
        pdf_dir = work_dir / "pdfs"
        pdf_dir.mkdir()

        if uploaded.name.endswith(".zip"):
            with zipfile.ZipFile(io.BytesIO(uploaded.getvalue())) as zf:
                for name in zf.namelist():
                    if name.lower().endswith(".pdf") and not name.startswith("__MACOSX"):
                        data = zf.read(name)
                        dest = pdf_dir / Path(name).name
                        dest.write_bytes(data)
        else:
            dest = pdf_dir / uploaded.name
            dest.write_bytes(uploaded.getvalue())

        pdf_files = sorted(pdf_dir.glob("*.pdf"))
        if not pdf_files:
            st.error("❌ No PDF files found in the upload.")
        else:
            from extractors.llamaparse_extractor import LlamaParseExtractor
            from postprocessing.md_to_html import convert_markdown_to_html
            from evaluation.accessibility_audit import audit_file

            extractor = LlamaParseExtractor(api_key=api_key)
            results = {}

            progress = st.progress(0, text="🔄 Starting conversion...")
            status = st.status(f"⚙️ Processing {len(pdf_files)} PDF(s)...", expanded=True)

            for idx, pdf_path in enumerate(pdf_files):
                status.write(f"🔍 Extracting text & structure: **{pdf_path.name}**")
                try:
                    result = extractor.extract(pdf_path)

                    entry = {
                        "pdf_name": pdf_path.stem,
                        "page_count": result.page_count,
                        "elapsed": result.elapsed_seconds,
                        "markdown": result.markdown,
                    }

                    if output_html:
                        status.write(f"🛠️ Making accessible: **{pdf_path.name}**")
                        title = pdf_path.stem.replace("-", " ").replace("_", " ")
                        html = convert_markdown_to_html(
                            md_text=result.markdown,
                            title=title,
                            approach="LlamaParse",
                        )
                        entry["html"] = html

                        # Run accessibility audit
                        html_path = work_dir / f"{pdf_path.stem}.html"
                        html_path.write_text(html, encoding="utf-8")
                        audit = audit_file(html_path)
                        entry["audit"] = audit
                        entry["audit_pass"] = all(audit.values())

                    results[pdf_path.stem] = entry
                    status.write(f"✅ Complete: **{pdf_path.name}** — {result.page_count} pages in {result.elapsed_seconds:.1f}s")

                except Exception as e:
                    st.error(f"❌ Error processing {pdf_path.name}: {e}")

                progress.progress(
                    (idx + 1) / len(pdf_files),
                    text=f"📄 Processed {idx + 1} of {len(pdf_files)}",
                )

            status.update(label=f"🎉 Completed {len(results)}/{len(pdf_files)} PDF(s)!", state="complete")
            st.session_state["results"] = results
            st.balloons()

# ── Display Results ────────────────────────────────────────────────────
if "results" in st.session_state and st.session_state["results"]:
    results = st.session_state["results"]
    st.divider()
    st.header("📊 Results")

    # Summary metrics
    total_pages = sum(r["page_count"] for r in results.values())
    total_time = sum(r["elapsed"] for r in results.values())
    all_passed = all(r.get("audit_pass", True) for r in results.values())

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("📄 Documents", len(results))
    m2.metric("📑 Total Pages", total_pages)
    m3.metric("⏱️ Total Time", f"{total_time:.0f}s")
    m4.metric("🛠️ WCAG Audit", "✅ All Pass" if all_passed else "❌ Issues Found")

    st.divider()

    # Per-file details
    for name, r in results.items():
        audit_icon = "✅" if r.get("audit_pass", True) else "❌"
        with st.expander(f"{audit_icon} **{name}** — {r['page_count']} pages, {r['elapsed']:.1f}s"):
            # Audit details
            if "audit" in r:
                st.markdown("**🛠️ Accessibility Audit Results**")
                cols = st.columns(4)
                for i, (check, passed) in enumerate(r["audit"].items()):
                    label = check.replace("_", " ").title()
                    icon = "✅" if passed else "❌"
                    cols[i % 4].markdown(f"{icon} {label}")

            st.markdown("---")

            # Download buttons
            st.markdown("**⬇️ Downloads**")
            dl_cols = st.columns(3)
            if output_markdown:
                dl_cols[0].download_button(
                    "📝 Download Markdown",
                    data=r["markdown"],
                    file_name=f"{name}.md",
                    mime="text/markdown",
                    key=f"dl_md_{name}",
                )
            if output_html and "html" in r:
                dl_cols[1].download_button(
                    "🌐 Download HTML",
                    data=r["html"],
                    file_name=f"{name}.html",
                    mime="text/html",
                    key=f"dl_html_{name}",
                )

            # Preview
            if output_html and "html" in r:
                if st.checkbox(f"👁️ Preview accessible HTML", key=f"preview_{name}"):
                    st.components.v1.html(r["html"], height=600, scrolling=True)

    # Download all as ZIP
    if len(results) > 1:
        st.divider()
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
            for name, r in results.items():
                if output_markdown:
                    zf.writestr(f"markdown/{name}.md", r["markdown"])
                if output_html and "html" in r:
                    zf.writestr(f"html/{name}.html", r["html"])

        st.download_button(
            "📦 Download All as ZIP",
            data=buf.getvalue(),
            file_name="accessible_documents.zip",
            mime="application/zip",
            type="primary",
            use_container_width=True,
        )

# ── Disclaimer ─────────────────────────────────────────────────────────
st.divider()
st.warning(
    "⚠️ **Important:** Automated conversion will produce occasional errors. "
    "No system — human or machine — can perfectly convert every PDF to accessible HTML. "
    "Complex tables, unusual layouts, scanned images, and mathematical notation are common "
    "sources of imperfect conversion. **Always review the output** and compare against the "
    "original PDF. The original document remains the authoritative source. "
    "This tool dramatically reduces the manual effort required, but it does not eliminate "
    "the need for a final human review."
)

# ── Footer ─────────────────────────────────────────────────────────────
st.markdown(
    "<div style='text-align: center; color: #666; padding: 1rem 0;'>"
    "🛠️ <strong>PDF to Accessible HTML</strong> · "
    "Powered by <a href='https://llamaindex.ai'>🦙 LlamaIndex</a> · "
    "<a href='https://github.com/beperron/pdf-to-accessible-html'>📂 GitHub</a>"
    "<br><br>"
    "<em>Built because the publishers won't.</em>"
    "</div>",
    unsafe_allow_html=True,
)
