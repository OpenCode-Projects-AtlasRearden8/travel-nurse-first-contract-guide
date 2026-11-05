#!/usr/bin/env python3
"""Build the Travel Nurse First-Contract Guide static HTML site.

Reads Markdown from docs/ and writes a self-contained static site to site/.
Standard library only, local-first: no network access, no dependencies.
Usage: python3 build.py [--check]
"""

import argparse
import datetime
import html
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DOCS = ROOT / "docs"
SITE = ROOT / "site"

# Reading order: index first, then chapters, then appendices.
PAGE_ORDER = [
    "index",
    "01-agency-types",
    "02-contract-clauses",
    "03-compact-licensing",
    "04-pay-packages",
    "05-housing-inspections",
    "06-packing-and-first-week",
    "07-tax-record-habits",
    "appendix-a-negotiation-questions",
    "appendix-b-packing-checklist",
    "appendix-c-glossary",
]

STYLE_CSS = """\
:root {
  --ink: #2b2a33;
  --soft: #6b6878;
  --accent: #0e7c66;
  --accent-soft: #e6f4f0;
  --bg: #fbf9f6;
  --card: #ffffff;
  --line: #e8e2d9;
  --code: #f4f1ec;
}
* { box-sizing: border-box; }
html { scroll-behavior: smooth; }
body {
  margin: 0;
  background: var(--bg);
  color: var(--ink);
  font: 17px/1.65 Georgia, "Times New Roman", serif;
}
a { color: var(--accent); text-decoration-thickness: 1px; text-underline-offset: 2px; }
a:hover { text-decoration-thickness: 2px; }
.wrap { max-width: 760px; margin: 0 auto; padding: 0 20px; }
header.site {
  border-bottom: 1px solid var(--line);
  background: var(--card);
}
header.site .wrap { display: flex; align-items: baseline; justify-content: space-between; padding: 14px 20px; flex-wrap: wrap; gap: 8px; }
header.site .brand { font-weight: bold; letter-spacing: 0.2px; color: var(--ink); text-decoration: none; }
header.site .brand small { color: var(--soft); font-weight: normal; }
main { padding: 34px 20px 60px; }
article { max-width: 760px; margin: 0 auto; }
h1, h2, h3, h4 { line-height: 1.25; color: #1f1e26; font-family: Georgia, serif; }
h1 { font-size: 2rem; margin: 0.2em 0 0.6em; }
h2 { font-size: 1.42rem; margin: 1.7em 0 0.5em; border-bottom: 1px solid var(--line); padding-bottom: 0.25em; }
h3 { font-size: 1.13rem; margin: 1.3em 0 0.4em; color: #33323b; }
p { margin: 0.7em 0; }
ul, ol { padding-left: 1.4em; }
li { margin: 0.3em 0; }
blockquote {
  margin: 1em 0; padding: 0.7em 1.1em;
  border-left: 4px solid var(--accent);
  background: var(--accent-soft);
  border-radius: 0 8px 8px 0;
  color: #215147;
}
blockquote p { margin: 0.25em 0; }
code {
  font: 0.86em/1.5 ui-monospace, "SF Mono", Menlo, Consolas, monospace;
  background: var(--code); padding: 0.15em 0.4em; border-radius: 5px;
}
pre {
  background: var(--code); padding: 14px 16px; border-radius: 10px;
  overflow-x: auto; border: 1px solid var(--line);
}
pre code { background: none; padding: 0; }
table { border-collapse: collapse; width: 100%; margin: 1.1em 0; font-size: 0.94em; }
th, td { border: 1px solid var(--line); padding: 7px 10px; text-align: left; vertical-align: top; }
th { background: var(--code); font-family: system-ui, sans-serif; font-size: 0.86em; text-transform: uppercase; letter-spacing: 0.4px; color: #4d4a58; }
tr:nth-child(even) td { background: #fcfaf7; }
hr { border: none; border-top: 1px solid var(--line); margin: 2em 0; }
.title-lead { color: var(--soft); font-style: italic; margin-top: -0.4em; }
.disclaimer {
  background: #fdf6e9; border: 1px solid #f0e2c4; border-radius: 10px;
  padding: 10px 16px; font-size: 0.88em; color: #6d5a2e; margin-bottom: 1.6em;
}
.toc { columns: 2; column-gap: 34px; padding-left: 1.2em; }
.toc li { break-inside: avoid; }
nav.page {
  display: flex; justify-content: space-between; gap: 16px;
  margin-top: 3em; padding-top: 1.2em; border-top: 1px solid var(--line);
  font-family: system-ui, sans-serif; font-size: 0.92em;
}
nav.page a { max-width: 48%; }
nav.page .next { margin-left: auto; text-align: right; }
nav.page .dir { display: block; color: var(--soft); font-size: 0.85em; text-transform: uppercase; letter-spacing: 0.5px; }
footer.site {
  border-top: 1px solid var(--line); margin-top: 40px;
  padding: 22px 20px 40px; color: var(--soft); font-size: 0.86em;
  font-family: system-ui, sans-serif; text-align: center;
}
@media (max-width: 640px) {
  .toc { columns: 1; }
  h1 { font-size: 1.7rem; }
}
"""

