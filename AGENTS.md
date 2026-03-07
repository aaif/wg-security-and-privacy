# Repository — Agent Instructions

This repository contains the working documents of the **AAIF Security and Privacy Working Group**, including the charter, deliverables, and meeting notes.

## Repository Structure

| Folder | Purpose | Has own AGENTS.md |
|--------|---------|-------------------|
| `charter/` | Working group charter and governance documents | No |
| `deliverables/` | Published deliverables produced by the working group | Yes |
| `meeting-notes/` | Meeting notes, agendas, and summaries | Yes |

Always check for a folder-level `AGENTS.md` before making changes inside a subdirectory — it contains folder-specific workflow and naming rules.

## General Conventions

- All Markdown files use standard CommonMark syntax.
- Use ATX-style headings (`#`, `##`, etc.), not Setext-style.
- Dates follow `YYYY-MM-DD` format everywhere (filenames, table cells, prose).
- Keep tables aligned and sorted as specified in the relevant `README.md`.
- After adding or modifying a file in a subdirectory, update that folder's `README.md` if it maintains an index or table of contents.

## Root README

The root `README.md` is the public-facing landing page for the repository. When editing it:

- Keep the **Repository Structure** table in sync with actual folder contents.
- Update the **Next meeting** date after each meeting occurs.
- Do not remove or reorder existing sections without explicit instruction.

## Charter

The charter lives in `charter/DRAFT.md`. It remains in draft status until formally approved by the working group. Do not rename or remove the `DRAFT` prefix without a recorded meeting decision approving the charter.

## Commit Messages

- Use imperative mood (e.g., "Add meeting notes for 2026-03-17").
- Reference the relevant folder or deliverable in the message when the change is scoped to one area.
