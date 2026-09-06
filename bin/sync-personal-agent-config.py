#!/usr/bin/env python3
"""Keep tracked personal defaults separate from writable local agent config."""
import argparse
import copy
import json
import os
from pathlib import Path
import tempfile
import tomllib


FILES = {
    ".codex-personal/config.toml": "codex/config.toml",
    ".claude-personal/settings.json": "claude/settings.json",
    ".codex-personal/hooks.json": "codex/hooks.json",
}
MISSING = object()


def merge(old, new, current):
    """Update unchanged defaults; keep local additions, edits, and deletions."""
    if isinstance(new, dict) and isinstance(current, dict):
        previous = old if isinstance(old, dict) else {}
        result = copy.deepcopy(current)
        for key in previous.keys() | new.keys():
            value = merge(previous.get(key, MISSING), new.get(key, MISSING),
                          current.get(key, MISSING))
            if value is MISSING:
                result.pop(key, None)
            else:
                result[key] = value
        return result
    if current == old or (old is MISSING and current is MISSING):
        return new
    return current


def parse(path, content):
    return tomllib.loads(content) if path.suffix == ".toml" else json.loads(content)


def encode(path, data):
    if path.suffix == ".toml":
        import tomli_w  # Supplied by the pinned Home Manager Python environment.
        return tomli_w.dumps(data)
    return json.dumps(data, indent=2) + "\n"


def write_local(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(mode="w", dir=path.parent, delete=False) as file:
        temporary = Path(file.name)
        try:
            file.write(content)
            file.flush()
            os.fsync(file.fileno())
            os.replace(temporary, path)  # Replace the link itself, never its target.
        finally:
            temporary.unlink(missing_ok=True)


def sync(root, home, apply=False, detach_only=False):
    state_dir = home / ".local/state/rig-agent-config"
    baseline = state_dir / "defaults.json"
    if baseline.is_symlink():
        raise ValueError(f"Unexpected baseline symlink: {baseline}")
    old = json.loads(baseline.read_text()) if baseline.exists() else {}
    defaults, pending = {}, []
    for relative, source in FILES.items():
        path, template = home / relative, root / source
        if path.parent.is_symlink():
            raise ValueError(f"Unexpected profile directory symlink: {path.parent}")
        if path.is_symlink() and path.resolve() != template.resolve():
            raise ValueError(f"Unexpected config symlink: {path}")
        default_text = template.read_text()
        defaults[relative] = parse(template, default_text)
        exists = path.exists()
        text = path.read_text() if exists else None
        current = parse(path, text) if exists else {}
        if detach_only:
            if path.is_symlink():
                pending.append((path, text, text))
            continue
        updated = merge(old.get(relative, {}), defaults[relative], current) if exists else defaults[relative]
        if path.is_symlink() or not exists or updated != current:
            content = text if exists and updated == current else encode(path, updated)
            pending.append((path, text, content))
    if not detach_only and old != defaults:
        pending.append((baseline, baseline.read_text() if baseline.exists() else None,
                        json.dumps(defaults, indent=2) + "\n"))
    # Parse and plan every file before writing. Save originals before replacement.
    backup = None
    for path, original, content in pending:
        print(f"{'Update' if apply else 'Would update'} {path}")
        if not apply:
            continue
        actual = path.read_text() if path.exists() else None
        if actual != original:
            raise ValueError(f"Concurrent config change: {path}; rerun when the agent is idle")
        if original is not None:
            if backup is None:
                state_dir.mkdir(parents=True, exist_ok=True, mode=0o700)
                backup = Path(tempfile.mkdtemp(prefix="backup-", dir=state_dir))
                print(f"Backup: {backup}")
            write_local(backup / path.relative_to(home), original)
        write_local(path, content)
    return len(pending)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--home", type=Path, default=Path.home())
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--apply", action="store_true")
    mode.add_argument("--check", action="store_true")
    parser.add_argument("--detach-only", action="store_true")
    args = parser.parse_args()
    try:
        changes = sync(args.root.resolve(), args.home.resolve(), args.apply, args.detach_only)
    except (OSError, ValueError) as error:
        parser.exit(1, f"{error}\n")
    if args.check and changes:
        parser.exit(1, "Personal config defaults need synchronization.\n")


if __name__ == "__main__":
    main()
