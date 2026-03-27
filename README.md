<div align="center">

<img src="assets/parsing.png" alt="A rainbow llama eating PDFs and producing accessible HTML documents" width="500">

# PDF to Accessible HTML

Convert inaccessible PDFs to WCAG 2.1 AA compliant, screen-reader-compatible HTML — for less than half a cent per page.

Powered by [LlamaIndex](https://llamaindex.ai) / [LlamaParse](https://docs.cloud.llamaindex.ai/llamaparse/getting_started)

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://pdf-to-accessible-html.streamlit.app/)
&nbsp;&nbsp;
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
&nbsp;&nbsp;
[![WCAG 2.1 AA](https://img.shields.io/badge/WCAG_2.1_AA-Compliant-brightgreen)](https://www.w3.org/WAI/WCAG21/quickref/)

---

Upload a PDF. Get back a fully accessible, screen-reader-compatible HTML document.<br>
No technical skills required. Every output file passes an 8-point accessibility audit.

[Try the App](https://pdf-to-accessible-html.streamlit.app/) · [How It Works](#how-it-works) · [Why This Exists](#why-this-exists)

</div>

<br>

## The Problem

On **April 24, 2026**, the DOJ's [ADA Title II Digital Accessibility Rule](https://www.ada.gov/resources/2024-03-08-web-rule/) takes effect for every state and local government serving 50,000 or more people. For the first time, there is a legally binding technical standard — [WCAG 2.1 Level AA](https://www.w3.org/TR/WCAG21/) — for all digital content published by covered entities. The penalties are real: up to $75,000 for a first violation, $150,000 for subsequent violations, assessed per instance.

Most institutions understand their websites need to be accessible. Fewer have reckoned with the **document problem**.

> Public institutions produce and host enormous volumes of PDFs — court opinions, policy documents, research publications, meeting minutes, budget reports. The overwhelming majority are inaccessible. They lack tagged headings, meaningful reading order, table structure, and alt text. A screen reader encounters most of them as a wall of undifferentiated text — or worse, as images with no text at all.

Manual remediation costs $50–$150 per document and takes a trained specialist 10–15 hours. For an institution with thousands of documents, the math is prohibitive. This is why, despite decades of legal obligation, most public-facing documents remain inaccessible.

The new rule changes that calculus. This tool converts documents at $0.004 per page, and the free tier covers ~3,300 pages/month.

---

## Why This Exists

This is a **civil rights issue**, not a compliance issue.

Approximately 42.5 million Americans live with a disability that affects their use of digital content. When a court system publishes opinions as inaccessible PDFs, it is an access-to-justice failure. When a university posts research behind inaccessible formatting, it excludes the people that research is meant to serve.

The standards to fix this have existed since 1999. The ADA has been law since 1990. The publishers and institutions with the resources to implement them have chosen not to.

What has changed is that the technology to solve this is now available at a price point that makes the failure to act a choice rather than a constraint.

---

## Quick Start

### Use the Web App

> [!TIP]
> No installation required. The web app handles everything.

1. [Open the App](https://pdf-to-accessible-html.streamlit.app/)
2. Get a free API key at [cloud.llamaindex.ai](https://cloud.llamaindex.ai) — takes 30 seconds, includes ~3,300 free pages/month
3. Paste your key in the sidebar
4. Upload your PDF or ZIP
5. Click Convert and download your accessible documents

### Run Locally (for large batches)

```bash
git clone https://github.com/beperron/pdf-to-accessible-html.git
cd pdf-to-accessible-html
pip install -r requirements.txt
streamlit run app.py
```

---

## How It Works

```
PDF  -->  LlamaParse API  -->  Structured Markdown  -->  5-Stage Pipeline  -->  Accessible HTML
```

Step 1 — Extraction via [LlamaParse](https://docs.cloud.llamaindex.ai/llamaparse/getting_started).
LlamaParse is a document parsing API built by [LlamaIndex](https://llamaindex.ai). It reads the PDF and extracts text, tables, equations, figures, and headings as structured markdown. This is the hard part — the step that would take a team of engineers months to build — and LlamaParse does it well, at scale, across PDFs, Word docs, PowerPoints, Excel files, and more.

Step 2 — Accessibility pipeline.
Five processors transform the markdown into WCAG-compliant HTML:

| Stage | What It Does |
|:---|:---|
| Math | Routes equations through MathJax for screen-reader navigation |
| Tables | Adds `<thead>`, `<th scope>`, `<caption>`, and ARIA roles |
| Figures | Wraps images in `<figure>` with `<figcaption>` and alt text |
| Headings | Repairs hierarchy (no skipped levels), adds slugified IDs |
| Accessibility | Skip links, ARIA landmarks, `lang` attribute, auto-generated TOC |

Step 3 — Audit.
Every output file is verified against 8 WCAG 2.1 AA criteria. Pass rate: 100%.

---

## What Makes the Output Accessible

<details>
<summary>Full accessibility feature list</summary>
<br>

| Feature | Why It Matters |
|:---|:---|
| Language attribute (`lang="en"`) | Screen readers use correct pronunciation |
| "Skip to content" link | Keyboard users jump past navigation |
| Landmark regions (`<main>`, `<nav>`, `<article>`) | Screen readers announce page structure |
| Auto-generated table of contents | Navigate to any section by heading |
| MathJax with accessibility explorer | Equations are spoken aloud and navigable |
| Semantic table markup (`<th scope>`, `<caption>`) | Screen readers announce row/column headers |
| Alt text on all images | Figures are described, not invisible |
| Sequential heading hierarchy | No confusing jumps in document structure |
| High-contrast styling (13.6:1 ratio) | Exceeds WCAG AA minimum (4.5:1) |
| Reduced motion support | Respects `prefers-reduced-motion` |
| Print stylesheet | Clean output when printed |

</details>

---

## Cost

| Tier | Cost | Pages |
|:---|:---|:---|
| Free | $0 | ~3,300 pages/month |
| Paid | ~$0.004/page | 10,000 pages = $50 |

> [!NOTE]
> You bring your own [LlamaParse API key](https://cloud.llamaindex.ai) from [LlamaIndex](https://llamaindex.ai). The free tier is generous — most individual users will never need to pay.

---

## Legal Context

Format conversion for accessibility is supported by multiple federal statutes and case law:

| Law | Relevance |
|:---|:---|
| ADA Title II (42 U.S.C. §§ 12131-12165) | Public entities must provide accessible digital content (WCAG 2.1 AA by April 2026) |
| Chafee Amendment (17 U.S.C. § 121) | Directly authorizes accessible format conversion for persons with print disabilities |
| Fair Use (17 U.S.C. § 107) | Educational, non-commercial format conversion for accessibility is a favored use |
| TEACH Act (17 U.S.C. §§ 110(2), 112(f)) | Authorizes format conversion for digital transmission to enrolled students |
| *HathiTrust* (755 F.3d 87, 2d Cir. 2014) | Federal appeals court held format conversion for accessibility is fair use — even for entire works |

---

## Limitations

> [!IMPORTANT]
> Automated conversion will produce occasional errors. Complex tables, unusual layouts, scanned images, and mathematical notation are common sources of imperfect output. Always review the output and compare against the original PDF. The original document remains the authoritative source.

This tool dramatically reduces manual effort — from hours per document to seconds — but it does not eliminate the need for a final human review.

---

## Privacy & Security

- Your API key is used only during your session — never saved or logged
- Uploaded files are processed in temporary storage and discarded when your session ends
- The app stores nothing between sessions

---

## Credits

This tool is 95% [LlamaParse](https://docs.cloud.llamaindex.ai/llamaparse/getting_started) and 5% post-processing. The extraction — the hard part — is entirely theirs.

- [LlamaIndex](https://llamaindex.ai) — the company behind LlamaParse. Their document parsing API is what makes this tool possible.
- [LlamaParse](https://docs.cloud.llamaindex.ai/llamaparse/getting_started) — the document extraction engine. Converts PDFs to structured markdown with remarkable accuracy.
- [MathJax](https://www.mathjax.org/) — accessible equation rendering with the Speech Rule Engine.

---

<div align="center">

[Try the App](https://pdf-to-accessible-html.streamlit.app/) · [Report an Issue](https://github.com/beperron/pdf-to-accessible-html/issues) · [Get an API Key](https://cloud.llamaindex.ai)

---

*Built because the publishers won't.*

*The legal discussion about whether you're allowed to do this costs 100x more than doing it.*

</div>
