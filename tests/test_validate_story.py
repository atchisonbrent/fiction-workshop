import json
import hashlib
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = REPO_ROOT / ".agents" / "skills" / "story-development" / "scripts" / "validate_story.py"


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_story_license(story: Path) -> None:
    story.mkdir(parents=True, exist_ok=True)
    (story / "LICENSE.md").write_text(
        "# Fixture copyright notice\n\nCopyright (c) 2026 Test Author. All rights reserved.\n",
        encoding="utf-8",
    )


def make_valid_flash(story: Path, release_id: str, parent_release_id: str | None = None) -> None:
    write_json(
        story / "project.json",
        {
            "schema_version": 1,
            "story_id": story.name,
            "title": "Fixture",
            "active_release_id": release_id,
            "current_scope_budget": {
                "planning_resolution": "flash",
                "publication_shape": "standalone",
                "target_mode": "bounded",
                "reader_promise": "A complete turn.",
                "closure_posture": "closed",
                "revisit_policy": "expandable",
            },
            "complexity": {
                "pov_count": 1,
                "subplot_count": 0,
                "timeline_nonlinear": False,
                "world_rule_density": "low",
            },
        },
    )
    write_story_license(story)
    (story / "kernel.md").write_text("# Kernel\n\nA complete turn.\n", encoding="utf-8")
    write_json(
        story / "working" / "release-contract.json",
        {
            "release_id": release_id,
            "status": "working",
            "parent_release_id": parent_release_id,
            "reader_promise": "A complete turn.",
            "required_payoffs": ["turn"],
        },
    )
    write_json(story / "working" / "canon.json", {"lineage": "main", "facts": []})
    (story / "outline").mkdir(parents=True)
    (story / "outline" / "beats.md").write_text("# Beats\n\n- turn\n", encoding="utf-8")


def make_released_snapshot(story: Path, release_id: str, frozen_scope_budget: dict) -> Path:
    released = story / "release-contracts" / release_id
    write_json(
        released / "contract.json",
        {
            "release_id": release_id,
            "status": "released",
            "parent_release_id": None,
            "reader_promise": "A complete turn.",
            "required_payoffs": ["turn"],
            "frozen_scope_budget": frozen_scope_budget,
        },
    )
    (released / "kernel.md").write_text("# Kernel\n\nFrozen.\n", encoding="utf-8")
    (released / "approved-draft.md").write_text("A complete turn.\n", encoding="utf-8")
    write_json(released / "canon.json", {"lineage": "main", "facts": []})
    files = {
        name: sha256(released / name)
        for name in ("contract.json", "kernel.md", "approved-draft.md", "canon.json")
    }
    write_json(
        released / "manifest.json",
        {"schema_version": 1, "release_id": release_id, "files": files},
    )
    return released


def rehash_released_snapshot(released: Path) -> None:
    manifest = json.loads((released / "manifest.json").read_text(encoding="utf-8"))
    manifest["files"] = {
        name: sha256(released / name)
        for name in ("contract.json", "kernel.md", "approved-draft.md", "canon.json")
    }
    write_json(released / "manifest.json", manifest)


def make_valid_novella(story: Path, required_payoffs: list[str]) -> None:
    make_valid_flash(story, "novella-v1")
    project = json.loads((story / "project.json").read_text(encoding="utf-8"))
    project["current_scope_budget"]["planning_resolution"] = "novella"
    write_json(story / "project.json", project)
    contract = json.loads(
        (story / "working" / "release-contract.json").read_text(encoding="utf-8")
    )
    contract["required_payoffs"] = required_payoffs
    write_json(story / "working" / "release-contract.json", contract)
    (story / "outline" / "movements.md").write_text("# Movements\n\nI. Consequence.\n", encoding="utf-8")
    write_json(
        story / "outline" / "open-loops.json",
        {
            "open_loops": [
                {
                    "id": "known-payoff",
                    "status": "open",
                    "origin": "movement-1",
                    "promise": "Resolve the known payoff.",
                }
            ]
        },
    )
    (story / "summaries").mkdir(parents=True)
    (story / "summaries" / "current.md").write_text("# Summary\n\nCurrent.\n", encoding="utf-8")


