# STATUS

**Project:** The Travel Nurse First-Contract Guide
**Owner:** Asdale Dynamics, LLC
**Date:** 2026-11-05
**Status:** Complete, built, and verified locally

## What was built

An education-only manual for licensed nurses taking their first travel
assignment — never contract, legal, tax, or medical advice. Content is
deliberately distinct from a new-nurse-first-year guide: it assumes an
experienced nurse and focuses on contracting and relocation logistics.

**Content (11 Markdown pages in `docs/`):**

- `index.md` — who this is for, what it is/is not, chapter map + full contents
- `01-agency-types.md` — national/boutique/local agencies, MSP/VMS, W2 vs 1099, recruiter tips
- `02-contract-clauses.md` — guaranteed hours, cancellations, housing stipends, overtime, clause table
- `03-compact-licensing.md` — NLC/multistate license basics, PSOR, non-compact planning
- `04-pay-packages.md` — taxable wage vs allowances, an 8-row comparison worksheet, red flags
- `05-housing-inspections.md` — ten-minute move-in inspection, photo-documentation habit
- `06-packing-and-first-week.md` — packing philosophy, documents pouch, day-by-day first week
- `07-tax-record-habits.md` — 10-minute weekly record habit, folder structure, questions for a tax pro
- `appendix-a-negotiation-questions.md` — 34 negotiation questions grouped by topic
- `appendix-b-packing-checklist.md` — copy-me packing checklist with checkboxes
- `appendix-c-glossary.md` — alphabetized glossary of traveler jargon

**Static site (`site/`, generated):** one HTML page per doc page, with a shared
stylesheet, a disclaimer banner on every page, prev/next navigation, heading
anchors, a contents list on the index, and print-able checklists. Self-contained
and openable directly via `file://` — fully local-first, no JS, no fonts, no
network calls, no analytics.

**Tooling:**

- `build.py` — stdlib-only Markdown→HTML site generator with `--check` (verifies output) and `--out` options
- `tests/test_build.py` — 24 unit tests (source-consistency, markdown conversion, site output, license/README metadata)
- `run_tests.sh` — convenience script: build with check, then run tests

## How to run it

```bash
python3 build.py              # generate site/ (needs only Python 3, stdlib only)
open site/index.html          # or double-click it in your file manager

./run_tests.sh                # build --check + all tests
python3 -m unittest discover -s tests -v   # tests only
```

## Verification results

- `python3 build.py --check` — OK: all 11 pages written.
- `python3 -m unittest discover -s tests` — **24/24 tests passed** (0 failures, 0 errors).
- Internal links: automated test confirms every generated page's links resolve to real pages.
- Content checks: no unrendered Markdown in output; no secrets/API keys/emails in docs (test-enforced); disclaimer present on every generated page.
- Site generated from a clean directory works in any browser via `file://`.

## Known gaps / limitations

- **No full-text search in the static site** — navigation is linear via the contents list and prev/next links.
- The Markdown converter is purpose-built for this guide's feature set (headings, lists, tables, fenced code, blockquotes, checkbox lists). It is not a general-purpose Markdown tool.
- State-level details (cancellation norms, licensing timelines, stipend tax treatment) vary and change; the guide teaches habits and questions rather than promising current specifics — readers are pointed to boards, the compact's official site, and professionals.
- No RSS/EPUB/PDF export (possible future addition).
- Site styling is a single hand-written stylesheet; no dark-mode toggle.
- `site/` is git-ignored (generated); a fresh clone must run `python3 build.py` once.
