import json
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = REPO_ROOT / ".agents" / "skills" / "story-development"
EXPECTED_SUPPORT_FILES = {
    "references/editorial-rubrics.md",
    "references/genre-adapters.md",
    "references/influence-and-voice.md",
    "references/scope-and-expansion.md",
    "references/story-model.md",
    "scripts/release_story.py",
    "scripts/validate_story.py",
    "templates/canon.json",
    "templates/character.json",
    "templates/project.json",
    "templates/release-contract.json",
    "templates/scene.json",
}
INSTALL_TARGETS = {
    "codex": ".agents/skills/story-development",
    "claude-code": ".claude/skills/story-development",
    "opencode": ".agents/skills/story-development",
    "hermes-agent": ".hermes/skills/story-development",
}


class SkillPortabilityTests(unittest.TestCase):
    def test_vendor_neutral_skill_is_complete(self) -> None:
        self.assertTrue((SKILL_ROOT / "SKILL.md").is_file())
        actual = {
            path.relative_to(SKILL_ROOT).as_posix()
            for path in SKILL_ROOT.rglob("*")
            if path.is_file()
        }
        self.assertTrue(EXPECTED_SUPPORT_FILES <= actual)
        self.assertFalse((REPO_ROOT / ".hermes" / "skills" / "story-development").exists())

    def test_frontmatter_matches_agent_skills_contract(self) -> None:
        text = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.assertTrue(text.startswith("---\n"))
        frontmatter, body = text[4:].split("\n---\n", 1)
        name = re.search(r"^name:\s*(\S+)\s*$", frontmatter, re.MULTILINE)
        description = re.search(
            r"^description:\s*(.+?)\s*$", frontmatter, re.MULTILINE
        )
        self.assertIsNotNone(name)
        self.assertIsNotNone(description)
        assert name is not None and description is not None
        self.assertRegex(name.group(1), r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
        self.assertLessEqual(len(description.group(1)), 1024)
        self.assertTrue(body.strip())

    def test_skill_instructions_resolve_resources_from_skill_directory(self) -> None:
        skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("SKILL_DIR", skill)
        self.assertIn("<SKILL_DIR>/scripts/validate_story.py", skill)
        self.assertIn("<SKILL_DIR>/scripts/release_story.py", skill)
        self.assertNotIn(".hermes/skills/story-development", skill)
        self.assertNotIn("terminal(command=", skill)
        self.assertNotIn("Work from this repository", skill)

    def test_copied_skill_validator_runs_from_each_agent_location(self) -> None:
        example = REPO_ROOT / "examples" / "small-mercy"
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for agent, relative_target in INSTALL_TARGETS.items():
                target = root / agent / relative_target
                shutil.copytree(SKILL_ROOT, target)
                result = subprocess.run(
                    [
                        sys.executable,
                        str(target / "scripts" / "validate_story.py"),
                        str(example),
                    ],
                    text=True,
                    capture_output=True,
                    check=False,
                )
                self.assertEqual(
                    result.returncode,
                    0,
                    f"{agent}: {result.stdout}{result.stderr}",
                )
                self.assertIn("valid: small-mercy", result.stdout)

    def test_release_config_tracks_canonical_skill_version(self) -> None:
        config = json.loads(
            (REPO_ROOT / "release-please-config.json").read_text(encoding="utf-8")
        )
        self.assertEqual(
            config["packages"]["."]["extra-files"],
            [
                {
                    "type": "generic",
                    "path": ".agents/skills/story-development/SKILL.md",
                },
                {
                    "type": "generic",
                    "path": "README.md",
                },
            ],
        )


if __name__ == "__main__":
    unittest.main()
