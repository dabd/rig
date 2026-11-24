"""Exercise managed launch and update behavior using isolated installations."""

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[2]
RUNTIME = ROOT / "bin/agent-runtime.py"
PACKAGE_METADATA = ("CODEX_MANAGED_BY_NPM", "CODEX_MANAGED_BY_BUN", "CODEX_MANAGED_BY_PNPM",
                    "CODEX_MANAGED_BY_VITE_PLUS", "CODEX_MANAGED_PACKAGE_ROOT")


class RuntimeTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="rig-agent-runtime-test-")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name).resolve()
        self.home = self.root / "home"
        self.home.mkdir()
        (self.home / "rig").symlink_to(ROOT)
        self.cwd = self.root / "project"
        self.cwd.mkdir()
        self.binaries = self.root / "managed/bin"
        self.binaries.mkdir(parents=True)
        self.log = self.root / "calls.jsonl"
        self.env = dict(os.environ, HOME=str(self.home), PATH="/usr/bin:/bin", SPY_LOG=str(self.log),
                        CODEX_HOME="/inherited/codex", CLAUDE_CONFIG_DIR="/inherited/claude")
        self.env.update({key: "inherited" for key in PACKAGE_METADATA})
        self.config_dir = self.home / ".config/rig"
        self.config_dir.mkdir(parents=True)
        self.config = self.config_dir / "agent-installations.json"
        self.config.write_text(json.dumps({name: str(self.binaries / name)
                                           for name in ("brew", "codex", "claude")}))
        for name in ("brew", "codex", "claude"):
            self.spy(self.binaries / name)

    def spy(self, path, version="old"):
        path.write_text("#!{}\n".format(sys.executable) + '''
import json, os, pathlib, subprocess, sys
with open(os.environ["SPY_LOG"], "a") as output:
    output.write(json.dumps({"exe": sys.argv[0], "args": sys.argv[1:], "cwd": os.getcwd(),
                            "env": dict(os.environ), "version": VERSION}) + "\\n")
if os.environ.get("SPY_CHILD"):
    child_env = dict(os.environ)
    child_env.pop("SPY_CHILD")
    raise SystemExit(subprocess.run(["/bin/zsh", "-f", "-c", "command codex child; command claude child"],
                                   env=child_env).returncode)
if pathlib.Path(sys.argv[0]).name == "brew" and sys.argv[1:2] == ["upgrade"]:
    target = pathlib.Path(sys.argv[0]).with_name("codex")
    target.write_text(target.read_text().replace("VERSION = 'old'", "VERSION = 'new'"))
if pathlib.Path(sys.argv[0]).name == "brew" and sys.argv[1:] == ["--prefix"]:
    print(pathlib.Path(sys.argv[0]).parent.parent)
if pathlib.Path(sys.argv[0]).name == "claude" and sys.argv[1:] == ["update"] and os.environ.get("SPY_UPGRADE_TARGET"):
    command = pathlib.Path(sys.argv[0])
    command.unlink()
    command.symlink_to(os.environ["SPY_UPGRADE_TARGET"])
raise SystemExit(int(os.environ.get("SPY_EXIT", "0")))
'''.replace("import json, os, pathlib, subprocess, sys", "import json, os, pathlib, subprocess, sys\nVERSION = {!r}".format(version)))
        path.chmod(0o700)

    def run_runtime(self, *args, cwd=None, env=None):
        self.log.unlink(missing_ok=True)
        result = subprocess.run([sys.executable, str(RUNTIME), *args], cwd=cwd or self.cwd,
                                env=dict(self.env, **(env or {})), capture_output=True, text=True)
        calls = [json.loads(line) for line in self.log.read_text().splitlines()] if self.log.exists() else []
        return result, calls

    def policy(self, **values):
        (self.config_dir / "agent-policy.json").write_text(json.dumps(values))

    def test_profile_and_executable_are_independent_of_inherited_path(self):
        poison = self.root / "poison"
        poison.mkdir()
        for name in ("codex", "claude"):
            self.spy(poison / name)
        for agent in ("codex", "claude"):
            args = ["--", "literal; $(never)", "argument with spaces", ""]
            result, calls = self.run_runtime("launch", "--personal", agent, "--", *args,
                                            env={"PATH": str(poison)})
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(calls[0]["exe"], str(self.binaries / agent))
            self.assertEqual(calls[0]["args"], args)
            self.assertEqual(calls[0]["cwd"], str(self.cwd))
            observed = calls[0]["env"]
            self.assertEqual(observed["CODEX_HOME"], str(self.home / ".codex-personal"))
            self.assertEqual(observed["CLAUDE_CONFIG_DIR"], str(self.home / ".claude-personal"))
            self.assertEqual(observed["RIG_AGENT_PROFILE"], "personal")
            self.assertEqual(observed["CLAUDE_CODE_USE_BEDROCK"], "0")
            if agent == "codex":
                for key in PACKAGE_METADATA:
                    self.assertNotIn(key, observed)

    def test_nonpersonal_launch_preserves_callers_profile(self):
        result, calls = self.run_runtime("launch", "codex", "--", "test")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(calls[0]["env"]["CODEX_HOME"], "/inherited/codex")
        self.assertEqual(calls[0]["env"]["CLAUDE_CONFIG_DIR"], "/inherited/claude")
        for key in PACKAGE_METADATA:
            self.assertNotIn(key, calls[0]["env"])

    def test_exit_status_and_missing_binary_never_fall_back(self):
        result, _ = self.run_runtime("launch", "--personal", "codex", "--", "test", env={"SPY_EXIT": "23"})
        self.assertEqual(result.returncode, 23)
        (self.binaries / "codex").unlink()
        result, calls = self.run_runtime("launch", "--personal", "codex", "--", "test")
        self.assertEqual(result.returncode, 1)
        self.assertIn("Managed executable missing", result.stderr)
        self.assertEqual(calls, [])

    def test_policy_removes_provider_environment_and_preserves_tools_for_children(self):
        private = self.root / "restricted-tools"
        private.mkdir()
        self.policy(personal_unset_env=["EXAMPLE_PRIVATE_TOKEN"])
        result, calls = self.run_runtime("launch", "--personal", "codex", "--", "test",
                                        env={"EXAMPLE_PRIVATE_TOKEN": "fixture", "PATH": str(private) + ":/usr/bin:/bin",
                                             "SPY_CHILD": "1"})
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(len(calls), 3)
        for call in calls:
            self.assertNotIn("EXAMPLE_PRIVATE_TOKEN", call["env"])
            self.assertIn(str(private), call["env"]["PATH"])
            self.assertEqual(call["env"]["RIG_AGENT_PROFILE"], "personal")
            self.assertEqual(call["env"]["CODEX_HOME"], str(self.home / ".codex-personal"))
        self.assertEqual([call["exe"] for call in calls[1:]],
                         [str(self.binaries / agent) for agent in ("codex", "claude")])

    def test_directory_arguments_and_admin_commands_keep_normal_semantics(self):
        project = self.root / "another project"
        project.mkdir()
        link = self.root / "linked"
        link.symlink_to(project)
        for agent in ("codex", "claude"):
            cases = [(project, []), (link, []), (self.cwd, ["-C", str(link)]),
                     (self.cwd, ["-C" + str(link)]), (self.cwd, ["--cd=" + str(link)]),
                     (self.cwd, ["--add-dir", str(link)]),
                     (self.cwd, ["--add-dir=" + str(link)]),
                     (self.cwd, ["--add-dir", str(self.cwd), str(link)]),
                     (project, ["--help"]), (project, ["--version"]),
                     (project, ["update", "--help"]), (project, ["upgrade", "-h"]),
                     (project, ["mcp", "add", "example", "--scope", "project"])]
            for cwd, args in cases:
                with self.subTest(agent=agent, args=args, cwd=cwd):
                    result, calls = self.run_runtime("launch", "--personal", agent, "--", *args, cwd=cwd)
                    self.assertEqual(result.returncode, 0, result.stderr)
                    self.assertEqual(calls[0]["args"], args)
                    self.assertEqual(calls[0]["cwd"], str(cwd.resolve()))

    def test_headless_personal_launchers_pin_both_profiles(self):
        for name in ("codex-personal", "claude-personal"):
            self.log.unlink(missing_ok=True)
            result = subprocess.run([str(ROOT / "bin" / name), "test"], cwd=self.cwd,
                                    env=self.env, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            call = json.loads(self.log.read_text())
            self.assertEqual(call["env"]["CODEX_HOME"], str(self.home / ".codex-personal"))
            self.assertEqual(call["env"]["CLAUDE_CONFIG_DIR"], str(self.home / ".claude-personal"))

    @unittest.skipUnless(sys.platform == "darwin", "Homebrew casks require macOS")
    def test_codex_update_targets_owner_and_both_profiles_see_new_binary(self):
        result, calls = self.run_runtime("launch", "--personal", "codex", "--", "update")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(calls[2]["exe"], str(self.binaries / "brew"))
        self.assertEqual(calls[2]["args"], ["upgrade", "--cask", "codex"])
        self.assertEqual(calls[3]["version"], "new")
        for flags in ([], ["--personal"]):
            result, calls = self.run_runtime("launch", *flags, "codex", "--", "test")
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(calls[0]["version"], "new")

    def test_claude_updater_preserves_vendor_link_and_personal_settings(self):
        native = self.binaries / "native-version"
        (self.binaries / "claude").rename(native)
        (self.binaries / "claude").symlink_to(native)
        upgraded = self.binaries / "native-next"
        self.spy(upgraded, "new")
        settings = self.home / ".claude-personal/settings.json"
        settings.parent.mkdir()
        settings.write_text('{"theme": "dark", "autoUpdatesChannel": "stable"}')
        result, calls = self.run_runtime("update", "claude", env={"DISABLE_AUTOUPDATER": "1",
                                                                  "SPY_UPGRADE_TARGET": str(upgraded)})
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(calls[0]["exe"], str(self.binaries / "claude"))
        self.assertEqual(calls[0]["args"], ["update"])
        self.assertEqual(calls[0]["env"]["CLAUDE_CONFIG_DIR"], str(settings.parent))
        self.assertNotIn("DISABLE_AUTOUPDATER", calls[0]["env"])
        self.assertEqual(json.loads(settings.read_text()), {"theme": "dark", "autoUpdatesChannel": "latest"})
        self.assertTrue((self.binaries / "claude").is_symlink())
        self.assertEqual((self.binaries / "claude").resolve(), upgraded)
        self.assertTrue(native.exists())
        self.assertEqual(calls[1]["version"], "new")
        for flags in ([], ["--personal"]):
            result, calls = self.run_runtime("launch", *flags, "claude", "--", "test")
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(calls[0]["version"], "new")

    def test_check_requires_no_private_policy(self):
        result, calls = self.run_runtime("check")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual([call["args"] for call in calls[-2:]], [["--version"], ["--version"]])

    def test_check_reports_disabled_claude_updates(self):
        result, calls = self.run_runtime("check", env={"DISABLE_AUTOUPDATER": "1"})
        self.assertEqual(result.returncode, 1)
        self.assertIn("Claude automatic updates: disabled by DISABLE_AUTOUPDATER", result.stderr)
        self.assertEqual([call["args"] for call in calls[-2:]], [["--version"], ["--version"]])

    def test_check_detects_local_settings_that_disable_updates(self):
        settings = self.home / ".claude-personal/settings.json"
        settings.parent.mkdir()
        for key in ("DISABLE_AUTOUPDATER", "DISABLE_UPDATES", "CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC"):
            with self.subTest(key=key):
                settings.write_text(json.dumps({"autoUpdatesChannel": "latest", "env": {key: "1"}}))
                result, _ = self.run_runtime("check")
                self.assertEqual(result.returncode, 1)
                self.assertIn(key, result.stderr)
        settings.write_text('{"autoUpdatesChannel": "latest"}')
        result, _ = self.run_runtime("check", env={"CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC": "0"})
        self.assertEqual(result.returncode, 1)
        self.assertIn("CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC", result.stderr)

    def test_install_enables_background_updates_without_changing_other_settings(self):
        settings = self.home / ".claude-personal/settings.json"
        settings.parent.mkdir()
        settings.write_text(json.dumps({"autoUpdatesChannel": "latest", "theme": "dark",
                                        "env": {"DISABLE_AUTOUPDATER": "1", "EXAMPLE_FLAG": "keep"}}))
        result, _ = self.run_runtime("install")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(settings.read_text()),
                         {"autoUpdatesChannel": "latest", "theme": "dark", "env": {"EXAMPLE_FLAG": "keep"}})

    def test_native_install_preserves_profile_and_arguments_in_neutral_directory(self):
        arguments = ["install", "latest", "--force"]
        result, calls = self.run_runtime("launch", "claude", "--", *arguments)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(calls[0]["args"], arguments)
        self.assertEqual(calls[0]["env"]["CLAUDE_CONFIG_DIR"], "/inherited/claude")
        self.assertNotEqual(calls[0]["cwd"], str(self.cwd))

    def test_update_from_explicit_profile_keeps_that_profile(self):
        profile = self.home / "selected-profile"
        result, calls = self.run_runtime("launch", "claude", "--", "update",
                                        env={"CLAUDE_CONFIG_DIR": str(profile), "RIG_AGENT_PROFILE": "selected"})
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(calls[0]["env"]["CLAUDE_CONFIG_DIR"], str(profile))
        self.assertEqual(calls[0]["env"]["CODEX_HOME"], "/inherited/codex")
        self.assertEqual(calls[0]["env"]["RIG_AGENT_PROFILE"], "selected")
        self.assertFalse((self.home / ".claude-personal/settings.json").exists())
        self.assertEqual(json.loads((profile / "settings.json").read_text()), {"autoUpdatesChannel": "latest"})

    def test_broken_policy_link_and_wrong_codex_owner_fail_closed(self):
        (self.config_dir / "agent-policy.json").symlink_to(self.root / "absent")
        result, calls = self.run_runtime("launch", "--personal", "codex", "--", "test")
        self.assertEqual(result.returncode, 1)
        self.assertIn("Broken configuration symlink", result.stderr)
        self.assertEqual(calls, [])
        (self.config_dir / "agent-policy.json").unlink()
        settings = json.loads(self.config.read_text())
        settings["codex"] = str(self.binaries / "other-codex")
        self.config.write_text(json.dumps(settings))
        result, calls = self.run_runtime("check")
        self.assertEqual(result.returncode, 1)
        self.assertIn("Configured Codex path must be the Homebrew command", result.stderr)
        self.assertEqual(len(calls), 1)


if __name__ == "__main__":
    unittest.main()