DISCLAIMER = (
    "This guide is educational only. It is never contract, legal, tax, or medical advice. "
    "Confirm specifics with the agency\u2019s written contract, your state board of nursing, "
    "and licensed professionals."
)

FOOTER = (
    "The Travel Nurse First-Contract Guide \u2014 an education-only project by "
    "Asdale Dynamics, LLC. No contracts were advised in the making of this site."
)


def slugify_heading(text: str) -> str:
    raw = re.sub(r"<[^>]+>", "", text).lower()
    raw = re.sub(r"[^\w\s-]", "", raw, flags=re.ASCII)
    return re.sub(r"[\s]+", "-", raw.strip()) or "heading"


def slugify_filename(stem: str) -> str:
    return stem


def inline(text: str) -> str:
    """Inline markdown -> HTML, escaping HTML first."""
    text = html.escape(text, quote=False)
    text = re.sub(r"\*\*\*([^*\n](?:[^*\n]*[^*\n])?)\*\*\*", r"<strong><em>\1</em></strong>", text)
    text = re.sub(r"\*\*([^*\n](?:[^*\n]*[^*\n])?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<![\w*])\*([^*\n](?:[^*\n]*[^*\n])?)\*(?![\w*])", r"<em>\1</em>", text)
    text = re.sub(r"~~([^~\n]+)~~", r"<del>\1</del>", text)
    text = re.sub(r"`([^`\n]+)`", r"<code>\1</code>", text)
    text = re.sub(r"\[([^\]\n]+)\]\(([^)\s]+)\)", r'<a href="\2">\1</a>', text)
    return text


def _table_cell(text: str) -> str:
    # Trim marker lists that leaked into first table cell, then inline-format.
    text = re.sub(r"^<strong>\s*", "", text) if text.startswith("<strong>") else text
    return "<td>" + inline(text) + "</td>"


def parse_blocks(lines):
    """Split markdown source into typed blocks."""
    blocks = []
    i = 0
    n = len(lines)
    while i < n:
        line = lines[i]

        # Fenced code block
        if line.startswith("```"):
            lang = line[3:].strip()
            code = []
            i += 1
            while i < n and not lines[i].startswith("```"):
                code.append(lines[i])
                i += 1
            i += 1  # closing fence
            blocks.append(("code", (lang, code)))
            continue

        # ATX heading
        m = re.match(r"^(#{1,4})\s+(.*)$", line)
        if m:
            blocks.append(("heading", (len(m.group(1)), m.group(2).strip())))
            i += 1
            continue

        # Horizontal rule
        if re.match(r"^\s*(\*\s*){3,}$|^\s*(-\s*){3,}$|^\s*(_\s*){3,}$", line):
            blocks.append(("hr", ""))
            i += 1
            continue

        # Blockquote (possibly multi-line)
        if line.lstrip().startswith(">"):
            quote = []
            while i < n and lines[i].lstrip().startswith(">"):
                quote.append(re.sub(r"^\s*>\s?", "", lines[i]))
                i += 1
            blocks.append(("quote", quote))
            continue

        # Table: | header | header |  followed by | --- | --- |
        if line.lstrip().startswith("|") and i + 1 < n and re.match(r"^\s*\|?[\s:|-]*-[\s:|-]*$", lines[i + 1]) and "|-" in lines[i + 1].replace(" ", ""):
            header = [c.strip() for c in line.strip().strip("|").split("|")]
            i += 2
            rows = []
            while i < n and lines[i].lstrip().startswith("|"):
                rows.append([c.strip() for c in lines[i].strip().strip("|").split("|")])
                i += 1
            blocks.append(("table", (header, rows)))
            continue

        # Checkbox list item
        if re.match(r"^\s*-\s+\[[ xX]\]\s?", line):
            items = []
            while i < n and re.match(r"^\s*-\s+\[[ xX]\]\s?", lines[i]):
                checked = bool(re.match(r"^\s*-\s+\[[xX]\]", lines[i]))
                content = re.sub(r"^\s*-\s+\[[ xX]\]\s?", "", lines[i])
                items.append((checked, content))
                i += 1
            blocks.append(("checklist", items))
            continue

        # Unordered list
        if re.match(r"^\s*[-*]\s+", line):
            items = []
            while i < n and re.match(r"^\s*[-*]\s+", lines[i]):
                items.append(re.sub(r"^\s*[-*]\s+", "", lines[i]))
                i += 1
            blocks.append(("ul", items))
            continue

        # Ordered list
        if re.match(r"^\s*\d+[.)]\s+", line):
            items = []
            while i < n and re.match(r"^\s*\d+[.)]\s+", lines[i]):
                items.append(re.sub(r"^\s*\d+[.)]\s+", "", lines[i]))
                i += 1
            blocks.append(("ol", items))
            continue

        # Blank line
        if not line.strip():
            i += 1
            continue

        # Paragraph (gathers until blank line or a block starter)
        para = [line]
        i += 1
        while i < n and lines[i].strip() and not re.match(
            r"^(#{1,4}\s|```|\s*[-*]\s|\s*\d+[.)]\s|\s*>\s?\||\||```|\s*(\*\s*){3,})",
            lines[i],
        ):
            para.append(lines[i])
            i += 1
        blocks.append(("para", para))

    return blocks