class ValidateStoryTests(unittest.TestCase):
    def run_validator(self, story: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(VALIDATOR), str(story)],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_minimal_flash_working_set_validates_without_long_form_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            story = Path(tmp) / "small-mercy"
            write_json(
                story / "project.json",
                {
                    "schema_version": 1,
                    "story_id": "small-mercy",
                    "title": "Small Mercy",
                    "active_release_id": "flash-v1",
                    "current_scope_budget": {
                        "planning_resolution": "flash",
                        "publication_shape": "standalone",
                        "target_mode": "bounded",
                        "target_words": {"min": 800, "preferred": 1200, "max": 1800},
                        "reader_promise": "A complete choice with an irreversible cost.",
                        "closure_posture": "closed",
                        "revisit_policy": "expandable",
                    },
                    "complexity": {
                        "pov_count": 1,
                        "subplot_count": 0,
                        "timeline_nonlinear": False,
                        "world_rule_density": "low",
                    },
                },
            )
            (story / "kernel.md").parent.mkdir(parents=True, exist_ok=True)
            write_story_license(story)
            (story / "kernel.md").write_text(
                "# Kernel\n\nPremise, focal want, story question, and constraint.\n",
                encoding="utf-8",
            )
            write_json(
                story / "working" / "release-contract.json",
                {
                    "release_id": "flash-v1",
                    "status": "working",
                    "parent_release_id": None,
                    "reader_promise": "A complete choice with an irreversible cost.",
                    "required_payoffs": ["choice-made"],
                },
            )
            write_json(
                story / "working" / "canon.json",
                {
                    "lineage": "main",
                    "facts": [
                        {
                            "id": "station-is-isolated",
                            "status": "established",
                            "statement": "The station is isolated.",
                            "provenance": "beat-01",
                        }
                    ],
                },
            )
            (story / "outline").mkdir(parents=True)
            (story / "outline" / "beats.md").write_text(
                "# Beats\n\n- beat-01: The choice arrives.\n- choice-made: It is made.\n",
                encoding="utf-8",
            )

            result = self.run_validator(story)

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("valid: small-mercy", result.stdout)

    def test_story_requires_a_nonempty_license_marker(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            story = Path(tmp) / "missing-license"
            make_valid_flash(story, "flash-v1")
            (story / "LICENSE.md").unlink()

            result = self.run_validator(story)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("LICENSE.md must exist", result.stderr)

    def test_story_license_marker_must_name_copyright_and_terms(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            story = Path(tmp) / "thin-license"
            make_valid_flash(story, "flash-v1")
            (story / "LICENSE.md").write_text("x\n", encoding="utf-8")

            result = self.run_validator(story)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("LICENSE.md must include a copyright notice", result.stderr)

            (story / "LICENSE.md").write_text(
                "Copyright (c) 2026 Test Author.\n",
                encoding="utf-8",
            )
            result = self.run_validator(story)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("LICENSE.md must state the story's license terms", result.stderr)

    def test_novella_requires_long_form_operating_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            story = Path(tmp) / "small-mercy"
            write_json(
                story / "project.json",
                {
                    "schema_version": 1,
                    "story_id": "small-mercy",
                    "title": "Small Mercy",
                    "active_release_id": "novella-v1",
                    "current_scope_budget": {
                        "planning_resolution": "novella",
                        "publication_shape": "standalone",
                        "target_mode": "exploratory",
                        "reader_promise": "The choice reshapes the station.",
                        "closure_posture": "closed",
                        "revisit_policy": "expandable",
                    },
                    "complexity": {
                        "pov_count": 2,
                        "subplot_count": 1,
                        "timeline_nonlinear": False,
                        "world_rule_density": "medium",
                    },
                },
            )
            write_story_license(story)
            (story / "kernel.md").write_text("# Kernel\n\nA larger pressure.\n", encoding="utf-8")
            write_json(
                story / "working" / "release-contract.json",
                {
                    "release_id": "novella-v1",
                    "status": "working",
                    "parent_release_id": "short-v1",
                    "reader_promise": "The choice reshapes the station.",
                    "required_payoffs": ["institutional-cost"],
                },
            )
            write_json(story / "working" / "canon.json", {"lineage": "main", "facts": []})

            result = self.run_validator(story)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("outline/movements.md", result.stderr)

    def test_tampered_released_snapshot_fails_manifest_validation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            story = Path(tmp) / "small-mercy"
            write_json(
                story / "project.json",
                {
                    "schema_version": 1,
                    "story_id": "small-mercy",
                    "title": "Small Mercy",
                    "active_release_id": "flash-v2",
                    "current_scope_budget": {
                        "planning_resolution": "flash",
                        "publication_shape": "standalone",
                        "target_mode": "bounded",
                        "reader_promise": "A second complete choice.",
                        "closure_posture": "closed",
                        "revisit_policy": "expandable",
                    },
                    "complexity": {
                        "pov_count": 1,
                        "subplot_count": 0,
                        "timeline_nonlinear": False,
                        "world_rule_density": "low",
                    },
                },
            )
            write_story_license(story)
            (story / "kernel.md").write_text("# Kernel\n\nWorking revision.\n", encoding="utf-8")
            write_json(
                story / "working" / "release-contract.json",
                {
                    "release_id": "flash-v2",
                    "status": "working",
                    "parent_release_id": "flash-v1",
                    "reader_promise": "A second complete choice.",
                    "required_payoffs": ["choice-two"],
                },
            )
            write_json(story / "working" / "canon.json", {"lineage": "main", "facts": []})
            (story / "outline").mkdir(parents=True)
            (story / "outline" / "beats.md").write_text("# Beats\n\n- choice-two\n", encoding="utf-8")

            released = story / "release-contracts" / "flash-v1"
            write_json(
                released / "contract.json",
                {
                    "release_id": "flash-v1",
                    "status": "released",
                    "parent_release_id": None,
                    "reader_promise": "A complete choice.",
                    "required_payoffs": ["choice-one"],
                    "frozen_scope_budget": {
                        "planning_resolution": "flash",
                        "publication_shape": "standalone",
                    },
                },
            )
            (released / "kernel.md").write_text("# Kernel\n\nFrozen.\n", encoding="utf-8")
            (released / "approved-draft.md").write_text("The original ending.\n", encoding="utf-8")
            write_json(released / "canon.json", {"lineage": "main", "facts": []})
            files = {
                name: sha256(released / name)
                for name in ("contract.json", "kernel.md", "approved-draft.md", "canon.json")
            }
            write_json(released / "manifest.json", {"schema_version": 1, "release_id": "flash-v1", "files": files})
            (released / "approved-draft.md").write_text("A quietly altered ending.\n", encoding="utf-8")

            result = self.run_validator(story)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("hash mismatch", result.stderr)
            self.assertIn("flash-v1/approved-draft.md", result.stderr)

    def test_working_parent_release_must_exist(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            story = Path(tmp) / "orphaned-child"
            make_valid_flash(story, "flash-v2", parent_release_id="flash-v1")

            result = self.run_validator(story)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("parent release does not exist: flash-v1", result.stderr)

    def test_fact_ids_are_unique_within_a_lineage(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            story = Path(tmp) / "duplicate-facts"
            make_valid_flash(story, "flash-v1")
            write_json(
                story / "working" / "canon.json",
                {
                    "lineage": "main",
                    "facts": [
                        {
                            "id": "door-is-locked",
                            "status": "established",
                            "statement": "The door is locked.",
                            "provenance": "beat-01",
                        },
                        {
                            "id": "door-is-locked",
                            "status": "character_belief",
                            "statement": "Mara believes the door is locked.",
                            "provenance": "beat-02",
                        },
                    ],
                },
            )

            result = self.run_validator(story)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("duplicate fact ID in lineage main: door-is-locked", result.stderr)

    def test_short_may_use_scene_cards_instead_of_beats(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            story = Path(tmp) / "scene-short"
            make_valid_flash(story, "short-v1")
            project = json.loads((story / "project.json").read_text(encoding="utf-8"))
            project["current_scope_budget"]["planning_resolution"] = "short"
            write_json(story / "project.json", project)
            (story / "outline" / "beats.md").unlink()
            write_json(
                story / "outline" / "scenes" / "scene-01.json",
                {
                    "id": "scene-01",
                    "kind": "scene",
                    "pov": "mara",
                    "outcome": "Mara opens the door.",
                },
            )

            result = self.run_validator(story)

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_frozen_scope_budget_requires_the_full_budget_schema(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            story = Path(tmp) / "thin-frozen-budget"
            make_valid_flash(story, "flash-v2", parent_release_id="flash-v1")
            make_released_snapshot(
                story,
                "flash-v1",
                {
                    "planning_resolution": "flash",
                    "publication_shape": "standalone",
                },
            )

            result = self.run_validator(story)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("frozen_scope_budget missing fields", result.stderr)

    def test_working_release_cannot_parent_itself(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            story = Path(tmp) / "self-parent"
            make_valid_flash(story, "flash-v1", parent_release_id="flash-v1")
            make_released_snapshot(
                story,
                "flash-v1",
                {
                    "planning_resolution": "flash",
                    "publication_shape": "standalone",
                    "target_mode": "bounded",
                    "reader_promise": "A complete turn.",
                    "closure_posture": "closed",
                    "revisit_policy": "expandable",
                },
            )

            result = self.run_validator(story)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("working release cannot parent itself", result.stderr)

    def test_release_directory_cannot_be_a_symlink(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            story = root / "symlinked-release"
            make_valid_flash(story, "flash-v2", parent_release_id="flash-v1")
            external_story = root / "external"
            external_release = make_released_snapshot(
                external_story,
                "flash-v1",
                {
                    "planning_resolution": "flash",
                    "publication_shape": "standalone",
                    "target_mode": "bounded",
                    "reader_promise": "A complete turn.",
                    "closure_posture": "closed",
                    "revisit_policy": "expandable",
                },
            )
            releases = story / "release-contracts"
            releases.mkdir(parents=True)
            try:
                (releases / "flash-v1").symlink_to(external_release, target_is_directory=True)
            except OSError as exc:
                self.skipTest(f"filesystem does not permit symlink creation: {exc}")

            result = self.run_validator(story)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("release directory cannot be a symlink: flash-v1", result.stderr)

    def test_novella_required_payoffs_must_exist_in_open_loop_ledger(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            story = Path(tmp) / "missing-payoff"
            make_valid_novella(story, ["known-payoff", "missing-payoff"])

            result = self.run_validator(story)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("required payoff missing from open-loop ledger: missing-payoff", result.stderr)

    def test_retcon_must_supersede_an_ancestor_fact(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            story = Path(tmp) / "orphaned-retcon"
            make_valid_flash(story, "flash-v2", parent_release_id="flash-v1")
            make_released_snapshot(
                story,
                "flash-v1",
                {
                    "planning_resolution": "flash",
                    "publication_shape": "standalone",
                    "target_mode": "bounded",
                    "reader_promise": "A complete turn.",
                    "closure_posture": "closed",
                    "revisit_policy": "expandable",
                },
            )
            write_json(
                story / "working" / "canon.json",
                {
                    "lineage": "main",
                    "facts": [
                        {
                            "id": "changed-door",
                            "status": "retconned",
                            "statement": "The door was never locked.",
                            "provenance": "scene-02",
                            "supersedes": "missing-parent-fact",
                            "decision_ref": "decisions/001-retcon.md",
                        }
                    ],
                },
            )
            (story / "decisions").mkdir(parents=True)
            (story / "decisions" / "001-retcon.md").write_text(
                "# Retcon\n\nReason and consequences.\n", encoding="utf-8"
            )

            result = self.run_validator(story)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("retcon supersedes no ancestor fact: missing-parent-fact", result.stderr)

    def test_shipped_short_to_novella_fixture_validates(self) -> None:
        story = REPO_ROOT / "examples" / "small-mercy"
        released = story / "release-contracts" / "short-v1"
        manifest = json.loads((released / "manifest.json").read_text(encoding="utf-8"))
        before = {name: sha256(released / name) for name in manifest["files"]}

        result = self.run_validator(story)

        after = {name: sha256(released / name) for name in manifest["files"]}
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(before, manifest["files"])
        self.assertEqual(after, manifest["files"])
        parent_canon = json.loads((released / "canon.json").read_text(encoding="utf-8"))
        child_canon = json.loads((story / "working" / "canon.json").read_text(encoding="utf-8"))
        parent_ids = {fact["id"] for fact in parent_canon["facts"]}
        child_ids = {fact["id"] for fact in child_canon["facts"]}
        self.assertIn("nera-granted-twelve-minutes", parent_ids & child_ids)

    def test_complexity_signals_have_required_types(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            story = Path(tmp) / "bad-complexity"
            make_valid_flash(story, "flash-v1")
            project = json.loads((story / "project.json").read_text(encoding="utf-8"))
            del project["complexity"]["pov_count"]
            write_json(story / "project.json", project)

            result = self.run_validator(story)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("complexity missing fields: pov_count", result.stderr)

    def test_released_parent_cycle_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            story = Path(tmp) / "cycle"
            make_valid_flash(story, "working-v1")
            budget = {
                "planning_resolution": "flash",
                "publication_shape": "standalone",
                "target_mode": "bounded",
                "reader_promise": "A complete turn.",
                "closure_posture": "closed",
                "revisit_policy": "expandable",
            }
            release_a = make_released_snapshot(story, "release-a", budget)
            release_b = make_released_snapshot(story, "release-b", budget)
            contract_a = json.loads((release_a / "contract.json").read_text(encoding="utf-8"))
            contract_b = json.loads((release_b / "contract.json").read_text(encoding="utf-8"))
            contract_a["parent_release_id"] = "release-b"
            contract_b["parent_release_id"] = "release-a"
            write_json(release_a / "contract.json", contract_a)
            write_json(release_b / "contract.json", contract_b)
            rehash_released_snapshot(release_a)
            rehash_released_snapshot(release_b)

            result = self.run_validator(story)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("release parent cycle detected", result.stderr)

    def test_complete_manuscript_below_minimum_word_count_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            story = Path(tmp) / "short-complete"
            make_valid_novella(story, ["known-payoff"])
            project = json.loads((story / "project.json").read_text(encoding="utf-8"))
            project["current_scope_budget"]["target_words"] = {
                "min": 1000,
                "preferred": 1200,
                "max": 1500,
            }
            write_json(story / "project.json", project)
            contract = json.loads(
                (story / "working" / "release-contract.json").read_text(encoding="utf-8")
            )
            contract["manuscript_status"] = "complete"
            write_json(story / "working" / "release-contract.json", contract)
            (story / "working" / "manuscript.md").write_text(
                "# Tiny\n\nThis manuscript is much too short.\n", encoding="utf-8"
            )

            result = self.run_validator(story)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("complete manuscript word count", result.stderr)
            self.assertIn("below minimum 1000", result.stderr)

    def test_released_approved_draft_must_meet_frozen_word_budget(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            story = Path(tmp) / "short-release"
            make_valid_flash(story, "flash-v2", parent_release_id="flash-v1")
            make_released_snapshot(
                story,
                "flash-v1",
                {
                    "planning_resolution": "flash",
                    "publication_shape": "standalone",
                    "target_mode": "bounded",
                    "target_words": {"min": 1000, "preferred": 1200, "max": 1500},
                    "reader_promise": "A complete turn.",
                    "closure_posture": "closed",
                    "revisit_policy": "expandable",
                },
            )

            result = self.run_validator(story)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("released approved draft word count", result.stderr)
            self.assertIn("below minimum 1000", result.stderr)

    def test_working_parent_release_id_cannot_escape_release_tree(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            story = Path(tmp) / "escape"
            make_valid_flash(story, "flash-v2", parent_release_id="../foreign")
            (story / "foreign").mkdir(parents=True)

            result = self.run_validator(story)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("unsafe parent_release_id: ../foreign", result.stderr)

    def test_working_set_at_rest_on_released_id_must_match_the_release(self) -> None:
        """Editing kernel/canon/prose while still pointed at a released ID is drift."""
        budget = {
            "planning_resolution": "flash",
            "publication_shape": "standalone",
            "target_mode": "bounded",
            "reader_promise": "A complete turn.",
            "closure_posture": "closed",
            "revisit_policy": "expandable",
        }
        with tempfile.TemporaryDirectory() as tmp:
            story = Path(tmp) / "at-rest"
            make_valid_flash(story, "flash-v1")
            released = make_released_snapshot(story, "flash-v1", budget)
            # Bring the working set to rest: identical kernel, canon, and prose.
            (story / "kernel.md").write_bytes((released / "kernel.md").read_bytes())
            (story / "working" / "canon.json").write_bytes((released / "canon.json").read_bytes())
            (story / "working" / "manuscript.md").write_bytes(
                (released / "approved-draft.md").read_bytes()
            )
            result = self.run_validator(story)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

            (story / "working" / "manuscript.md").write_text("Edited after release.\n", encoding="utf-8")
            result = self.run_validator(story)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("working prose differs from released flash-v1", result.stderr)

            (story / "working" / "manuscript.md").write_bytes(
                (released / "approved-draft.md").read_bytes()
            )
            (story / "kernel.md").write_text("# Kernel\n\nQuietly changed.\n", encoding="utf-8")
            result = self.run_validator(story)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("kernel.md differs from released flash-v1", result.stderr)

            # Opening a child working release lifts the at-rest constraint.
            contract = json.loads(
                (story / "working" / "release-contract.json").read_text(encoding="utf-8")
            )
            contract["release_id"] = "flash-v2"
            contract["parent_release_id"] = "flash-v1"
            write_json(story / "working" / "release-contract.json", contract)
            project = json.loads((story / "project.json").read_text(encoding="utf-8"))
            project["active_release_id"] = "flash-v2"
            write_json(story / "project.json", project)
            result = self.run_validator(story)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_stale_manuscript_aggregate_fails_when_chapters_exist(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            story = Path(tmp) / "chapters"
            make_valid_flash(story, "flash-v1")
            chapters = story / "working" / "chapters"
            chapters.mkdir(parents=True)
            (chapters / "01-one.md").write_text("# One\n\nFirst.\n", encoding="utf-8")
            (chapters / "02-two.md").write_text("# Two\n\nSecond.\n", encoding="utf-8")
            (story / "working" / "manuscript.md").write_text(
                "# One\n\nFirst.\n\n---\n\n# Two\n\nSecond.\n", encoding="utf-8"
            )
            result = self.run_validator(story)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

            (chapters / "02-two.md").write_text("# Two\n\nSecond, revised.\n", encoding="utf-8")
            result = self.run_validator(story)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("working/manuscript.md is stale", result.stderr)

    def test_chaptered_working_provenance_must_resolve(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            story = Path(tmp) / "provenance"
            make_valid_flash(story, "flash-v1")
            chapters = story / "working" / "chapters"
            chapters.mkdir(parents=True)
            (chapters / "01-arrival.md").write_text(
                "# Story\n\n## Chapter One: The Cold Desk\n\nProse.\n", encoding="utf-8"
            )
            write_json(
                story / "outline" / "scenes" / "arrival.json",
                {"id": "cold-desk", "kind": "scene", "pov": "a", "outcome": "b"},
            )
            canon = {
                "lineage": "main",
                "facts": [
                    {"id": "a", "status": "established", "statement": "A.", "provenance": "kernel"},
                    {"id": "b", "status": "established", "statement": "B.", "provenance": "01-arrival"},
                    {
                        "id": "c",
                        "status": "character_belief",
                        "statement": "C.",
                        "provenance": "cold-desk",
                    },
                    {"id": "d", "status": "proposed", "statement": "D."},
                ],
            }
            write_json(story / "working" / "canon.json", canon)
            result = self.run_validator(story)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

            canon["facts"][1]["provenance"] = "first-contact"
            write_json(story / "working" / "canon.json", canon)
            result = self.run_validator(story)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("fact b provenance does not resolve", result.stderr)

            # Unchaptered short work keeps free-form provenance.
            shutil.rmtree(chapters)
            result = self.run_validator(story)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_chaptered_child_preserves_inherited_free_form_provenance(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            story = Path(tmp) / "child-provenance"
            make_valid_flash(story, "flash-v2", parent_release_id="flash-v1")
            budget = json.loads((story / "project.json").read_text())["current_scope_budget"]
            parent = make_released_snapshot(story, "flash-v1", budget)
            parent_canon = {
                "lineage": "main",
                "facts": [
                    {
                        "id": "inherited",
                        "status": "established",
                        "statement": "This came from the short.",
                        "provenance": "short-v1:opening",
                    }
                ],
            }
            write_json(parent / "canon.json", parent_canon)
            rehash_released_snapshot(parent)
            chapters = story / "working" / "chapters"
            chapters.mkdir(parents=True)
            (chapters / "01-child.md").write_text("# Child\n\nNew prose.\n", encoding="utf-8")
            child_canon = {
                "lineage": "main",
                "facts": parent_canon["facts"]
                + [
                    {
                        "id": "new",
                        "status": "established",
                        "statement": "This came from the child.",
                        "provenance": "01-child",
                    }
                ],
            }
            write_json(story / "working" / "canon.json", child_canon)
            result = self.run_validator(story)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

            # A changed inherited record is no longer exempt and must resolve.
            child_canon["facts"][0]["statement"] = "Silently changed."
            write_json(story / "working" / "canon.json", child_canon)
            result = self.run_validator(story)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("fact inherited provenance does not resolve", result.stderr)

    def test_at_rest_guard_covers_canon_contract_and_chaptered_prose(self) -> None:
        budget = {
            "planning_resolution": "flash",
            "publication_shape": "standalone",
            "target_mode": "bounded",
            "reader_promise": "A complete turn.",
            "closure_posture": "closed",
            "revisit_policy": "expandable",
        }
        with tempfile.TemporaryDirectory() as tmp:
            story = Path(tmp) / "at-rest-more"
            make_valid_flash(story, "flash-v1")
            released = make_released_snapshot(story, "flash-v1", budget)
            (story / "kernel.md").write_bytes((released / "kernel.md").read_bytes())
            (story / "working" / "canon.json").write_bytes((released / "canon.json").read_bytes())
            prose = (released / "approved-draft.md").read_text(encoding="utf-8")
            (story / "working" / "manuscript.md").write_text(prose, encoding="utf-8")

            (story / "working" / "manuscript.md").unlink()
            result = self.run_validator(story)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("working prose is missing", result.stderr)
            (story / "working" / "manuscript.md").write_text(prose, encoding="utf-8")

            canon = json.loads((story / "working" / "canon.json").read_text())
            canon["facts"] = [
                {"id": "x", "status": "proposed", "statement": "Drift."}
            ]
            write_json(story / "working" / "canon.json", canon)
            result = self.run_validator(story)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("working/canon.json differs", result.stderr)

            (story / "working" / "canon.json").write_bytes((released / "canon.json").read_bytes())
            contract = json.loads(
                (story / "working" / "release-contract.json").read_text(encoding="utf-8")
            )
            contract["reader_promise"] = "Drifted promise."
            write_json(story / "working" / "release-contract.json", contract)
            result = self.run_validator(story)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("working/release-contract.json differs", result.stderr)

            contract["reader_promise"] = "A complete turn."
            write_json(story / "working" / "release-contract.json", contract)
            chapters = story / "working" / "chapters"
            chapters.mkdir()
            (chapters / "01-only.md").write_text(prose, encoding="utf-8")
            result = self.run_validator(story)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            (chapters / "02-extra.md").write_text("Extra.\n", encoding="utf-8")
            result = self.run_validator(story)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("working/manuscript.md is stale", result.stderr)

    def test_chapters_directory_and_kernel_cannot_be_symlinks(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            story = root / "links"
            make_valid_flash(story, "flash-v1")
            external = root / "external"
            external.mkdir()
            (story / "working" / "chapters").symlink_to(external, target_is_directory=True)
            result = self.run_validator(story)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("working/chapters must be a real directory", result.stderr)

            (story / "working" / "chapters").unlink()
            kernel_text = (story / "kernel.md").read_text(encoding="utf-8")
            (story / "kernel.md").unlink()
            external_kernel = root / "kernel.md"
            external_kernel.write_text(kernel_text, encoding="utf-8")
            (story / "kernel.md").symlink_to(external_kernel)
            result = self.run_validator(story)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("kernel.md must exist, be non-empty, and not be a symlink", result.stderr)

    def test_complete_targetless_exploratory_story_validates(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            story = Path(tmp) / "targetless"
            make_valid_flash(story, "flash-v1")
            contract = json.loads(
                (story / "working" / "release-contract.json").read_text(encoding="utf-8")
            )
            contract["manuscript_status"] = "complete"
            write_json(story / "working" / "release-contract.json", contract)
            (story / "working" / "manuscript.md").write_text("Complete at its natural length.\n")
            result = self.run_validator(story)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
