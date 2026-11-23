#!/usr/bin/env python3
"""Check consistency between the security best practices feature matrix and the guide.

Files compared:
  workstreams/best-practices/security-best-practices-feature-matrix.md
  deliverables/DRAFT-agentic-ai-security-best-practices-guide.md

Only matrix rows that cite the guide ([SPAA-BP-Guide]) are checked against it.
Rows sourced from other documents (for example [ADK-Safety]) are checked for
structure only.

Every inconsistency is reported as a warning. The script exits 0 unless
--strict is passed, so it can run as a non-blocking GitHub Action step. When
GITHUB_ACTIONS is set, warnings are emitted as workflow annotations.

Checks:
  1. Links to the guide point at an existing file and an existing heading anchor.
  2. Row IDs are well formed, unique, and match the matrix section number.
  3. The Type column only holds Technology, Process, or People.
  4. Backticked terms, numbers, durations, percentages, RFC numbers, Tier/Step
     labels, and named tools in guide-cited rows also appear in the guide.
  5. Leaf guide sections covered by the matrix are cited by at least one row.

Standard library only. Requires Python 3.8 or later.
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_MATRIX = "workstreams/best-practices/security-best-practices-feature-matrix.md"
DEFAULT_GUIDE = "deliverables/DRAFT-agentic-ai-security-best-practices-guide.md"
GUIDE_SOURCE_TAG = "SPAA-BP-Guide"
VALID_TYPES = {"Technology", "Process", "People"}

LINK_RE = re.compile(r"\]\(([^)\s#]+\.md)(?:#([^)\s]*))?\)")
ROW_ID_RE = re.compile(r"^(\d+)\.(\d+)\.(\d+)$")
MATRIX_H2_RE = re.compile(r"^##\s+(\d+)\.\s")
HEADING_RE = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")
NUMBERED_RE = re.compile(r"^(\d+(?:\.\d+)*)\.?\s")


@dataclass
class Warning_:
    path: str
    line: int
    title: str
    message: str


@dataclass
class Heading:
    level: int
    text: str
    slug: str
    line: int
    number: str = ""
    has_children: bool = False


@dataclass
class Row:
    line: int
    row_id: str
    practice: str
    feature: str
    types: str
    citation: str


@dataclass
class Report:
    warnings: list = field(default_factory=list)

    def add(self, path: str, line: int, title: str, message: str) -> None:
        self.warnings.append(Warning_(path, line, title, message))


def rel(path: Path) -> str:
    try:
        return os.path.relpath(path, Path.cwd())
    except ValueError:
        return str(path)


def slugify(text: str) -> str:
    """Approximate the GitHub heading anchor algorithm."""
    text = re.sub(r"`([^`]*)`", r"\1", text)
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)
    text = text.strip().lower()
    text = re.sub(r"[^\w\- ]", "", text)
    return text.replace(" ", "-")


def parse_headings(lines: list) -> list:
    headings = []
    seen = {}
    in_fence = False
    in_front_matter = bool(lines) and lines[0].strip() == "---"
    for idx, raw in enumerate(lines, start=1):
        stripped = raw.strip()
        if in_front_matter:
            if idx > 1 and stripped == "---":
                in_front_matter = False
            continue
        if stripped.startswith("```") or stripped.startswith("~~~"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        match = HEADING_RE.match(raw)
        if not match:
            continue
        text = match.group(2)
        slug = slugify(text)
        count = seen.get(slug, 0)
        seen[slug] = count + 1
        if count:
            slug = f"{slug}-{count}"
        num_match = NUMBERED_RE.match(text)
        headings.append(
            Heading(len(match.group(1)), text, slug, idx, num_match.group(1) if num_match else "")
        )
    for i, head in enumerate(headings):
        if i + 1 < len(headings) and headings[i + 1].level > head.level:
            head.has_children = True
    return headings


def split_cells(line: str) -> list:
    body = line.strip()
    if body.startswith("|"):
        body = body[1:]
    if body.endswith("|"):
        body = body[:-1]
    return [cell.strip() for cell in re.split(r"(?<!\\)\|", body)]


def parse_rows(lines: list) -> list:
    rows = []
    for idx, raw in enumerate(lines, start=1):
        if not raw.lstrip().startswith("|"):
            continue
        cells = split_cells(raw)
        if len(cells) < 5 or not re.match(r"^\d", cells[0]):
            continue
        rows.append(Row(idx, cells[0], cells[1], cells[2], cells[3], cells[4]))
    return rows


def normalize(text: str) -> str:
    """Lowercase, drop markdown emphasis, unify dashes, and unify quantity phrasing."""
    text = text.replace("`", "").replace("*", "")
    text = re.sub(r"[\u2010-\u2015\u2212]", "-", text)
    text = text.lower()
    text = re.sub(r"(\d+)[- ](days?|hours?|weeks?|months?|minutes?|bits?)\b", r"\1 \2", text)
    text = re.sub(r"\b(days?|hours?|weeks?|months?|minutes?|bits?)\b", lambda m: m.group(1).rstrip("s"), text)
    return re.sub(r"\s+", " ", text)


def extract_backticked(text: str) -> list:
    return [t for t in re.findall(r"`([^`]+)`", text) if t.strip()]


QUANTITY_PATTERNS = [
    r"\d+(?:\.\d+)?(?:\s?[–-]\s?\d+(?:\.\d+)?)?\s?%",
    r"[≥≤]?\s?\d+[- ](?:day|hour|week|month|minute|bit)s?\b",
    r"\b(?:weeks?|months?)\s\d+(?:\s?[–-]\s?\d+)?\+?",
    r"\bTier\s\d\b",
    r"\bStep\s\d\b",
    r"\bRFC\s\d+\b",
    r"\bOAuth\s\d\.\d\b",
]


def extract_quantities(text: str) -> list:
    cleaned = text.replace("`", "")
    found = []
    for pattern in QUANTITY_PATTERNS:
        for match in re.finditer(pattern, cleaned, flags=re.IGNORECASE):
            token = match.group(0).lstrip("≥≤ ").strip()
            if token not in found:
                found.append(token)
    return found


def extract_named_items(text: str) -> list:
    """Return capitalized names inside parentheses, such as tools and products."""
    items = []
    for group in re.findall(r"\(([^()]*)\)", text.replace("`", "")):
        for segment in re.split(r",|;|\bor\b", group):
            segment = re.sub(r"^\s*(e\.g\.|i\.e\.)\s*", "", segment.strip(), flags=re.IGNORECASE).strip()
            if not segment or not segment[0].isupper():
                continue
            if segment not in items:
                items.append(segment)
    return items


def section_for_anchor(headings: list, slug: str):
    for head in headings:
        if head.slug == slug:
            return head
    return None


def check_links(matrix_path: Path, guide_path: Path, matrix_lines: list,
                guide_headings: list, report: Report) -> dict:
    """Validate links. Return {anchor: count} for anchors that resolve in the guide."""
    matrix_rel = rel(matrix_path)
    guide_slugs = {h.slug for h in guide_headings}
    cited = {}
    reported = set()
    for idx, raw in enumerate(matrix_lines, start=1):
        for match in LINK_RE.finditer(raw):
            target, anchor = match.group(1), match.group(2)
            resolved = (matrix_path.parent / target).resolve()
            if not resolved.exists():
                key = ("file", target)
                if key not in reported:
                    reported.add(key)
                    report.add(matrix_rel, idx, "Broken link",
                               f"Linked file '{target}' does not exist.")
                continue
            if resolved != guide_path.resolve() or anchor is None:
                continue
            if anchor in guide_slugs:
                cited[anchor] = cited.get(anchor, 0) + 1
            else:
                key = ("anchor", anchor)
                if key not in reported:
                    reported.add(key)
                    suggestions = ", ".join(sorted(s for s in guide_slugs if s[:2] == anchor[:2])[:4])
                    hint = f" Guide anchors with a similar prefix: {suggestions}." if suggestions else ""
                    report.add(matrix_rel, idx, "Unresolved guide anchor",
                               f"Anchor '#{anchor}' is not a heading in the guide.{hint}")
    return cited


def check_structure(matrix_path: Path, matrix_lines: list, rows: list, report: Report) -> None:
    matrix_rel = rel(matrix_path)
    current_section = None
    section_by_line = {}
    for idx, raw in enumerate(matrix_lines, start=1):
        match = MATRIX_H2_RE.match(raw)
        if match:
            current_section = match.group(1)
        section_by_line[idx] = current_section

    seen = {}
    for row in rows:
        id_match = ROW_ID_RE.match(row.row_id)
        if not id_match:
            report.add(matrix_rel, row.line, "Malformed row ID",
                       f"Row ID '{row.row_id}' does not match the N.N.N pattern.")
            continue
        if row.row_id in seen:
            report.add(matrix_rel, row.line, "Duplicate row ID",
                       f"Row ID {row.row_id} also appears on line {seen[row.row_id]}.")
        else:
            seen[row.row_id] = row.line
        section = section_by_line.get(row.line)
        if section is not None and id_match.group(1) != section:
            report.add(matrix_rel, row.line, "Row ID section mismatch",
                       f"Row {row.row_id} sits under matrix section {section}.")
        types = [t.strip() for t in row.types.split(",") if t.strip()]
        bad = [t for t in types if t not in VALID_TYPES]
        if not types or bad:
            report.add(matrix_rel, row.line, "Invalid Type value",
                       f"Row {row.row_id} has Type '{row.types}'. Allowed values: "
                       f"{', '.join(sorted(VALID_TYPES))}.")


def check_content(matrix_path: Path, rows: list, guide_text_norm: str, report: Report) -> int:
    matrix_rel = rel(matrix_path)
    checked = 0
    for row in rows:
        if GUIDE_SOURCE_TAG not in row.citation:
            continue
        checked += 1
        combined = f"{row.practice} {row.feature}"
        missing = []

        for term in extract_backticked(combined):
            if normalize(term) not in guide_text_norm:
                missing.append(f"term `{term}`")

        for qty in extract_quantities(combined):
            if normalize(qty) not in guide_text_norm:
                missing.append(f"value '{qty}'")

        # Parentheses in the practice column are scope qualifiers, so only the
        # feature column is searched for tool and product names.
        for item in extract_named_items(row.feature):
            if normalize(item) in guide_text_norm:
                continue
            parts = [p for p in item.split("/") if p.strip()]
            if len(parts) > 1:
                absent = [p.strip() for p in parts if normalize(p) not in guide_text_norm]
                missing.extend(f"name '{p}'" for p in absent)
            else:
                missing.append(f"name '{item}'")

        if missing:
            report.add(matrix_rel, row.line, "Matrix item not found in guide",
                       f"Row {row.row_id} mentions {', '.join(missing)}, which the guide does not contain.")
    return checked


def check_coverage(guide_path: Path, headings: list, cited: dict, report: Report) -> None:
    """Warn when a leaf guide section in a matrix-covered area has no citing row."""
    cited_headings = [h for h in headings if h.slug in cited]
    covered_tops = {h.number.split(".")[0] for h in cited_headings if h.number}
    guide_rel = rel(guide_path)

    def covered(head: Heading) -> bool:
        if head.slug in cited:
            return True
        # A citation to a descendant section covers its ancestors.
        start = headings.index(head)
        for later in headings[start + 1:]:
            if later.level <= head.level:
                break
            if later.slug in cited:
                return True
        return False

    for head in headings:
        if not head.number or head.has_children or head.level < 2:
            continue
        if head.number.split(".")[0] not in covered_tops:
            continue
        if not covered(head):
            report.add(guide_rel, head.line, "Guide section not in matrix",
                       f"Guide section '{head.text}' (#{head.slug}) has no row in the feature matrix.")


def escape_annotation(value: str) -> str:
    return value.replace("%", "%25").replace("\r", "%0D").replace("\n", "%0A")


def emit(report: Report) -> None:
    in_actions = os.environ.get("GITHUB_ACTIONS") == "true"
    for w in sorted(report.warnings, key=lambda x: (x.path, x.line)):
        if in_actions:
            print(f"::warning file={w.path},line={w.line},title={escape_annotation(w.title)}::"
                  f"{escape_annotation(w.message)}")
        else:
            print(f"WARNING: {w.path}:{w.line}: [{w.title}] {w.message}")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--matrix", default=str(REPO_ROOT / DEFAULT_MATRIX), help="Path to the feature matrix.")
    parser.add_argument("--guide", default=str(REPO_ROOT / DEFAULT_GUIDE), help="Path to the best practices guide.")
    parser.add_argument("--strict", action="store_true", help="Exit 1 when any warning is reported.")
    args = parser.parse_args(argv)

    matrix_path, guide_path = Path(args.matrix).resolve(), Path(args.guide).resolve()
    for path in (matrix_path, guide_path):
        if not path.is_file():
            print(f"ERROR: file not found: {path}", file=sys.stderr)
            return 2

    matrix_lines = matrix_path.read_text(encoding="utf-8").splitlines()
    guide_lines = guide_path.read_text(encoding="utf-8").splitlines()
    guide_headings = parse_headings(guide_lines)
    rows = parse_rows(matrix_lines)
    guide_norm = normalize("\n".join(guide_lines))

    report = Report()
    cited = check_links(matrix_path, guide_path, matrix_lines, guide_headings, report)
    check_structure(matrix_path, matrix_lines, rows, report)
    checked = check_content(matrix_path, rows, guide_norm, report)
    check_coverage(guide_path, guide_headings, cited, report)

    emit(report)
    print(f"Checked {len(rows)} matrix rows ({checked} cite the guide) against "
          f"{len(guide_headings)} guide headings: {len(report.warnings)} warning(s).")
    return 1 if (args.strict and report.warnings) else 0


if __name__ == "__main__":
    sys.exit(main())
