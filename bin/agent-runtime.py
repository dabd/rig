#!/usr/bin/python3
"""Launch separate agent profiles through one managed installation per agent."""

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile


class RuntimeErrorWithHint(Exception):
    pass


def read_object(path):
    if not path.exists():
        if path.is_symlink():
            raise RuntimeErrorWithHint("Broken configuration symlink: {}".format(path))
        return {}
    value = json.loads(path.read_text())
    if not isinstance(value, dict):
        raise RuntimeErrorWithHint("Expected a JSON object in {}".format(path))
    return value


def absolute_path(value, label):
    if not isinstance(value, str) or not Path(value).is_absolute():
        raise RuntimeErrorWithHint("{} must be an absolute path".format(label))
    return Path(value)


def installations(home):
    settings = read_object(home / ".config/rig/agent-installations.json")
    brew = settings.get("brew")
    if brew is None:
        brew = next((str(path) for path in
                     (Path("/opt/homebrew/bin/brew"), Path("/usr/local/bin/brew"))
                     if path.is_file()), "/opt/homebrew/bin/brew")
    brew = absolute_path(brew, "brew")
    return {"brew": brew,
            "codex": absolute_path(settings.get("codex", str(brew.parent / "codex")), "codex"),
            "claude": absolute_path(settings.get("claude", str(home / ".local/bin/claude")), "claude")}


def executable(path):
    if not path.is_file() or not os.access(path, os.X_OK):
        raise RuntimeErrorWithHint("Managed executable missing: {}. Run ~/rig/bin/agent-runtime.py install."
                                   .format(path))
    # Keep the stable symlink, so a vendor update is visible on the next launch.
    return str(path)


def policy_list(policy, name):
    value = policy.get(name, [])
    if not isinstance(value, list) or any(not isinstance(item, str) or not item for item in value):
        raise RuntimeErrorWithHint("{} must be a list of nonempty strings".format(name))
    return value


def personal_environment(home):
    env = dict(os.environ)
    policy = read_object(home / ".config/rig/agent-policy.json")
    for key in policy_list(policy, "personal_unset_env"):
        env.pop(key, None)
    personal_bin = str(home / "rig/bin/personal")
    env["PATH"] = os.pathsep.join([personal_bin] + [part for part in env.get("PATH", "").split(os.pathsep)
                                                   if part != personal_bin])
    env["RIG_AGENT_PERSONAL_BIN"] = personal_bin
    env.update(CODEX_HOME=str(home / ".codex-personal"),
               CLAUDE_CONFIG_DIR=str(home / ".claude-personal"),
               CLAUDE_CODE_USE_BEDROCK="0", CLAUDE_CODE_USE_VERTEX="0",
               CLAUDE_CODE_USE_FOUNDRY="0", RIG_AGENT_PROFILE="personal")
    return env, policy


def run_neutral(command, env):
    # Do not load project instructions or local settings for administration.
    with tempfile.TemporaryDirectory(prefix="rig-agent-maintenance-") as cwd:
        return subprocess.run(command, env=env, cwd=cwd).returncode


def latest_claude_settings(directory):
    path = directory / "settings.json"
    value = read_object(path)
    desired = dict(value, autoUpdatesChannel="latest")
    if isinstance(value.get("env"), dict) and "DISABLE_AUTOUPDATER" in value["env"]:
        desired["env"] = dict(value["env"])
        del desired["env"]["DISABLE_AUTOUPDATER"]
    if desired == value:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.is_symlink():
        raise RuntimeErrorWithHint("Detach settings from repository symlinks before updating: {}"
                                   .format(path))
    with tempfile.NamedTemporaryFile(mode="w", dir=path.parent, delete=False) as output:
        temporary = Path(output.name)
        try:
            json.dump(desired, output, indent=2)
            output.write("\n")
            output.flush()
            os.fsync(output.fileno())
            os.replace(temporary, path)
        finally:
            temporary.unlink(missing_ok=True)


def verify_codex_owner(paths, env, installed=True):
    brew = executable(paths["brew"])
    with tempfile.TemporaryDirectory(prefix="rig-agent-maintenance-") as cwd:
        prefix = subprocess.run([brew, "--prefix"], cwd=cwd, env=env, check=True,
                                capture_output=True, text=True).stdout.strip()
        expected = absolute_path(prefix, "Homebrew prefix") / "bin/codex"
        if paths["codex"] != expected:
            raise RuntimeErrorWithHint("Configured Codex path must be the Homebrew command: {}".format(expected))
        if installed:
            subprocess.run([brew, "list", "--cask", "codex"], cwd=cwd, env=env, check=True,
                           capture_output=True, text=True)


