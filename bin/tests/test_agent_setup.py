"""Filesystem behavior of profile installation and policy rendering."""
import contextlib
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest


def module(name, filename):
    path = Path(__file__).resolve().parents[1] / filename
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


installer = module("installer", "install-agent-skills.py")
renderer = module("renderer", "render-agent-policy.py")


class InstallationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="rig-skills-test-")
        self.addCleanup(self.temp.cleanup)
        base = Path(self.temp.name)
        self.root, self.home, self.work = (base / p for p in ("rig", "home", "work"))
        self.put(self.root / "agent-policy/skills.json", json.dumps(
            {"shared": ["shared-tool"], "claude_only": [], "codex_only": ["codex-tool"]}))
        self.put(self.work / "agent-policy/skills.json", json.dumps(
            {"skills": ["work-tool"], "retire_global": ["work-tool", "old-prose"]}))
        for path in (self.root / "claude-shared/skills/shared-tool",
                     self.root / "codex/skills/codex-tool", self.work / "work-skills/work-tool"):
            self.put(path / "SKILL.md", "skill body\n")

    def put(self, path, content):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)

    def run_install(self, apply=True):
        with contextlib.redirect_stdout(io.StringIO()):
            return installer.execute(self.root, self.home, self.work, apply)

    def test_migration_preserves_content_and_is_idempotent(self):
        legacy = self.home / ".agents/skills/work-tool/SKILL.md"
        self.put(legacy, "local original\n")
        old_link = self.home / ".agents/skills/old-prose"
        old_link.symlink_to("/missing/plugin-cache")
        unrelated = self.home / ".agents/skills/user-tool/SKILL.md"
        self.put(unrelated, "untouched\n")
        displaced = self.home / ".claude/skills/work-tool/SKILL.md"
        self.put(displaced, "older profile body\n")
        self.assertGreater(self.run_install(False), 0)
        self.assertTrue(legacy.exists())
        self.assertFalse((self.home / ".local/state").exists())
        self.run_install()
        self.assertFalse(legacy.exists())
        self.assertFalse(old_link.is_symlink())
        saved = self.home / ".local/state/rig-skill-backups"
        self.assertEqual([p.read_text() for p in saved.glob("*/.agents/skills/work-tool/SKILL.md")],
                         ["local original\n"])
        self.assertEqual([p.read_text() for p in saved.glob("*/.claude/skills/work-tool/SKILL.md")],
                         ["older profile body\n"])
        self.assertTrue(next(saved.glob("*/.agents/skills/old-prose")).is_symlink())
        self.assertEqual(unrelated.read_text(), "untouched\n")
        self.assertFalse((self.home / ".codex-personal/skills/work-tool").exists())
        self.assertEqual((self.home / ".codex/skills/work-tool").resolve(),
                         (self.work / "work-skills/work-tool").resolve())
        self.assertEqual(self.run_install(), 0)

    def test_missing_source_fails_before_archiving(self):
        legacy = self.home / ".agents/skills/work-tool/SKILL.md"
        self.put(legacy, "must survive\n")
        (self.work / "work-skills/work-tool/SKILL.md").rename(self.work / "saved.md")
        with self.assertRaises(ValueError):
            self.run_install()
        self.assertEqual(legacy.read_text(), "must survive\n")

    def test_retired_openrouter_profile_is_not_created(self):
        self.run_install()
        self.assertFalse((self.home / ".claude-openrouter").exists())

    def test_directory_symlinks_do_not_mutate_source(self):
        profile = self.home / ".claude-personal/skills"
        profile.parent.mkdir(parents=True)
        profile.symlink_to(self.root / "claude-shared/skills")
        self.run_install()
        self.assertFalse((self.root / "claude-shared/skills/shared-tool").is_symlink())
        self.assertEqual(self.run_install(), 0)

    def test_policy_changes_propagate_to_both_hosts_and_scopes(self):
        for path, content in (("agent-policy/common.md", "shared rule"),
                              ("agent-policy/personal.md", "personal paths"),
                              ("agent-policy/claude.md", "claude adapter"),
                              ("agent-policy/codex.md", "codex adapter"),
                              ("claude-shared/prose-rules.md", "prose rule")):
            self.put(self.root / path, content)
        self.put(self.work / "agent-policy/work.md", "work paths")
        generated = dict(renderer.outputs(self.root, self.work))
        self.assertEqual(len(generated), 4)
        self.put(self.root / "agent-policy/common.md", "updated shared rule")
        updated = dict(renderer.outputs(self.root, self.work))
        for path, content in updated.items():
            self.assertNotEqual(content, generated[path])
            self.assertIn("updated shared rule", content)
            self.assertIn("prose rule", content)
            self.assertEqual("work paths" in content, self.work in path.parents)


if __name__ == "__main__":
    unittest.main()
