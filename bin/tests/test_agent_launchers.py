"""Profile routing checks using executable spies, without native clients."""

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


MODULE = Path(__file__).resolve().parents[2] / "zsh/agent-launchers.zsh"
PROFILES = ("claude", "codex", "claude-personal", "codex-personal")
CLAUDE_ADMIN = ("auth", "doctor", "install", "update", "upgrade", "mcp", "plugin", "plugins",
                "setup-token", "help", "-h", "--help", "-V", "--version")
CODEX_ADMIN = ("login", "logout", "mcp", "features", "completion", "help", "-h", "--help", "-V", "--version")
BOOTSTRAP = '''
source "$1"
shift
function _jig_native_claude { command claude "$@"; }
function _jig_native_codex { command codex "$@"; }
function claude { _jig_default claude "$@"; }
function codex { _jig_default codex "$@"; }
"$@"
'''


class AgentLauncherTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="rig-agent-launchers-")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name).resolve()
        self.bin = self.root / "spy-bin"
        self.bin.mkdir()
        self.cwd = self.root / "task with spaces"
        self.cwd.mkdir()
        self.log = self.root / "calls.jsonl"
        for name in ("jig", "claude", "codex"):
            spy = self.bin / name
            spy.write_text(f"#!{sys.executable}\n" + '''
import json, os, sys
with open(os.environ["SPY_LOG"], "a") as output:
    output.write(json.dumps({"command": os.path.basename(sys.argv[0]), "args": sys.argv[1:],
                            "cwd": os.getcwd(), "env": {key: os.environ.get(key) for key in
                            ("HOME", "CODEX_HOME", "CLAUDE_CONFIG_DIR", "CLAUDE_CODE_USE_BEDROCK",
                             "JIG_DISPATCHING_PROFILE")}}) + "\\n")
raise SystemExit(int(os.environ.get("SPY_EXIT", "0")))
''')
            spy.chmod(0o700)
        # HOME is retained solely to verify pinned profile paths. No test
        # reads or changes native profile files or sources the user's zshrc.
        self.env = {"HOME": os.environ["HOME"], "PATH": str(self.bin), "ZDOTDIR": str(self.root),
                    "SPY_LOG": str(self.log), "CODEX_HOME": "/inherited-codex",
                    "CLAUDE_CONFIG_DIR": "/inherited-claude", "CLAUDE_CODE_USE_BEDROCK": "1"}

    def run_shell(self, args, *, env=None, script=BOOTSTRAP):
        self.log.unlink(missing_ok=True)
        result = subprocess.run(["/bin/zsh", "-f", "-c", script, "fixture", str(MODULE), *args],
                                cwd=self.cwd, env=self.env | (env or {}), capture_output=True, text=True)
        calls = [json.loads(line) for line in self.log.read_text().splitlines()] if self.log.exists() else []
        return result, calls

    def test_sessions_route_all_profiles_through_jig_without_changing_argv_or_cwd(self):
        cases = ([], ["resume", "session-id"], ["--workspace", "task with spaces", "hello"],
                 ["--", "--help", "", "literal; $(no-command)"], ["--model", "fixture", "help"])
        for profile in PROFILES:
            for args in cases:
                with self.subTest(profile=profile, args=args):
                    result, calls = self.run_shell([profile, *args])
                    self.assertEqual(result.returncode, 0, result.stderr)
                    self.assertEqual(len(calls), 1)
                    self.assertEqual(calls[0]["command"], "jig")
                    self.assertEqual(calls[0]["args"], [profile, *args])
                    self.assertEqual(calls[0]["cwd"], str(self.cwd))
                    self.assertEqual(calls[0]["env"]["JIG_DISPATCHING_PROFILE"], profile)

    def test_only_explicit_first_argument_admin_commands_use_native_hooks(self):
        for profile in PROFILES:
            admins = CLAUDE_ADMIN if profile.startswith("claude") else CODEX_ADMIN
            for first in admins:
                with self.subTest(profile=profile, first=first):
                    args = [first, *(["list"] if first == "mcp" and profile.startswith("claude") else []),
                            "argument with spaces", "", "--literal"]
                    result, calls = self.run_shell([profile, *args])
                    self.assertEqual(result.returncode, 0, result.stderr)
                    self.assertEqual(len(calls), 1)
                    self.assertEqual(calls[0]["command"], profile.split("-")[0])
                    self.assertEqual(calls[0]["args"], args)
                    self.assertIsNone(calls[0]["env"]["JIG_DISPATCHING_PROFILE"])

    def test_claude_mcp_bypass_is_limited_to_management_subcommands(self):
        management = ([], ["help"], ["-h"], ["--help"], ["add"], ["add-json"], ["add-from-claude-desktop"],
                      ["get"], ["list"], ["login"], ["logout"], ["remove"], ["reset-project-choices"])
        for profile in ("claude", "claude-personal"):
            for tail in management:
                with self.subTest(profile=profile, tail=tail):
                    result, calls = self.run_shell([profile, "mcp", *tail])
                    self.assertEqual(result.returncode, 0, result.stderr)
                    self.assertEqual([call["command"] for call in calls], ["claude"])
                    self.assertEqual(calls[0]["args"], ["mcp", *tail])
            for tail in (["serve"], ["serve", "--verbose"], ["--scope", "user", "list"], ["unknown"]):
                with self.subTest(profile=profile, tail=tail):
                    result, calls = self.run_shell([profile, "mcp", *tail])
                    self.assertEqual(result.returncode, 0, result.stderr)
                    self.assertEqual([call["command"] for call in calls], ["jig"])
                    self.assertEqual(calls[0]["args"], [profile, "mcp", *tail])

    def test_server_cloud_and_background_modes_never_use_native_bypass(self):
        for profile in PROFILES:
            for first in ("app-server", "remote-control", "cloud", "--cloud", "--bg", "--background",
                          "attach", "serve", "exec-server", "--worktree", "--remote", "auth" if profile.startswith("codex") else "login"):
                with self.subTest(profile=profile, first=first):
                    result, calls = self.run_shell([profile, first])
                    self.assertEqual(result.returncode, 0, result.stderr)
                    self.assertEqual([call["command"] for call in calls], ["jig"])

    def test_nested_dispatch_fails_before_any_child(self):
        for profile in PROFILES:
            for args in ([], ["--help"]):
                with self.subTest(profile=profile, args=args):
                    result, calls = self.run_shell([profile, *args], env={"JIG_DISPATCHING_PROFILE": "codex"})
                    self.assertEqual(result.returncode, 2)
                    self.assertIn("refused recursive dispatch", result.stderr)
                    self.assertEqual(calls, [])
            result, calls = self.run_shell([profile, "hello"], env={"JIG_DISPATCHING_PROFILE": ""})
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(calls[0]["env"]["JIG_DISPATCHING_PROFILE"], profile)

    def test_missing_jig_has_no_native_fallback(self):
        (self.bin / "jig").unlink()
        for profile in PROFILES:
            result, calls = self.run_shell([profile, "hello"])
            self.assertEqual(result.returncode, 127)
            self.assertIn("command not found: jig", result.stderr)
            self.assertEqual(calls, [])

    def test_child_exit_status_and_dispatch_marker_are_not_lost_or_exported(self):
        for profile in PROFILES:
            for args in (["hello"], ["--help"]):
                result, calls = self.run_shell([profile, *args], env={"SPY_EXIT": "23"})
                self.assertEqual(result.returncode, 23)
                self.assertEqual(len(calls), 1)
        script = BOOTSTRAP + '\nprint -r -- "marker=${JIG_DISPATCHING_PROFILE-unset}"\n'
        result, calls = self.run_shell(["codex-personal", "hello"], script=script)
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "marker=unset\n")
        self.assertEqual(calls[0]["env"]["JIG_DISPATCHING_PROFILE"], "codex-personal")

    def test_personal_native_hooks_preserve_profile_environment(self):
        for profile in ("claude-personal", "codex-personal"):
            for invoked in (profile, "_jig_native_" + profile):
                result, calls = self.run_shell([invoked, "--help"])
                self.assertEqual(result.returncode, 0, result.stderr)
                observed = calls[0]["env"]
                self.assertEqual(observed["HOME"], self.env["HOME"])
                self.assertEqual(observed["CODEX_HOME"], self.env["HOME"] + "/.codex-personal")
                if profile.startswith("claude"):
                    self.assertEqual(observed["CLAUDE_CONFIG_DIR"], self.env["HOME"] + "/.claude-personal")
                    self.assertEqual(observed["CLAUDE_CODE_USE_BEDROCK"], "0")
                else:
                    self.assertEqual(observed["CLAUDE_CONFIG_DIR"], "/inherited-claude")
                    self.assertEqual(observed["CLAUDE_CODE_USE_BEDROCK"], "1")

    def test_codex_resolver_skips_personal_shim_directory(self):
        result, calls = self.run_shell(["_jig_native_codex-personal", "--help"],
                                       env={"PATH": self.env["HOME"] + "/.local/bin:" + str(self.bin)})
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual([call["command"] for call in calls], ["codex"])
        (self.bin / "codex").unlink()
        result, calls = self.run_shell(["_jig_native_codex-personal", "--help"])
        self.assertEqual(result.returncode, 1)
        self.assertIn("Real Codex binary not found", result.stderr)
        self.assertEqual(calls, [])


if __name__ == "__main__":
    unittest.main()
