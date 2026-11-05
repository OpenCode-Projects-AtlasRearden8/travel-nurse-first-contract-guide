# The Travel Nurse First-Contract Guide

An **education-only** manual for registered nurses taking their first travel
assignment: agency types decoded, contract clauses in plain English,
NLC compact licensing basics, honest pay-package comparisons, furnished-housing
inspections, packing and first-week routines, and simple tax-record habits.

It is **not** contract, legal, tax, or medical advice. Confirm everything that
matters with the agency's written contract, your state board of nursing, and
licensed professionals.

| Fact | Value |
|---|---|
| Format | Markdown chapters + a static HTML site |
| Build | `python3 build.py` (Python 3 standard library only) |
| Tests | `python3 -m unittest discover -s tests` |
| License | MIT — see [LICENSE](LICENSE) |
| Owner | Asdale Dynamics, LLC |

## Read it

1. **Locally (recommended):** run `python3 build.py`, then open `site/index.html`
   in any browser. No server needed.
2. **As text:** every chapter lives in [`docs/`](docs/), in plain Markdown.

Chapters:

- `docs/index.md` — who this is for, and how to use it
- `docs/01-agency-types.md` — national, boutique, local, MSP/VMS, W2 vs 1099
- `docs/02-contract-clauses.md` — guarantees, cancellations, stipends, overtime
- `docs/03-compact-licensing.md` — NLC multistate licensing basics
- `docs/04-pay-packages.md` — a worksheet for comparing offers honestly
- `docs/05-housing-inspections.md` — the ten-minute arrival walk-through
- `docs/06-packing-and-first-week.md` — the first 96 hours, made boring
- `docs/07-tax-record-habits.md` — ten weekly minutes that fix April
- `docs/appendix-a-negotiation-questions.md` — 34 questions for recruiter calls
- `docs/appendix-b-packing-checklist.md` — the copy-me packing list
- `docs/appendix-c-glossary.md` — a translator for traveler jargon

## Build the site

```bash
python3 build.py            # writes site/ (11 HTML pages + style.css)
python3 build.py --check    # build, then verify all pages exist
python3 build.py --out out  # build into a custom directory
```

The build uses only the Python standard library — no packages to install,
nothing to fetch, fully offline and local-first.

## Run the tests

```bash
python3 -m unittest discover -s tests -v
```

Tests cover: every doc page present and titled, no broken internal links,
markdown conversion (tables, checklists, fences, escaping), the generated
site (all pages built, nav links resolve, disclaimer present on every page),
and the LICENSE/README copyright lines.

## Intended audience

Nurses moving into travel assignments who want plain-English preparation
before signing anything. This guide is deliberately distinct from a
new-nurse-first-year guide: it assumes an experienced, licensed nurse and
focuses entirely on the *logistics of contracting and relocating*.

## About

An education project by **Asdale Dynamics, LLC** — beginner-friendly manuals,
guides, and practical tools, written "like a friend would": clear, warm, and
tested. This project collects no data, runs no network calls, and contains no
secrets. Copyright (c) 2026 Asdale Dynamics, LLC.
