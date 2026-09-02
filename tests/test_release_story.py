import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = REPO_ROOT / ".agents" / "skills" / "story-development" / "scripts"
RELEASER = SCRIPTS / "release_story.py"
VALIDATOR = SCRIPTS / "validate_story.py"
EXAMPLE = REPO_ROOT / "examples" / "small-mercy"


def run(script: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(script), *args],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


class ReleaseStoryTests(unittest.TestCase):
    def rewind_example_to_short_working_set(self, story: Path) -> Path:
        """Reconstruct the working set that produced short-v1 and remove the release."""
        shutil.copytree(EXAMPLE, story)
        released = story / "release-contracts" / "short-v1"
        frozen = read_json(released / "contract.json")

        project = read_json(story / "project.json")
        project["active_release_id"] = "short-v1"
        project["current_scope_budget"] = frozen["frozen_scope_budget"]
        project["complexity"] = {
            "pov_count": 1,
            "subplot_count": 0,
            "timeline_nonlinear": False,
            "world_rule_density": "low",
        }
        write_json(story / "project.json", project)

        working = dict(frozen)
        working["status"] = "working"
        working["manuscript_status"] = "complete"
        del working["frozen_scope_budget"]
        write_json(story / "working" / "release-contract.json", working)

        (story / "kernel.md").write_bytes((released / "kernel.md").read_bytes())
        (story / "working" / "canon.json").write_bytes((released / "canon.json").read_bytes())
        (story / "working" / "manuscript.md").write_bytes(
            (released / "approved-draft.md").read_bytes()
        )
        (story / "outline" / "beats.md").write_text(
            "# Beats\n\n- purpose-of-heat-request\n- nera-choice\n- ship-departure\n",
            encoding="utf-8",
        )
        shutil.rmtree(released)
        return released

    def test_release_reproduces_shipped_example_snapshot_except_field_order(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            story = Path(tmp) / "small-mercy"
            released = self.rewind_example_to_short_working_set(story)

            result = run(RELEASER, str(story))
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("released: release-contracts/short-v1", result.stdout)

            for name in ("kernel.md", "approved-draft.md", "canon.json"):
                self.assertEqual(
                    (released / name).read_bytes(),
                    (EXAMPLE / "release-contracts" / "short-v1" / name).read_bytes(),
                    name,
                )
            # The contract must carry the same content; JSON key order is not canon.
            self.assertEqual(
                read_json(released / "contract.json"),
                {
                    **read_json(EXAMPLE / "release-contracts" / "short-v1" / "contract.json"),
                    "manuscript_status": "complete",
                },
            )
            manifest = read_json(released / "manifest.json")
            self.assertEqual(manifest["release_id"], "short-v1")
            self.assertEqual(
                set(manifest["files"]),
                {"contract.json", "kernel.md", "approved-draft.md", "canon.json"},
            )
            self.assertEqual(run(VALIDATOR, str(story)).returncode, 0)

    def test_release_refuses_to_overwrite_an_existing_release(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            story = Path(tmp) / "small-mercy"
            shutil.copytree(EXAMPLE, story)
            contract = read_json(story / "working" / "release-contract.json")
            contract["manuscript_status"] = "complete"
            write_json(story / "working" / "release-contract.json", contract)
            (story / "working" / "manuscript.md").write_text(
                " ".join(["word"] * 20000) + "\n", encoding="utf-8"
            )
            before = {
                path: path.read_bytes()
                for path in (story / "release-contracts").rglob("*")
                if path.is_file()
            }
            # Point the working set at the already-released ID.
            project = read_json(story / "project.json")
            project["active_release_id"] = "short-v1"
            write_json(story / "project.json", project)
            contract["release_id"] = "short-v1"
            contract["parent_release_id"] = None
            write_json(story / "working" / "release-contract.json", contract)

            result = run(RELEASER, str(story))
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("release failed:", result.stderr)
            after = {
                path: path.read_bytes()
                for path in (story / "release-contracts").rglob("*")
                if path.is_file()
            }
            self.assertEqual(before, after, "release tree must never be touched on failure")

    def test_release_requires_complete_manuscript_status_and_valid_story(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            story = Path(tmp) / "small-mercy"
            shutil.copytree(EXAMPLE, story)
            result = run(RELEASER, str(story))
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("manuscript_status 'complete'", result.stderr)
            self.assertFalse((story / "release-contracts" / "novella-v1").exists())

            (story / "LICENSE.md").unlink()
            result = run(RELEASER, str(story))
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("LICENSE.md", result.stderr)

    def test_dry_run_writes_nothing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            story = Path(tmp) / "small-mercy"
            self.rewind_example_to_short_working_set(story)
            result = run(RELEASER, "--dry-run", str(story))
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("would release short-v1", result.stdout)
            self.assertFalse((story / "release-contracts" / "short-v1").exists())

    def test_release_assembles_chapters_and_rejects_stale_aggregate(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            story = Path(tmp) / "small-mercy"
            released = self.rewind_example_to_short_working_set(story)
            text = (story / "working" / "manuscript.md").read_text(encoding="utf-8")
            head, tail = text.split("\n\n", 1)
            chapters = story / "working" / "chapters"
            chapters.mkdir()
            (chapters / "01-a.md").write_text(head + "\n", encoding="utf-8")
            (chapters / "02-b.md").write_text(tail, encoding="utf-8")
            expected = head + "\n\n---\n\n" + tail.rstrip("\n") + "\n"
            (story / "working" / "manuscript.md").write_text(expected, encoding="utf-8")
            # Chaptered prose requires provenance that resolves to it.
            canon = read_json(story / "working" / "canon.json")
            for fact in canon["facts"]:
                if "provenance" in fact:
                    fact["provenance"] = "02-b"
            write_json(story / "working" / "canon.json", canon)

            result = run(RELEASER, str(story))
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertEqual((released / "approved-draft.md").read_text(encoding="utf-8"), expected)

            shutil.rmtree(released)
            (chapters / "02-b.md").write_text(tail + "\nAdded late.\n", encoding="utf-8")
            result = run(RELEASER, str(story))
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("stale", result.stderr)
            self.assertFalse(released.exists())


if __name__ == "__main__":
    unittest.main()
