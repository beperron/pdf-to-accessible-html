<div align="center">

# 🛠️ PDF to Accessible HTML

### Make scientific papers readable by everyone.

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://pdf-to-accessible-html.streamlit.app/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![WCAG 2.1 AA](https://img.shields.io/badge/WCAG_2.1_AA-Compliant-brightgreen)](https://www.w3.org/WAI/WCAG21/quickref/)

Upload a PDF. Get back a fully accessible, screen-reader-compatible HTML document.
No technical skills required.

---

</div>

## 🎯 What This Does

You upload a scientific PDF (or a ZIP of several). The app converts it to an **accessible HTML document** that works with screen readers, keyboard navigation, and assistive technologies — meeting the [WCAG 2.1 AA](https://www.w3.org/WAI/WCAG21/quickref/) accessibility standard.

That's it. Upload, convert, download.

> **📄 → 🛠️ Accessible HTML**
> One click. Every equation, table, heading, and figure made accessible.

---

## 💡 Why This Exists

Scientific publishers earn billions of dollars a year from research that academics write, review, and edit — for free. And yet, the PDFs they produce are overwhelmingly **inaccessible** to people with disabilities:

- 🚫 Headings look like headings but aren't tagged — screen readers can't navigate them
- 🚫 Tables have no structure — screen readers read them as a jumble of cell values
- 🚫 Equations are flat images — screen readers just say "image"
- 🚫 Figures have no descriptions

The accessibility standards to fix this have existed since **1999**. The ADA has been law since **1990**. The publishers have had decades and billions of dollars. They haven't done it.

**This tool does it for them — for about half a cent per page.**

---

## 🚀 Try It Now

### Option 1: Use the Web App (easiest)

👉 **[Open the App](https://pdf-to-accessible-html.streamlit.app/)**

1. Get a free API key at [cloud.llamaindex.ai](https://cloud.llamaindex.ai) (takes 30 seconds, includes ~3,300 free pages/month)
2. Paste your key in the sidebar
3. Upload your PDF or ZIP
4. Click **Convert** and download your accessible documents

### Option 2: Run It Yourself (for large batches)

The web app is perfect for a few documents. For processing hundreds or thousands of pages, run it locally — same code, no limits, three commands:

```bash
git clone https://github.com/beperron/pdf-to-accessible-html.git
pip install -r requirements.txt
streamlit run app.py
```

---

## 💰 What It Costs

| | Cost | Pages |
|---|---|---|
| 🆓 **Free tier** | $0 | ~3,300 pages/month |
| 💵 **Paid** | ~$0.004/page | 10,000 pages ≈ **$50** |

For perspective:

| Activity | Cost | Pages Converted |
|---|---|---|
| 🗣️ One meeting (4 staff, 1 hour, $100k salaries) | ~$280 | **0** |
| 🤖 This tool (same $280) | ~$280 | **~70,000** |
| 🧑‍💼 Manual remediation (1 document, 15 hours) | ~$1,020 | **~20 pages** |

---

## 🔧 How It Works

```
PDF  →  LlamaParse API  →  Structured Markdown  →  5-Stage Accessibility Pipeline  →  Accessible HTML
```

**Step 1 — Extraction.** Your PDF is sent to [LlamaParse](https://llamaindex.ai) (by LlamaIndex), which reads the document and pulls out the text, tables, equations, figures, and headings as structured content.

**Step 2 — Accessibility Processing.** Five automated processors clean up and enhance the output:

| Processor | What It Does |
|---|---|
| 🧮 **Math** | Equations become screen-reader navigable via MathJax |
| 📊 **Tables** | Proper headers, captions, and structure added |
| 🖼️ **Figures** | Wrapped with captions and alt text |
| 📑 **Headings** | Hierarchy repaired (no skipped levels), IDs added for navigation |
| 🛠️ **Accessibility** | Skip links, landmarks, language tags, auto-generated table of contents |

**Step 3 — Audit.** Every output file is checked against 8 WCAG 2.1 AA criteria. Pass rate: **100%**.

---

## 📤 Output Options

Choose one or both:

- **📝 Markdown** — the intermediate structured text (inspectable, editable, lightweight)
- **🌐 Accessible HTML** — self-contained document with inline styling, ready to open in any browser

---

## 🛠️ What Makes the Output Accessible

Every HTML file includes:

| Feature | Why It Matters |
|---|---|
| Language attribute (`lang="en"`) | Screen readers use correct pronunciation |
| "Skip to content" link | Keyboard users jump past navigation |
| Landmark regions (`<main>`, `<nav>`, `<article>`) | Screen readers announce page structure |
| Auto-generated table of contents | Navigate to any section by heading |
| MathJax with accessibility explorer | Equations are spoken aloud and navigable |
| Semantic table markup | Screen readers announce row/column headers |
| Alt text on all images | Figures are described, not invisible |
| Sequential heading hierarchy | No confusing jumps in document structure |
| High-contrast styling (13.6:1 ratio) | Exceeds WCAG AA requirements (4.5:1 minimum) |
| Reduced motion support | Respects user accessibility preferences |
| Print stylesheet | Clean output when printed |

---

## ⚖️ Legal Context

Format conversion for accessibility in higher education is supported by multiple federal statutes and case law:

| Law | What It Says |
|---|---|
| **Fair Use** (17 U.S.C. § 107) | Educational, non-commercial format conversion for accessibility is a favored use |
| **Chafee Amendment** (17 U.S.C. § 121) | Directly authorizes accessible format conversion for persons with print disabilities |
| **TEACH Act** (17 U.S.C. §§ 110(2), 112(f)) | Authorizes format conversion for digital transmission to enrolled students |
| **ADA Title II** (42 U.S.C. §§ 12131–12165) | Public universities are *required* to provide accessible digital content (WCAG 2.1 AA by April 2026) |
| ***HathiTrust*** (755 F.3d 87, 2d Cir. 2014) | Federal appeals court held format conversion for accessibility is fair use — even for entire works |

---

## ⚠️ Disclaimer

Automated conversion will produce occasional errors. No system — human or machine — can perfectly handle every PDF. Complex tables, unusual layouts, scanned images, multi-column formatting, and mathematical notation are common sources of imperfect conversion. The pipeline handles the vast majority of content correctly, but **always review the output** and compare against the original PDF.

The original document remains the authoritative source. This tool dramatically reduces the manual effort required to produce accessible documents (from hours per document to seconds), but it does not eliminate the need for a final human review.

---

## 🔒 Privacy & Security

- Your API key is used **only during your session** — it is never saved to disk or logged
- Uploaded files are processed in **temporary storage** and discarded when your session ends
- The app stores **nothing** between sessions

---

## 🙏 Credits

- **[LlamaIndex / LlamaParse](https://llamaindex.ai)** — the extraction engine that makes this possible. Excellent service, highly recommended.
- **[MathJax](https://www.mathjax.org/)** — accessible equation rendering with the Speech Rule Engine

---

<div align="center">

### 📬 Questions or Feedback?

Open an [issue on GitHub](https://github.com/beperron/pdf-to-accessible-html/issues) or reach out.

---

*Built because the publishers won't.*

*10,000 pages for $50. Every file passes every accessibility check.*

*The legal discussion about whether you're allowed to do this costs 100× more than doing it.*

</div>
