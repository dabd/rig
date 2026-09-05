#!/usr/bin/env python3
"""Install manifest-selected skills; dry-run by default, --apply makes changes."""
import argparse
import datetime
import json
from pathlib import Path


def manifest(path):
    data = json.loads(path.read_text())
    for names in data.values():
        if not isinstance(names, list) or len(names) != len(set(names)):
            raise ValueError(f"Invalid or duplicate list in {path}")
        if any(not isinstance(n, str) or not n or
               any(c not in "abcdefghijklmnopqrstuvwxyz0123456789-" for c in n)
               for n in names):
            raise ValueError(f"Invalid skill name in {path}")
    return data


def plan(root, home, work):
    config = manifest(root / "agent-policy/skills.json")
    shared = config["shared"]
    links = {}
    profiles = [(".claude-personal", "claude"), (".codex-personal", "codex")]
    if work:
        profiles.extend([(".claude", "claude"), (".codex", "codex")])
    for profile, host in profiles:
        for name in shared + config[f"{host}_only"]:
            source = root / ("claude-shared/skills" if name in shared else f"{host}/skills") / name
            links[home / profile / "skills" / name] = source
    retire = []
    if work:
        work_config = manifest(work / "agent-policy/skills.json")
        for name in work_config["skills"]:
            for profile in (".claude", ".codex"):
                destination = home / profile / "skills" / name
                if destination in links:
                    raise ValueError(f"Shared/work skill collision: {name}")
                links[destination] = work / "work-skills" / name
        retire = [home / ".agents/skills" / n for n in work_config["retire_global"]]
    for source in links.values():
        if not (source / "SKILL.md").is_file():
            raise ValueError(f"Missing skill: {source}")
    return links, retire


def present(path):
    return path.exists() or path.is_symlink()


def same_source(destination, source):
    # Whole-directory Nix symlinks can already expose the exact source directory.
    return present(destination) and destination.resolve() == source.resolve()


def execute(root, home, work, apply=False):
    links, retire = plan(root, home, work)
    pending = [(d, s) for d, s in links.items() if not same_source(d, s)]
    retire = [p for p in retire if present(p)]
    # Never write links into the source tree through a whole-directory symlink.
    # Nix-managed personal profiles should already expose the required entries.
    for destination, _ in pending:
        if destination.parent.is_symlink():
            raise ValueError(f"Missing or conflicting source entry behind {destination.parent}; fix the source first")
    stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    backup_root = home / ".local/state/rig-skill-backups" / stamp

    def backup(path):
        saved = backup_root / path.relative_to(home)
        if apply:
            saved.parent.mkdir(parents=True, exist_ok=True)
            path.rename(saved)
        print(f"{'Backed up' if apply else 'Would back up'} {path} -> {saved}")

    for path in retire:
        backup(path)
    for destination, source in pending:
        if present(destination):
            backup(destination)
        if apply:
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.symlink_to(source, target_is_directory=True)
        print(f"{'Linked' if apply else 'Would link'} {destination} -> {source}")
    print(f"{len(links)} selected links; {len(pending)} changes; {len(retire)} global entries archived.")
    if apply:
        wrong = [str(d) for d, s in links.items() if not same_source(d, s)]
        if wrong or any(present(p) for p in retire):
            raise ValueError("Installation verification failed: " + ", ".join(wrong))
    return len(pending) + len(retire)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--home", type=Path, default=Path.home())
    parser.add_argument("--work-repo", type=Path)
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.apply and args.check:
        parser.error("--apply and --check are mutually exclusive")
    try:
        count = execute(args.root.resolve(), args.home.resolve(),
                        args.work_repo.resolve() if args.work_repo else None, args.apply)
    except (ValueError, OSError) as error:
        parser.exit(1, f"{error}\n")
    if args.check and count:
        parser.exit(1, "Installed skills differ from the manifests.\n")


if __name__ == "__main__":
    main()
