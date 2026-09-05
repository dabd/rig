#!/bin/bash
# Label the active pane's personal Codex process, not its directory or title.
# Foreground process groups exclude suspended and background Codex sessions.
# Read only the selected processes; never print or save their environment.
tty=${1#/dev/}
[[ -n "$tty" && "$tty" != *[!a-zA-Z0-9/_-]* ]] || exit 0

pids=$(ps -t "$tty" -o pid=,pgid=,tpgid=,comm= 2>/dev/null |
  awk '$2 == $3 && $4 ~ /(^|\/)codex$/ { print $1 }')
for pid in $pids; do
  if ps eww -p "$pid" -o command= 2>/dev/null |
      awk -v expected="CODEX_HOME=$HOME/.codex-personal" '
        { for (i = 1; i <= NF; i++) if ($i == expected) found = 1 }
        END { exit !found }
      '; then
    printf 'personal \n'
    exit 0
  fi
done
exit 0
