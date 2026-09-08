# Containment tool integration

Containment is an independent satellite tool. It owns the policy engine, trusted
registry, source composition, installed runtime preparation and recovery code.
It must work without this machine-configuration repository.

Rig provides a thin `rig-contained-source` command that delegates offline source
maintenance to an independently installed `contained-source` executable. It
refuses when that executable is absent. Home Manager installs the wrapper; it
does not install or activate a containment release. The wrapper passes arguments
to the tool's closed maintenance CLI and contains no policy-generation logic.

The tool currently provides source preparation and an unavailable client-launch
entrypoint. A validated launch runtime, release version and distribution source
must exist before bootstrap can pin a downloadable package or normal agent
commands can move to it. There is no inferred repository URL or automatic
download in this integration.

## Ownership

| Location | Responsibility |
| --- | --- |
| Independent tool | Generic enforcement and recovery mechanisms, versioned input contracts, synthetic tests |
| This repository | Portable installation integration, optional command wiring and personal-safe defaults |
| Optional private overlay | Work provider references, network policy and work integration declarations |
| Local configuration | Exact registered paths, executable and directory pins, personal profile choices and credential references |
| Local runtime state | Prepared releases, registrations, transcripts, indexes, logs and caches |

The private overlay can consume the public tool's contract. Neither this
repository nor the tool should import a private repository or assume an employer.
Credentials and runtime data are never source-bundle inputs.

## Offline preparation

After installing a reviewed version of the standalone tool, its CLI can create
an inactive candidate using local inputs and an optional private overlay:

```sh
rig-contained-source prepare \
  --local-input /path/to/reviewed-machine-input.json \
  --overlay /path/to/private-overlay.json \
  --output "$HOME/.local/share/contained/candidates/new-candidate"
```

The output directory must be fresh and its parent must already exist. Omit `--overlay` when local input supplies
all profile declarations. This is a controller maintenance operation, not an
agent permission request or a running-session command. The tool validates the
registered identities, protected paths, profile policy and copied source.

Preparing source does not make client execution available. Ordinary `codex`,
`codex-personal`, `claude` and `claude-personal` commands retain their existing
behavior until a separately validated runtime is ready for cutover. Existing
client configuration remains runtime-managed; installing this tool must not
replace those files with repository symlinks or change their shared status line.
