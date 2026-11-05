#!/usr/bin/env python3
"""Tests for the Travel Nurse First-Contract Guide build.

Run with: python3 -m unittest discover -s tests -v
(Or via run_tests.sh.)
"""

import re
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import build  # noqa: E402

DOCS = ROOT / "docs"


class TestSourceDocs(unittest.TestCase):
    """The Markdown source itself should be consistent and complete."""

    def test_all_doc_files_exist_and_match_page_order(self):
        actual = sorted(p.stem for p in DOCS.glob("*.md"))
        self.assertEqual(actual, sorted(build.PAGE_ORDER))

    def test_docs_have_h1_titles(self):
        for stem in build.PAGE_ORDER:
            text = (DOCS / f"{stem}.md").read_text(encoding="utf-8")
            self.assertTrue(
                text.lstrip().startswith("# "),
                f"{stem}.md must start with an H1 title",
            )

    def test_no_broken_internal_links(self):
        # Links of the form [text](something.md) or [text](something.html)
        # should point at real doc pages.
        stems = set(build.PAGE_ORDER)
        for stem in build.PAGE_ORDER:
            text = (DOCS / f"{stem}.md").read_text(encoding="utf-8")
            for link in re.findall(r"\]\(([^)\s]+)\)", text):
                if link.startswith("http"):
                    continue
                target = link.rsplit(".", 1)[0]
                self.assertIn(target, stems, f"{stem}.md links to unknown page: {link}")

    def test_appendices_present(self):
        required = [
            "appendix-a-negotiation-questions",
            "appendix-b-packing-checklist",
            "appendix-c-glossary",
        ]
        for stem in required:
            self.assertTrue((DOCS / f"{stem}.md").exists())

    def test_no_secrets_or_emails_in_docs(self):
        for stem in build.PAGE_ORDER:
            text = (DOCS / f"{stem}.md").read_text(encoding="utf-8")
            self.assertNotRegex(text, r"(?i)(api[_-]?key|secret|password\s*[:=])")
            self.assertNotRegex(text, r"[\w.]+@[\w-]+\.[a-z]{2,}")

    def test_disclaimer_words_present_in_intro(self):
        text = (DOCS / "index.md").read_text(encoding="utf-8")
        self.assertIn("education-only", text.lower())

    def test_guide_is_distinct_from_first_year_guide(self):
        # This project must be about travel contracts, not first-year nursing.
        text = (DOCS / "index.md").read_text(encoding="utf-8")
        self.assertIn("travel", text.lower())
        self.assertIn("contract", text.lower())


class TestMarkdownConversion(unittest.TestCase):
    def test_bold_italic_code_and_links(self):
        html_out = build.render_doc_html("**bold** *ital* `code` [x](y.html)")
        self.assertIn("<strong>bold</strong>", html_out)
        self.assertIn("<em>ital</em>", html_out)
        self.assertIn("<code>code</code>", html_out)
        self.assertIn('<a href="y.html">x</a>', html_out)

    def test_heading_gets_slug_id(self):
        html_out = build.render_doc_html("## The Unusual Clause!")
        self.assertIn('id="the-unusual-clause"', html_out)

    def test_table_renders(self):
        md = "| a | b |\n|---|---|\n| 1 | 2 |\n"
        html_out = build.render_doc_html(md)
        self.assertIn("<table>", html_out)
        self.assertIn("<th>a</th>", html_out)
        self.assertIn("<td>1</td>", html_out)

    def test_fenced_code_renders_and_escapes(self):
        html_out = build.render_doc_html("```\n<b>&raw\n```")
        self.assertIn("&lt;b&gt;", html_out)

    def test_blockquote_renders(self):
        html_out = build.render_doc_html("> quoted line")
        self.assertIn("<blockquote>", html_out)

    def test_checklist_renders(self):
        html_out = build.render_doc_html("- [ ] task\n- [x] done")
        self.assertIn('type="checkbox"', html_out)
        self.assertIn("checked", html_out)

    def test_html_is_escaped_in_paragraphs(self):
        html_out = build.render_doc_html("<script>alert(1)</script>")
        self.assertNotIn("<script>", html_out)


class TestSiteBuild(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="site-test-"))
        build.build(out_dir=self.tmp, quiet=True)

    def tearDown(self):
        import shutil

        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_every_page_built(self):
        for stem in build.PAGE_ORDER:
            p = self.tmp / f"{stem}.html"
            self.assertTrue(p.exists(), f"missing {p.name}")

    def test_stylesheet_written(self):
        self.assertTrue((self.tmp / "style.css").exists())

    def test_titles_rendered(self):
        text = (self.tmp / "index.html").read_text(encoding="utf-8")
        self.assertIn("The Travel Nurse First-Contract Guide", text)

    def test_nav_links_point_to_real_pages(self):
        hrefs = set()
        for page in self.tmp.glob("*.html"):
            hrefs |= set(re.findall(r'href="([^"#]+\.html)"', page.read_text(encoding="utf-8")))
        files = {p.name for p in self.tmp.glob("*.html")}
        self.assertEqual(hrefs - files, set())

    def test_disclaimer_in_footer_of_each_page(self):
        for page in self.tmp.glob("*.html"):
            text = page.read_text(encoding="utf-8")
            self.assertIn("never contract, legal, tax, or medical advice", text, f"missing in {page.name}")

    def test_owner_credit_present(self):
        text = (self.tmp / "index.html").read_text(encoding="utf-8")
        self.assertIn("Asdale Dynamics, LLC", text)

    def test_no_unrendered_markdown_in_output(self):
        for page in self.tmp.glob("*.html"):
            text = page.read_text(encoding="utf-8")
            self.assertNotRegex(text, r"\*\*[^*\n]+\*\*", f"raw bold in {page.name}")
            self.assertNotRegex(text, r"<h2 id=. missing", f"check {page.name}")

    def test_index_has_toc(self):
        text = (self.tmp / "index.html").read_text(encoding="utf-8")
        self.assertIn("Contents", text)
        self.assertIn("<ul class='toc'>", text)


class TestLicensesAndMetadata(unittest.TestCase):
    def test_license_copyright_line_exact(self):
        license_text = (ROOT / "LICENSE").read_text(encoding="utf-8")
        self.assertIn("Copyright (c) 2026 Asdale Dynamics, LLC", license_text)

    def test_readme_credits_llc(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("Asdale Dynamics, LLC", readme)


if __name__ == "__main__":
    unittest.main()
