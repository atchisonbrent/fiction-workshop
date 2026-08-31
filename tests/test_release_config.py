import json
import re
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
CONFIG = REPO_ROOT / "release-please-config.json"
MANIFEST = REPO_ROOT / ".release-please-manifest.json"
VERSION = REPO_ROOT / "version.txt"
CHANGELOG = REPO_ROOT / "CHANGELOG.md"
WORKFLOW = REPO_ROOT / ".github" / "workflows" / "release-please.yml"
SKILL = REPO_ROOT / ".hermes" / "skills" / "story-development" / "SKILL.md"


class ReleaseConfigurationTests(unittest.TestCase):
    def test_release_please_configuration_is_single_root_simple_release(self) -> None:
        config = json.loads(CONFIG.read_text(encoding="utf-8"))
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))

        package = config["packages"]["."]
        self.assertEqual(package["release-type"], "simple")
        self.assertTrue(package["include-v-in-tag"])
        self.assertEqual(package["package-name"], "fiction-workshop")
        self.assertEqual(
            package["extra-files"],
            [
                {
                    "type": "generic",
                    "path": ".hermes/skills/story-development/SKILL.md",
                }
            ],
        )
        self.assertEqual(set(manifest), {"."})
        self.assertRegex(manifest["."], r"^\d+\.\d+\.\d+$")

    def test_unreleased_versions_are_synchronized(self) -> None:
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        current_version = manifest["."]
        self.assertEqual(VERSION.read_text(encoding="utf-8").strip(), current_version)
        skill = SKILL.read_text(encoding="utf-8")
        match = re.search(
            r"^version:\s*([^\s#]+)\s+#\s*x-release-please-version\s*$",
            skill,
            re.MULTILINE,
        )
        self.assertIsNotNone(match)
        assert match is not None
        self.assertEqual(match.group(1), current_version)
        changelog = CHANGELOG.read_text(encoding="utf-8")
        if current_version == "0.0.0":
            self.assertEqual(changelog, "")
        else:
            self.assertEqual(changelog.count("# Changelog"), 1)

    def test_workflow_tests_before_pinned_release_action(self) -> None:
        workflow = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("python3 -m unittest discover -s tests -v", workflow)
        self.assertIn(
            "python3 .hermes/skills/story-development/scripts/validate_story.py examples/small-mercy",
            workflow,
        )
        release_action = (
            "googleapis/release-please-action@"
            "45996ed1f6d02564a971a2fa1b5860e934307cf7"
        )
        checkout_action = "actions/checkout@11d5960a326750d5838078e36cf38b85af677262"
        self.assertIn(release_action, workflow)
        self.assertIn(checkout_action, workflow)
        self.assertLess(workflow.index("python3 -m unittest"), workflow.index(release_action))
        self.assertIn("contents: write", workflow)
        self.assertIn("pull-requests: write", workflow)


if __name__ == "__main__":
    unittest.main()
