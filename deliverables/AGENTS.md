# Deliverables — Agent Instructions

## Adding a New Deliverable

1. Every new deliverable starts with **Draft** status. Name the file with a `DRAFT-` prefix followed by a kebab-case title (e.g., `DRAFT-threat-model-framework.md`).
2. Add a row to the table in `README.md` in alphabetical order by name. Set the status to **Draft** and the last modified date to today's date (`YYYY-MM-DD`).

## Editing a Deliverable

- Update the **Last Modified** date in the `README.md` table whenever a deliverable's content changes.
- Keep the table sorted alphabetically by name after any addition or rename.

## Moving a Deliverable from Draft to Final

A deliverable **must not** be moved to Final status unless there is a corresponding meeting in `../meeting-notes/` whose **Decisions** section explicitly records the group's approval of that deliverable.

Before changing status to Final:

1. Identify the meeting date where the deliverable was approved.
2. Verify the meeting notes file (`../meeting-notes/YYYY-MM-DD.md`) exists and contains a decision approving the deliverable.
3. If no such meeting decision exists, **do not** move the deliverable to Final. Instead, inform the user that a working group meeting decision is required before a deliverable can be finalized.

When finalizing:

1. Rename the file by removing the `DRAFT-` prefix (e.g., `DRAFT-threat-model-framework.md` becomes `threat-model-framework.md`).
2. Update the `README.md` table: change the status to **Final**, update the link to the new filename, and set the last modified date.
3. Add a note at the top of the deliverable referencing the meeting that approved it (e.g., `> Approved by the working group on YYYY-MM-DD ([meeting notes](../meeting-notes/YYYY-MM-DD.md)).`).

## Moving a Deliverable to Another Workstream

When a deliverable is handed off to a cross-WG workstream or another repository, turn it into a redirect so its history and inbound links stay intact.

1. Replace the deliverable file's content with a short redirect note that records the new home, links to the destination repository, and explains how this WG stays involved.
2. Keep the existing filename so inbound links continue to resolve.
3. In the `README.md` table, set the status to **Moved**, update the last modified date, and point the link to the destination repository.

## Status Values

| Status | File Prefix | Meaning |
|--------|-------------|---------|
| Draft  | `DRAFT-`    | Work in progress; not yet approved by the working group |
| Final  | *(none)*    | Approved by the working group in a recorded meeting decision |
| Moved  | *(retained)* | Handed off to another workstream or repository; the file remains as a redirect to the new home |

## Communication Style

Apply these guidelines to all writing in this repository, including documents, commit messages, pull request descriptions, and responses to users:

- Do not use contrastive language.
- Do not line break with horizontal rules.
- Don't be a sycophant.
- Be direct, but don't use partial clauses in your sentence structure.
- Use complete thoughts that flow naturally.
- Provide a neutral voice that's both playful but professional at the same time.