def block_to_html(block) -> str:
    kind, payload = block
    if kind == "heading":
        level, text = payload
        slug = slugify_heading(text)
        return f'<h{level} id="{html.escape(slug, quote=True)}">{inline(text)}</h{level}>'
    if kind == "para":
        return "<p>" + inline(" ".join(s.strip() for s in payload)) + "</p>"
    if kind == "ul":
        lis = "".join(f"<li>{inline(it)}</li>" for it in payload)
        return f"<ul>{lis}</ul>"
    if kind == "ol":
        lis = "".join(f"<li>{inline(it)}</li>" for it in payload)
        return f"<ol>{lis}</ol>"
    if kind == "checklist":
        lis = "".join(
            f'<li><input type="checkbox" disabled{" checked" if checked else ""}> {inline(text)}</li>'
            for checked, text in payload
        )
        return f'<ul class="checklist">{lis}</ul>'
    if kind == "quote":
        inner = "".join(f"<p>{inline(s)}</p>" for s in payload)
        return f"<blockquote>{inner}</blockquote>"
    if kind == "hr":
        return "<hr>"
    if kind == "code":
        lang, code_lines = payload
        body = html.escape("\n".join(code_lines))
        return f"<pre><code>{body}</code></pre>"
    if kind == "table":
        header, rows = payload
        cols = len(header)
        thead = "<tr>" + "".join(f"<th>{inline(h)}</th>" for h in header) + "</tr>"
        body_rows = []
        for r in rows:
            cells = list(r) + [""] * (cols - len(r))
            body_rows.append("<tr>" + "".join("<td>%s</td>" % inline(c) for c in cells[:cols]) + "</tr>")
        return f"<table><thead>{thead}</thead><tbody>{''.join(body_rows)}</tbody></table>"
    raise ValueError(f"unknown block kind: {kind}")


def extract_title(blocks) -> str:
    for kind, payload in blocks:
        if kind == "heading" and payload[0] == 1:
            return payload[1]
    return "Untitled"


def extract_lead(blocks) -> str:
    """Find the italic tagline paragraph after the H1, if any."""
    for idx, (kind, payload) in enumerate(blocks):
        if kind == "heading" and payload[0] == 1:
            for kind2, payload2 in blocks[idx + 1 : idx + 4]:
                if kind2 == "para" and payload2 and payload2[0].strip().startswith("*") and payload2[0].strip().endswith("*"):
                    lead = payload2[0].strip().strip("*").strip()
                    return inline(lead)
                break
            return ""
    return ""


def is_disclaimer_para(blocks) -> bool:
    first_para = next((p for k, p in blocks if k == "para"), None)
    return bool(first_para and "education" in first_para[0].lower())


def render_doc_html(text: str) -> str:
    """Markdown doc -> inner HTML (article content), with headings slugged."""
    lines = text.splitlines()
    blocks = parse_blocks(lines)
    parts = [block_to_html(b) for b in blocks]
    return "\n".join(parts)


H1_RE = re.compile(r"<h1[^>]*>(.*?)</h1>", re.DOTALL)


def split_title(content: str):
    """Pull the first h1 out of rendered content; return (title, lead, rest)."""
    m = H1_RE.search(content)
    if not m:
        return "Untitled", "", content
    title = re.sub(r"<[^>]+>", "", m.group(1)).strip()
    rest = content[: m.start()] + content[m.end() :]
    return title, rest


def build_toc(pages):
    lis = [
        f'<li><a href="{page["filename"]}">{html.escape(page["title"])}</a></li>'
        for page in pages
    ]
    return "<ul class='toc'>" + "".join(lis) + "</ul>"


