#!/usr/bin/env python3
"""Audit evidence bookkeeping for a literature-to-lecture project.

This checks files and recorded evidence, not scientific correctness or search recall.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path


def resolve(base: Path, value: str) -> Path:
    p = Path(value).expanduser()
    return p if p.is_absolute() else base / p


def require_text(obj: dict, key: str, label: str, errors: list[str]) -> str:
    value = obj.get(key)
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{label}: missing {key}")
        return ""
    return value.strip()


def check_file(base: Path, name: str, label: str, errors: list[str]) -> Path | None:
    if not name:
        return None
    p = resolve(base, name)
    if not p.is_file() or p.stat().st_size == 0:
        errors.append(f"{label}: file missing or empty: {p}")
        return None
    return p


def pdf_pages(path: Path) -> int | None:
    if not shutil.which("pdfinfo"):
        return None
    result = subprocess.run(["pdfinfo", str(path)], capture_output=True, text=True)
    if result.returncode:
        return None
    match = re.search(r"^Pages:\s+(\d+)\s*$", result.stdout, re.MULTILINE)
    return int(match.group(1)) if match else None


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def audit(manifest: Path) -> tuple[list[str], list[str], int]:
    errors: list[str] = []
    warnings: list[str] = []
    try:
        data = json.loads(manifest.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        return [f"cannot read manifest: {exc}"], warnings, 0
    if not isinstance(data, dict):
        return ["manifest root must be an object"], warnings, 0
    base = manifest.parent
    require_text(data, "scope", "manifest", errors)
    cutoff = require_text(data, "cutoff", "manifest", errors)
    if cutoff and not re.fullmatch(r"\d{4}-\d{2}-\d{2}", cutoff):
        errors.append("manifest: cutoff must be YYYY-MM-DD")
    log = check_file(base, require_text(data, "search_log", "manifest", errors), "search log", errors)
    if log and log.stat().st_size < 100:
        warnings.append("search log is very short; inspect query and citation-chasing evidence")
    lecture = check_file(base, require_text(data, "lecture", "manifest", errors), "lecture", errors)
    lecture_text = lecture.read_text(encoding="utf-8") if lecture else ""
    headings = {line.lstrip("# ").strip() for line in lecture_text.splitlines() if line.startswith("#")}
    unresolved = data.get("unresolved_candidates")
    if not isinstance(unresolved, list):
        errors.append("manifest: unresolved_candidates must be an array, even when empty")
    elif unresolved:
        errors.append(f"manifest: {len(unresolved)} unresolved in-scope candidate(s) remain")
    records = data.get("records")
    if not isinstance(records, list) or not records:
        errors.append("manifest: records must be a nonempty array")
        return errors, warnings, 0

    seen_ids: set[str] = set()
    seen_dois: set[str] = set()
    for index, rec in enumerate(records, 1):
        label = f"record {index}"
        if not isinstance(rec, dict):
            errors.append(f"{label}: must be an object")
            continue
        paper_id = require_text(rec, "id", label, errors)
        label = paper_id or label
        if paper_id in seen_ids:
            errors.append(f"{label}: duplicate ID")
        seen_ids.add(paper_id)
        require_text(rec, "title", label, errors)
        require_text(rec, "authors", label, errors)
        require_text(rec, "kind", label, errors)
        url = require_text(rec, "primary_url", label, errors)
        if not isinstance(rec.get("year"), int):
            errors.append(f"{label}: year must be an integer")
        doi = rec.get("doi", "")
        if doi and not isinstance(doi, str):
            errors.append(f"{label}: doi must be text")
            doi = ""
        if doi:
            doi_key = re.sub(r"^https?://(?:dx\.)?doi\.org/", "", doi.strip(), flags=re.I).lower()
            if doi_key in seen_dois:
                errors.append(f"{label}: duplicate DOI {doi_key}")
            seen_dois.add(doi_key)
        if lecture_text and not (url in lecture_text or (doi and doi_key in lecture_text.lower())):
            errors.append(f"{label}: primary URL or DOI not cited in lecture")

        full = rec.get("full_text")
        if not isinstance(full, dict):
            errors.append(f"{label}: full_text must be an object")
        else:
            path_name = require_text(full, "path", f"{label}.full_text", errors)
            path = check_file(base, path_name, f"{label}.full_text", errors)
            digest = require_text(full, "sha256", f"{label}.full_text", errors).lower()
            require_text(full, "version", f"{label}.full_text", errors)
            retrieved = require_text(full, "retrieved", f"{label}.full_text", errors)
            if retrieved and not re.fullmatch(r"\d{4}-\d{2}-\d{2}", retrieved):
                errors.append(f"{label}.full_text: retrieved must be YYYY-MM-DD")
            if digest and not re.fullmatch(r"[0-9a-f]{64}", digest):
                errors.append(f"{label}.full_text: sha256 must be 64 hexadecimal characters")
            if path:
                actual = sha256_file(path)
                if digest and actual != digest:
                    errors.append(f"{label}.full_text: SHA-256 mismatch")
                if path.suffix.lower() == ".pdf":
                    with path.open("rb") as stream:
                        is_pdf = stream.read(5) == b"%PDF-"
                    if not is_pdf:
                        errors.append(f"{label}.full_text: file is not a PDF")
                    pages = full.get("pages")
                    if not isinstance(pages, int) or pages < 1:
                        errors.append(f"{label}.full_text: PDF needs positive page count")
                    actual_pages = pdf_pages(path)
                    if actual_pages is None:
                        warnings.append(f"{label}.full_text: page count not independently checked (pdfinfo unavailable or failed)")
                    elif pages != actual_pages:
                        errors.append(f"{label}.full_text: page count says {pages}, file has {actual_pages}")
                elif path.suffix.lower() not in {".html", ".htm", ".xml", ".tei"}:
                    warnings.append(f"{label}.full_text: inspect unusual full-text format {path.suffix}")

        reading = rec.get("reading")
        if not isinstance(reading, dict):
            errors.append(f"{label}: reading must be an object")
        else:
            if reading.get("status") != "complete":
                errors.append(f"{label}.reading: status must be complete")
            note_name = require_text(reading, "note_path", f"{label}.reading", errors)
            note = check_file(base, note_name, f"{label}.reading", errors)
            if note and note.stat().st_size < 300:
                warnings.append(f"{label}.reading: note is short; inspect for substantive reading")
            locations = reading.get("evidence_locators")
            if not isinstance(locations, list) or not any(isinstance(x, str) and x.strip() for x in locations):
                errors.append(f"{label}.reading: add page/section/figure evidence locators")
            equations = reading.get("equations")
            no_equation = reading.get("no_central_equation_reason", "")
            if not isinstance(equations, list):
                errors.append(f"{label}.reading: equations must be an array")
                equations = []
            if not equations and not (isinstance(no_equation, str) and no_equation.strip()):
                errors.append(f"{label}.reading: record central equations or a reason none applies")
            for number, eq in enumerate(equations, 1):
                eq_label = f"{label}.equation {number}"
                if not isinstance(eq, dict):
                    errors.append(f"{eq_label}: must be an object")
                    continue
                for key in ("source_locator", "latex", "meaning", "assumptions"):
                    require_text(eq, key, eq_label, errors)
                if not isinstance(eq.get("variables"), dict):
                    errors.append(f"{eq_label}: variables must be a dictionary, even if empty")
        sections = rec.get("lecture_sections")
        if not isinstance(sections, list) or not sections:
            errors.append(f"{label}: lecture_sections must name at least one section")
        else:
            for section in sections:
                if not isinstance(section, str) or section.strip() not in headings:
                    errors.append(f"{label}: lecture heading not found: {section!r}")
    return errors, warnings, len(records)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    args = parser.parse_args()
    errors, warnings, count = audit(args.manifest)
    print(f"Audited {count} record(s): {'READY' if not errors else 'INCOMPLETE'}")
    for issue in errors:
        print(f"ERROR: {issue}")
    for issue in warnings:
        print(f"WARN: {issue}")
    return 0 if not errors else 2


if __name__ == "__main__":
    sys.exit(main())
