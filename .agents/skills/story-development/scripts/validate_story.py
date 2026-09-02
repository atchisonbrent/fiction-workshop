#!/usr/bin/env python3
"""Validate deterministic structure for a fiction-workshop story."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any


VALID_RESOLUTIONS = {"flash", "short", "novella", "novel", "custom"}
VALID_TARGET_MODES = {"fixed", "bounded", "exploratory"}
VALID_CLOSURE_POSTURES = {"closed", "open_by_design", "ambiguous_by_design"}
VALID_REVISIT_POLICIES = {"preserve", "expandable", "adaptation_only"}
VALID_PUBLICATION_SHAPES = {
    "standalone",
    "episodic",
    "serial",
    "collection_part",
    "custom",
}
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
RELEASE_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
RELEASE_REQUIRED_FILES = {
    "contract.json",
    "kernel.md",
    "approved-draft.md",
    "canon.json",
}
CANON_STATUSES = {
    "proposed",
    "established",
    "character_belief",
    "rumor_or_claim",
    "unresolved",
    "retconned",
    "rejected_branch",
}
PROVENANCE_REQUIRED_STATUSES = {
    "established",
    "character_belief",
    "rumor_or_claim",
    "retconned",
}
CHAPTER_JOINER = "\n\n---\n\n"


def chapter_files(story: Path) -> list[Path]:
    """Return working chapter files in assembly order, or [] when none exist."""
    chapters = story / "working" / "chapters"
    if not chapters.is_dir() or chapters.is_symlink():
        return []
    return sorted(
        path for path in chapters.glob("*.md") if path.is_file() and not path.is_symlink()
    )


def assemble_manuscript(chapters: list[Path]) -> str:
    """Deterministically assemble chapter files into one manuscript text."""
    return CHAPTER_JOINER.join(
        path.read_text(encoding="utf-8").rstrip("\n") for path in chapters
    ) + "\n"


def heading_anchor(heading: str) -> str:
    """Derive a stable slug from a Markdown heading line (without the leading #s)."""
    text = re.sub(r"[^\w\s-]", "", heading.strip().lower())
    return re.sub(r"[\s_]+", "-", text).strip("-")


def provenance_targets(story: Path, chapters: list[Path]) -> set[str]:
    """Collect every identifier a canon provenance may resolve to.

    Chapter file stems, chapter headings (as slugs), and every scene/beat ID in
    ``outline/scenes/*.json`` count. The special value ``kernel`` always resolves.
    """
    targets: set[str] = {"kernel"}
    for chapter in chapters:
        targets.add(chapter.stem)
        for line in chapter.read_text(encoding="utf-8").splitlines():
            if line.startswith("#"):
                slug = heading_anchor(line.lstrip("#"))
                if slug:
                    targets.add(slug)
    scenes = story / "outline" / "scenes"
    if scenes.is_dir() and not scenes.is_symlink():
        for scene_file in sorted(scenes.glob("*.json")):
            if not scene_file.is_file() or scene_file.is_symlink():
                continue
            scene = load_json(scene_file)
            if isinstance(scene, dict) and isinstance(scene.get("id"), str):
                targets.add(scene["id"])
    return targets


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError(f"missing required file: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid JSON in {path}: {exc}") from exc


def require_mapping(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be an object")
    return value


def require_fields(value: dict[str, Any], fields: set[str], label: str) -> None:
    missing = sorted(field for field in fields if field not in value)
    if missing:
        raise ValueError(f"{label} missing fields: {', '.join(missing)}")


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_scope_budget(budget: dict[str, Any], label: str) -> None:
    require_fields(
        budget,
        {
            "planning_resolution",
            "publication_shape",
            "target_mode",
            "reader_promise",
            "closure_posture",
            "revisit_policy",
        },
        label,
    )
    if budget["planning_resolution"] not in VALID_RESOLUTIONS:
        raise ValueError(f"{label} has invalid planning_resolution")
    if budget["publication_shape"] not in VALID_PUBLICATION_SHAPES:
        raise ValueError(f"{label} has invalid publication_shape")
    if budget["target_mode"] not in VALID_TARGET_MODES:
        raise ValueError(f"{label} has invalid target_mode")
    if budget["closure_posture"] not in VALID_CLOSURE_POSTURES:
        raise ValueError(f"{label} has invalid closure_posture")
    if budget["revisit_policy"] not in VALID_REVISIT_POLICIES:
        raise ValueError(f"{label} has invalid revisit_policy")
    if not isinstance(budget["reader_promise"], str) or not budget["reader_promise"].strip():
        raise ValueError(f"{label} reader_promise must be a non-empty string")


def validate_complexity(complexity: dict[str, Any]) -> None:
    require_fields(
        complexity,
        {"pov_count", "subplot_count", "timeline_nonlinear", "world_rule_density"},
        "complexity",
    )
    for field in ("pov_count", "subplot_count"):
        if type(complexity[field]) is not int or complexity[field] < 0:
            raise ValueError(f"complexity {field} must be a non-negative integer")
    if not isinstance(complexity["timeline_nonlinear"], bool):
        raise ValueError("complexity timeline_nonlinear must be boolean")
    density = complexity["world_rule_density"]
    if density not in {"low", "medium", "high", "custom"}:
        raise ValueError("complexity has invalid world_rule_density")


def validate_canon(canon: dict[str, Any], label: str) -> None:
    require_fields(canon, {"lineage", "facts"}, label)
    lineage = canon["lineage"]
    facts = canon["facts"]
    if not isinstance(lineage, str) or not lineage:
        raise ValueError(f"{label} lineage must be a non-empty string")
    if not isinstance(facts, list):
        raise ValueError(f"{label} facts must be an array")

    seen: set[str] = set()
    for index, raw_fact in enumerate(facts):
        fact = require_mapping(raw_fact, f"{label} fact {index}")
        require_fields(fact, {"id", "status", "statement"}, f"{label} fact {index}")
        fact_id = fact["id"]
        if not isinstance(fact_id, str) or not fact_id:
            raise ValueError(f"{label} fact {index} has invalid ID")
        if fact_id in seen:
            raise ValueError(f"duplicate fact ID in lineage {lineage}: {fact_id}")
        seen.add(fact_id)
        status = fact["status"]
        if status not in CANON_STATUSES:
            raise ValueError(f"{label} fact {fact_id} has invalid status")
        if not isinstance(fact["statement"], str) or not fact["statement"].strip():
            raise ValueError(f"{label} fact {fact_id} has invalid statement")
        if status in PROVENANCE_REQUIRED_STATUSES:
            require_fields(fact, {"provenance"}, f"{label} fact {fact_id}")
            if not isinstance(fact["provenance"], str) or not fact["provenance"].strip():
                raise ValueError(f"{label} fact {fact_id} has invalid provenance")
        if status == "retconned":
            require_fields(
                fact,
                {"supersedes", "decision_ref"},
                f"{label} fact {fact_id}",
            )


def validate_working_retcons(
    story: Path,
    canon: dict[str, Any],
    parent_release_id: str | None,
) -> None:
    retcons = [fact for fact in canon["facts"] if fact["status"] == "retconned"]
    if not retcons:
        return
    if parent_release_id is None:
        raise ValueError("working retcon requires a parent release")

    ancestor_fact_ids: set[str] = set()
    visited: set[str] = set()
    current: str | None = parent_release_id
    while current is not None:
        if current in visited:
            raise ValueError(f"release parent cycle detected at: {current}")
        visited.add(current)
        release = story / "release-contracts" / current
        ancestor_canon = require_mapping(
            load_json(release / "canon.json"),
            f"{current}/canon.json",
        )
        ancestor_fact_ids.update(fact["id"] for fact in ancestor_canon["facts"])
        ancestor_contract = require_mapping(
            load_json(release / "contract.json"),
            f"{current}/contract.json",
        )
        current = ancestor_contract["parent_release_id"]

    for fact in retcons:
        supersedes = fact["supersedes"]
        if not isinstance(supersedes, str) or supersedes not in ancestor_fact_ids:
            raise ValueError(f"retcon supersedes no ancestor fact: {supersedes}")
        decision_ref = fact["decision_ref"]
        if not isinstance(decision_ref, str):
            raise ValueError(f"retcon {fact['id']} has invalid decision_ref")
        relative = Path(decision_ref)
        if (
            relative.is_absolute()
            or ".." in relative.parts
            or not relative.parts
            or relative.parts[0] != "decisions"
        ):
            raise ValueError(f"retcon {fact['id']} has unsafe decision_ref")
        decision = story / relative
        if not decision.is_file() or decision.is_symlink():
            raise ValueError(f"retcon decision note does not exist: {decision_ref}")


def validate_released_snapshots(story: Path) -> None:
    releases = story / "release-contracts"
    if not releases.exists():
        return
    if not releases.is_dir() or releases.is_symlink():
        raise ValueError("release-contracts must be a real directory")

    for release in sorted(releases.iterdir()):
        if release.is_symlink():
            raise ValueError(f"release directory cannot be a symlink: {release.name}")
        if not release.is_dir():
            continue
        if not RELEASE_ID_RE.fullmatch(release.name):
            raise ValueError(f"unsafe release directory name: {release.name}")
        manifest_path = release / "manifest.json"
        manifest = require_mapping(load_json(manifest_path), str(manifest_path))
        require_fields(manifest, {"schema_version", "release_id", "files"}, str(manifest_path))
        if manifest["release_id"] != release.name:
            raise ValueError(f"release ID does not match directory: {release}")
        files = require_mapping(manifest["files"], f"{manifest_path} files")
        missing_manifest_entries = sorted(RELEASE_REQUIRED_FILES - set(files))
        if missing_manifest_entries:
            raise ValueError(
                f"{release.name}/manifest.json missing protected files: "
                + ", ".join(missing_manifest_entries)
            )
        for relative_name, expected_hash in sorted(files.items()):
            if not isinstance(relative_name, str) or not isinstance(expected_hash, str):
                raise ValueError(f"{release.name}/manifest.json entries must be strings")
            relative = Path(relative_name)
            if relative.is_absolute() or ".." in relative.parts:
                raise ValueError(f"unsafe release manifest path: {relative_name}")
            if not SHA256_RE.fullmatch(expected_hash):
                raise ValueError(f"invalid SHA-256 in {release.name}/manifest.json: {relative_name}")
            protected = release / relative
            if not protected.is_file() or protected.is_symlink():
                raise ValueError(f"missing protected release file: {release.name}/{relative_name}")
            if file_sha256(protected) != expected_hash:
                raise ValueError(f"hash mismatch: {release.name}/{relative_name}")

        released_canon = require_mapping(
            load_json(release / "canon.json"),
            f"{release.name}/canon.json",
        )
        validate_canon(released_canon, f"{release.name}/canon.json")

        contract = require_mapping(load_json(release / "contract.json"), "released contract")
        require_fields(
            contract,
            {
                "release_id",
                "status",
                "parent_release_id",
                "reader_promise",
                "required_payoffs",
                "frozen_scope_budget",
            },
            f"{release.name}/contract.json",
        )
        if contract["release_id"] != release.name or contract["status"] != "released":
            raise ValueError(f"invalid released contract identity or status: {release.name}")
        parent_release_id = contract["parent_release_id"]
        if parent_release_id is not None:
            if not isinstance(parent_release_id, str) or not parent_release_id:
                raise ValueError(f"invalid released parent ID: {release.name}")
            if not RELEASE_ID_RE.fullmatch(parent_release_id):
                raise ValueError(f"unsafe released parent ID: {parent_release_id}")
            if parent_release_id == release.name:
                raise ValueError(f"released contract cannot parent itself: {release.name}")
            parent = releases / parent_release_id
            if not parent.is_dir() or parent.is_symlink():
                raise ValueError(
                    f"released parent does not exist: {release.name} -> {parent_release_id}"
                )
        frozen = require_mapping(
            contract["frozen_scope_budget"],
            f"{release.name}/contract.json frozen_scope_budget",
        )
        validate_scope_budget(frozen, f"{release.name}/contract.json frozen_scope_budget")
        if frozen.get("target_words") is not None:
            try:
                approved_text = (release / "approved-draft.md").read_text(encoding="utf-8")
            except (OSError, UnicodeError) as exc:
                raise ValueError(
                    f"cannot read released approved draft {release.name}: {exc}"
                ) from exc
            validate_text_word_budget(
                approved_text,
                frozen.get("target_words"),
                "released approved draft",
            )


def validate_release_parent_cycles(story: Path) -> None:
    releases = story / "release-contracts"
    if not releases.is_dir():
        return
    release_ids = {
        path.name
        for path in releases.iterdir()
        if path.is_dir() and not path.is_symlink()
    }
    for start in sorted(release_ids):
        visited: set[str] = set()
        current: str | None = start
        while current is not None:
            if current in visited:
                raise ValueError(f"release parent cycle detected at: {current}")
            visited.add(current)
            contract = require_mapping(
                load_json(releases / current / "contract.json"),
                f"{current}/contract.json",
            )
            current = contract["parent_release_id"]


def validate_text_word_budget(text: str, raw_target: Any, label: str) -> None:
    target = require_mapping(raw_target, f"{label} target_words")
    require_fields(target, {"min", "preferred", "max"}, f"{label} target_words")
    minimum, preferred, maximum = target["min"], target["preferred"], target["max"]
    if any(type(value) is not int or value < 1 for value in (minimum, preferred, maximum)):
        raise ValueError("target_words values must be positive integers")
    if not minimum <= preferred <= maximum:
        raise ValueError("target_words must satisfy min <= preferred <= max")
    word_count = len(re.findall(r"\b[\w’'-]+\b", text))
    if word_count < minimum:
        raise ValueError(f"{label} word count {word_count} is below minimum {minimum}")
    if word_count > maximum:
        raise ValueError(f"{label} word count {word_count} exceeds maximum {maximum}")


def validate_working_provenance(story: Path, canon: dict[str, Any]) -> None:
    """When chapters exist, working provenance must resolve to real prose or scenes.

    Short-form stories with no chapter files keep free-form provenance: the whole
    text fits one reading and unresolved labels cost nothing. Once prose is split
    into chapters, a provenance that names nothing defeats targeted retrieval.

    Only an actively drafted working set is checked. A working set at rest on a
    released ID is governed by ``validate_working_matches_release`` instead; its
    frozen provenance is history, and a child release is where it gets repaired.
    """
    chapters = chapter_files(story)
    if not chapters:
        return
    targets = provenance_targets(story, chapters)
    for fact in canon["facts"]:
        if fact["status"] not in PROVENANCE_REQUIRED_STATUSES:
            continue
        provenance = fact["provenance"].strip()
        if provenance not in targets:
            raise ValueError(
                f"working/canon.json fact {fact['id']} provenance does not resolve to a "
                f"chapter file, chapter heading, scene ID, or 'kernel': {provenance}"
            )


def working_is_at_rest(story: Path, contract: dict[str, Any]) -> bool:
    """True when the working release ID already has a released snapshot."""
    released = story / "release-contracts" / contract["release_id"]
    return released.is_dir() and not released.is_symlink()


def validate_working_matches_release(story: Path, contract: dict[str, Any]) -> None:
    """A working set that reuses a released ID must still equal that release.

    Between releasing and opening a child, the working tree legitimately points at
    the released ID. Editing it in that state silently mutates what the release
    claims to have frozen, so require byte equality until a new working release
    ID (normally a child naming this one as parent) is created.
    """
    release_id = contract["release_id"]
    released = story / "release-contracts" / release_id
    pairs = [
        (story / "kernel.md", released / "kernel.md", "kernel.md"),
        (story / "working" / "canon.json", released / "canon.json", "working/canon.json"),
    ]
    for working_path, released_path, label in pairs:
        if working_path.read_bytes() != released_path.read_bytes():
            raise ValueError(
                f"{label} differs from released {release_id}; create a child working "
                "release instead of editing a released story"
            )
    chapters = chapter_files(story)
    manuscript = story / "working" / "manuscript.md"
    if chapters:
        working_text = assemble_manuscript(chapters)
    elif manuscript.is_file() and not manuscript.is_symlink():
        working_text = manuscript.read_text(encoding="utf-8")
    else:
        return
    approved = (released / "approved-draft.md").read_text(encoding="utf-8")
    if working_text != approved:
        raise ValueError(
            f"working prose differs from released {release_id}/approved-draft.md; "
            "create a child working release instead of editing a released story"
        )


def validate_manuscript(
    story: Path,
    budget: dict[str, Any],
    contract: dict[str, Any],
) -> None:
    status = contract.get("manuscript_status", "draft")
    if status not in {"planned", "draft", "complete"}:
        raise ValueError(f"invalid manuscript_status: {status}")
    chapters = chapter_files(story)
    manuscript = story / "working" / "manuscript.md"
    if chapters and manuscript.is_file() and not manuscript.is_symlink():
        if manuscript.read_text(encoding="utf-8") != assemble_manuscript(chapters):
            raise ValueError(
                "working/manuscript.md is stale: it does not equal the chapter files "
                "joined in sorted order with '\\n\\n---\\n\\n'"
            )
    if status != "complete":
        return

    if not manuscript.is_file() or manuscript.is_symlink():
        raise ValueError("complete manuscript requires working/manuscript.md")
    try:
        text = manuscript.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise ValueError(f"cannot read complete manuscript: {exc}") from exc
    validate_text_word_budget(
        text,
        budget.get("target_words"),
        "complete manuscript",
    )


def validate_story(story: Path) -> str:
    license_marker = story / "LICENSE.md"
    if not license_marker.is_file() or license_marker.is_symlink():
        raise ValueError("LICENSE.md must exist, be nonempty, and not be a symlink")
    try:
        license_text = license_marker.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise ValueError(f"cannot read LICENSE.md: {exc}") from exc
    if not license_text.strip():
        raise ValueError("LICENSE.md must exist, be nonempty, and not be a symlink")
    if not re.search(r"(?im)^\s*copyright\b.+$", license_text):
        raise ValueError("LICENSE.md must include a copyright notice naming the owner")
    if not re.search(
        r"(?i)\b(?:all rights reserved|licensed under|permission is hereby granted)\b",
        license_text,
    ):
        raise ValueError("LICENSE.md must state the story's license terms")

    project = require_mapping(load_json(story / "project.json"), "project.json")
    require_fields(
        project,
        {
            "schema_version",
            "story_id",
            "title",
            "active_release_id",
            "current_scope_budget",
            "complexity",
        },
        "project.json",
    )
    budget = require_mapping(project["current_scope_budget"], "current_scope_budget")
    validate_scope_budget(budget, "current_scope_budget")
    complexity = require_mapping(project["complexity"], "complexity")
    validate_complexity(complexity)

    kernel = story / "kernel.md"
    if not kernel.is_file() or not kernel.read_text(encoding="utf-8").strip():
        raise ValueError("kernel.md must exist and be non-empty")

    contract = require_mapping(
        load_json(story / "working" / "release-contract.json"),
        "working/release-contract.json",
    )
    require_fields(
        contract,
        {"release_id", "status", "parent_release_id", "reader_promise", "required_payoffs"},
        "working/release-contract.json",
    )
    if contract["status"] != "working":
        raise ValueError("working release contract must have status 'working'")
    if not isinstance(contract["release_id"], str) or not RELEASE_ID_RE.fullmatch(
        contract["release_id"]
    ):
        raise ValueError(f"unsafe working release ID: {contract['release_id']}")
    if contract["release_id"] != project["active_release_id"]:
        raise ValueError("active_release_id does not match working release contract")

    canon = require_mapping(load_json(story / "working" / "canon.json"), "working/canon.json")
    validate_canon(canon, "working/canon.json")

    resolution = budget["planning_resolution"]
    beats = story / "outline" / "beats.md"
    has_beats = beats.is_file() and bool(beats.read_text(encoding="utf-8").strip())
    if resolution == "flash" and not has_beats:
        raise ValueError("flash working set requires outline/beats.md")
    if resolution == "short" and not has_beats:
        scenes = story / "outline" / "scenes"
        scene_files = (
            sorted(path for path in scenes.glob("*.json") if path.is_file() and not path.is_symlink())
            if scenes.is_dir() and not scenes.is_symlink()
            else []
        )
        if not scene_files:
            raise ValueError("short working set requires outline/beats.md or outline/scenes/*.json")
        for scene_file in scene_files:
            scene = require_mapping(load_json(scene_file), str(scene_file))
            require_fields(scene, {"id", "kind", "pov", "outcome"}, str(scene_file))
    if resolution in {"novella", "novel"}:
        required_long_form_files = (
            story / "outline" / "movements.md",
            story / "outline" / "open-loops.json",
            story / "summaries" / "current.md",
        )
        for path in required_long_form_files:
            if not path.is_file() or not path.read_text(encoding="utf-8").strip():
                raise ValueError(
                    f"{resolution} working set requires {path.relative_to(story)}"
                )
        loop_ledger = require_mapping(
            load_json(story / "outline" / "open-loops.json"),
            "outline/open-loops.json",
        )
        require_fields(loop_ledger, {"open_loops"}, "outline/open-loops.json")
        loops = loop_ledger["open_loops"]
        if not isinstance(loops, list):
            raise ValueError("outline/open-loops.json open_loops must be an array")
        loop_ids: set[str] = set()
        for index, raw_loop in enumerate(loops):
            loop = require_mapping(raw_loop, f"open loop {index}")
            require_fields(loop, {"id", "status", "origin", "promise"}, f"open loop {index}")
            loop_id = loop["id"]
            if not isinstance(loop_id, str) or not loop_id:
                raise ValueError(f"open loop {index} has invalid ID")
            if loop_id in loop_ids:
                raise ValueError(f"duplicate open-loop ID: {loop_id}")
            loop_ids.add(loop_id)
        required_payoffs = contract["required_payoffs"]
        if not isinstance(required_payoffs, list) or not all(
            isinstance(payoff, str) and payoff for payoff in required_payoffs
        ):
            raise ValueError("required_payoffs must be an array of non-empty strings")
        for payoff in required_payoffs:
            if payoff not in loop_ids:
                raise ValueError(f"required payoff missing from open-loop ledger: {payoff}")

    validate_released_snapshots(story)
    validate_release_parent_cycles(story)
    parent_release_id = contract["parent_release_id"]
    if parent_release_id is not None:
        if not isinstance(parent_release_id, str) or not parent_release_id:
            raise ValueError("parent_release_id must be null or a non-empty string")
        if not RELEASE_ID_RE.fullmatch(parent_release_id):
            raise ValueError(f"unsafe parent_release_id: {parent_release_id}")
        if parent_release_id == contract["release_id"]:
            raise ValueError("working release cannot parent itself")
        parent = story / "release-contracts" / parent_release_id
        if not parent.is_dir() or parent.is_symlink():
            raise ValueError(f"parent release does not exist: {parent_release_id}")
    validate_working_retcons(story, canon, parent_release_id)
    validate_manuscript(story, budget, contract)
    if working_is_at_rest(story, contract):
        validate_working_matches_release(story, contract)
    else:
        validate_working_provenance(story, canon)
    return str(project["story_id"])


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("story", type=Path, help="Path to a story directory")
    args = parser.parse_args(argv)
    try:
        story_id = validate_story(args.story.resolve())
    except ValueError as exc:
        print(f"invalid: {exc}", file=sys.stderr)
        return 1
    print(f"valid: {story_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