PAGE_TEMPLATE = """\
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} — Travel Nurse First-Contract Guide</title>
<meta name="description" content="Education-only manual for nurses taking travel assignments: agencies, contract clauses in plain English, NLC compact licensing, honest pay-package comparisons, housing inspections, packing, and tax-record habits.">
<meta name="author" content="Asdale Dynamics, LLC">
<link rel="stylesheet" href="style.css">
</head>
<body>
<header class="site">
  <div class="wrap">
    <a class="brand" href="index.html">The Travel Nurse First-Contract Guide</a>
    <small>Education only &middot; never contract or legal advice</small>
  </div>
</header>
<main>
  <article>
  {disclaimer}
  {content}
  <nav class="page">
    {prev_link}
    {next_link}
  </nav>
  </article>
</main>
<footer class="site">
  {footer}
  <br>Copyright (c) 2026 Asdale Dynamics, LLC
</footer>
</body>
</html>
"""


LEAD_RE = re.compile(r"\s*<p><em>(.*?)</em></p>", re.DOTALL)


def decorate_content(title: str, content: str) -> str:
    """Re-inject the page H1 (split_title removed it) and style the tagline."""
    lead = ""
    m = LEAD_RE.match(content)
    if m and len(m.group(1)) < 200:
        lead = f'<p class="title-lead">{m.group(1)}</p>'
        content = content[m.end() :]
    return f"<h1>{html.escape(title)}</h1>\n{lead}\n{content}"


def build(out_dir: Path = SITE, quiet: bool = False) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "style.css").write_text(STYLE_CSS, encoding="utf-8")

    pages = []
    for stem in PAGE_ORDER:
        path = DOCS / f"{stem}.md"
        if not path.exists():
            raise SystemExit(f"build error: missing docs/{stem}.md")
        rendered = render_doc_html(path.read_text(encoding="utf-8"))
        title, rest = split_title(rendered)
        pages.append({"stem": stem, "filename": f"{slugify_filename(stem)}.html", "title": title, "content": rest})

    # Page order sanity: every docs file is in PAGE_ORDER and vice versa.
    actual = sorted(p.stem for p in DOCS.glob("*.md"))
    if actual != sorted(PAGE_ORDER):
        missing = sorted(set(actual) - set(PAGE_ORDER))
        extra = sorted(set(PAGE_ORDER) - set(actual))
        raise SystemExit(f"build error: docs/ and PAGE_ORDER mismatch; missing={missing} extra={extra}")

    toc_html = build_toc(pages)

    for idx, page in enumerate(pages):
        prev_link = ""
        next_link = ""
        if idx > 0:
            prev_link = (
                f'<a class="prev" href="{pages[idx-1]["filename"]}">'
                f'<span class="dir">Previous</span>{html.escape(pages[idx-1]["title"])}</a>'
            )
        else:
            prev_link = "<span></span>"
        if idx < len(pages) - 1:
            next_link = (
                f'<a class="next" href="{pages[idx+1]["filename"]}">'
                f'<span class="dir">Next</span>{html.escape(pages[idx+1]["title"])}</a>'
            )
        else:
            next_link = "<span></span>"

        content = decorate_content(page["title"], page["content"])
        if page["stem"] == "index":
            # Add a full table of contents under the chapter map.
            if '<h2 id="chapter-map">' in content:
                content = content.replace(
                    "</table>",
                    "</table>\n<h2 id=\"contents\">Contents</h2>\n" + toc_html,
                    1,
                )

        html_text = PAGE_TEMPLATE.format(
            title=html.escape(page["title"]),
            disclaimer=f'<div class="disclaimer">{html.escape(DISCLAIMER)}</div>',
            content=content,
            prev_link=prev_link,
            next_link=next_link,
            footer=html.escape(FOOTER),
        )
        (out_dir / page["filename"]).write_text(html_text, encoding="utf-8")
        if not quiet:
            print(f"  built {page['filename']}")

    if not quiet:
        print(f"Built {len(pages)} pages into {out_dir}")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Build the static site from docs/.")
    parser.add_argument("--check", action="store_true", help="Build and verify output; exit non-zero on failure.")
    parser.add_argument("--out", default=None, help="Output directory (default: site/)")
    args = parser.parse_args(argv)

    out_dir = Path(args.out) if args.out else SITE
    build(out_dir=out_dir)

    if args.check:
        expected = [f"{s}.html" for s in PAGE_ORDER]
        problems = [f for f in expected if not (out_dir / f).exists()]
        if problems:
            print("check FAILED; missing pages:", problems)
            return 1
        print("check OK — all pages present.")
    print(f"Site generated at {out_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
