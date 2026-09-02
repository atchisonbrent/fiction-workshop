#!/usr/bin/env python3
"""Freeze the current working set of a story into an immutable release snapshot.

Releasing was previously a hand-performed ritual: copy four files, hash them,
hand-write ``manifest.json``, hand-edit ``status``, hand-embed the frozen scope
budget. Every step is a chance to freeze the wrong thing, and the validator can
only prove that a manifest matches its files, not that the files match intent.

This script performs the ritual deterministically and refuses to proceed unless
the working set already validates. It never touches an existing release tree.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

from validate_story import (  # noqa: E402
    RELEASE_REQUIRED_FILES,
    assemble_manuscript,
    chapter_files,
    file_sha256,
    load_json,
    validate_story,
)


def dump_json(value: Any) -> str:
    return json.dumps(value, indent=2, ensure_ascii=False) + "\n"


def working_prose(story: Path) -> bytes:
    """Return the prose to freeze: assembled chapters, else working/manuscript.md."""
    chapters = chapter_files(story)
    manuscript = story / "working" / "manuscript.md"
    if chapters:
        assembled = assemble_manuscript(chapters).encode("utf-8")
        if manuscript.is_file() and manuscript.read_bytes() != assembled:
            raise ValueError(
                "working/manuscript.md is stale relative to working/chapters/; "
                "regenerate it before releasing"
            )
        return assembled
    if manuscript.is_file() and not manuscript.is_symlink():
        return manuscript.read_bytes()
    raise ValueError("nothing to release: no working/chapters/*.md or working/manuscript.md")


def build_release(story: Path, *, dry_run: bool) -> Path:
    validate_story(story)

    project = load_json(story / "project.json")
    contract = load_json(story / "working" / "release-contract.json")
    release_id = contract["release_id"]
    released = story / "release-contracts" / release_id
    if released.exists():
        raise ValueError(
            f"release {release_id} already exists; bump working release_id "
            "(and normally set parent_release_id) before releasing again"
        )
    if contract.get("manuscript_status", "draft") != "complete":
        raise ValueError(
            "working release contract must declare manuscript_status 'complete' "
            "before it can be released"
        )

    frozen_contract = dict(contract)
    frozen_contract["status"] = "released"
    frozen_contract["frozen_scope_budget"] = project["current_scope_budget"]

    outputs: dict[str, bytes] = {
        "contract.json": dump_json(frozen_contract).encode("utf-8"),
        "kernel.md": (story / "kernel.md").read_bytes(),
        "approved-draft.md": working_prose(story),
        "canon.json": (story / "working" / "canon.json").read_bytes(),
    }
    assert set(outputs) == RELEASE_REQUIRED_FILES

    if dry_run:
        print(f"would release {release_id} with files: {', '.join(sorted(outputs))}")
        return released

    released.mkdir(parents=True, exist_ok=False)
    for name, data in outputs.items():
        (released / name).write_bytes(data)
    manifest = {
        "schema_version": 1,
        "release_id": release_id,
        "files": {name: file_sha256(released / name) for name in sorted(outputs)},
    }
    (released / "manifest.json").write_text(dump_json(manifest), encoding="utf-8")

    # Re-validate so a half-written release never survives silently.
    validate_story(story)
    return released


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("story", type=Path, help="Path to a story directory")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate and report what would be frozen without writing anything",
    )
    args = parser.parse_args(argv)
    try:
        released = build_release(args.story.resolve(), dry_run=args.dry_run)
    except ValueError as exc:
        print(f"release failed: {exc}", file=sys.stderr)
        return 1
    if not args.dry_run:
        print(f"released: {released.relative_to(args.story.resolve())}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