def check_claude_updates(home, env):
    settings = read_object(home / ".claude-personal/settings.json")
    channel = settings.get("autoUpdatesChannel", "latest")
    configured_env = settings.get("env", {})
    if not isinstance(configured_env, dict):
        raise RuntimeErrorWithHint("Claude settings env must be an object")
    def disables_updates(key, source):
        value = str(source.get(key, ""))
        if key == "CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC":
            return bool(value)
        return value.lower() in ("1", "true", "yes")

    disabled = [key for key in ("DISABLE_AUTOUPDATER", "DISABLE_UPDATES",
                                "CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC")
                if any(disables_updates(key, source) for source in (env, configured_env))]
    print("Claude personal update channel: {}".format(channel), flush=True)
    if channel != "latest" or disabled:
        details = "disabled by " + ", ".join(disabled) if disabled else "expected latest channel"
        raise RuntimeErrorWithHint("Claude automatic updates: {}".format(details))


def maintain(home, paths, agent, install=False, env=None):
    env = dict(env) if env is not None else personal_environment(home)[0]
    env.pop("DISABLE_AUTOUPDATER", None)
    if agent == "codex":
        brew = executable(paths["brew"])
        if sys.platform != "darwin":
            raise RuntimeErrorWithHint("Codex cask installation requires macOS and Homebrew.")
        verify_codex_owner(paths, env, installed=not install)
        action = "install" if install else "upgrade"
        result = run_neutral([brew, action, "--cask", "codex"], env)
    else:
        directory = absolute_path(env.get("CLAUDE_CONFIG_DIR"), "CLAUDE_CONFIG_DIR")
        latest_claude_settings(directory)
        if install and not paths["claude"].is_file():
            if paths["claude"] != home / ".local/bin/claude":
                raise RuntimeErrorWithHint("Install the configured Claude executable with its owning installer.")
            with tempfile.TemporaryDirectory(prefix="rig-claude-installer-") as directory:
                script = Path(directory) / "install.sh"
                subprocess.run(["/usr/bin/curl", "-fsSL", "https://claude.ai/install.sh", "-o", str(script)],
                               check=True, env=env, cwd=directory)
                result = run_neutral(["/bin/bash", str(script), "latest"], env)
        else:
            result = run_neutral([executable(paths["claude"]), "update"], env)
    if result:
        return result
    return run_neutral([executable(paths[agent]), "--version"], env)


def launch(home, paths, agent, args, personal):
    env = personal_environment(home)[0] if personal else dict(os.environ)
    if agent == "codex":
        # A child of an older package-manager launcher may inherit its marker.
        # The managed native binary must detect its own installation method.
        for key in ("CODEX_MANAGED_BY_NPM", "CODEX_MANAGED_BY_BUN", "CODEX_MANAGED_BY_PNPM",
                    "CODEX_MANAGED_BY_VITE_PLUS", "CODEX_MANAGED_PACKAGE_ROOT"):
            env.pop(key, None)
    # Codex's update notice must reach the package manager that owns this binary.
    if args and args[0] in ("update", "upgrade") and args[1:] not in (["-h"], ["--help"]):
        if len(args) != 1:
            raise RuntimeErrorWithHint("Use ~/rig/bin/agent-runtime.py update {} for managed upgrades."
                                       .format(agent))
        return maintain(home, paths, agent, env=env)
    command = [executable(paths[agent])] + args
    if agent == "claude" and args[:1] == ["install"]:
        return run_neutral(command, env)
    os.execve(command[0], command, env)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    path = commands.add_parser("path")
    path.add_argument("agent", choices=("codex", "claude"))
    start = commands.add_parser("launch")
    start.add_argument("--personal", action="store_true")
    start.add_argument("agent", choices=("codex", "claude"))
    start.add_argument("args", nargs=argparse.REMAINDER)
    commands.add_parser("install")
    update = commands.add_parser("update")
    update.add_argument("agent", choices=("codex", "claude", "all"))
    commands.add_parser("check")
    args = parser.parse_args()
    home = Path.home()
    try:
        paths = installations(home)
        if args.command == "path":
            print(executable(paths[args.agent]))
            return 0
        if args.command == "launch":
            return launch(home, paths, args.agent, args.args, args.personal)
        if args.command == "check":
            env, _ = personal_environment(home)
            verify_codex_owner(paths, env)
            for agent in ("codex", "claude"):
                print("{}: {}".format(agent, executable(paths[agent])), flush=True)
                result = run_neutral([str(paths[agent]), "--version"], env)
                if result:
                    return result
            check_claude_updates(home, env)
            return 0
        agents = ("codex", "claude") if args.command == "install" or args.agent == "all" else (args.agent,)
        for agent in agents:
            if args.command == "install" and paths[agent].is_file():
                if agent == "claude":
                    latest_claude_settings(home / ".claude-personal")
                else:
                    verify_codex_owner(paths, personal_environment(home)[0])
                continue
            result = maintain(home, paths, agent, args.command == "install")
            if result:
                return result
        return 0
    except (RuntimeErrorWithHint, OSError, ValueError, subprocess.CalledProcessError) as error:
        print("agent-runtime: {}".format(error), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
