#!/bin/bash
# Set @agent_profile=personal on each pane whose foreground Codex runs the
# personal profile, so window-status formats read an option, not a #() job.
# tmux reruns #() jobs on every status redraw, per window, and endpoint security
# scans each spawn; one poller per server does a few spawns per interval.
# Foreground process groups exclude suspended and background Codex sessions.
# Read only the selected processes; never print or save their environment.
# tmux.conf starts this with run-shell -b, which sets TMUX to this server.
interval=15
expected="CODEX_HOME=$HOME/.codex-personal"

socket=$(tmux display -p '#{socket_path}' 2>/dev/null) || exit 0
pidfile="${TMPDIR:-/tmp}/tmux-agent-profile-$(id -u)-${socket//\//_}.pid"
# A config reload starts another copy; keep the running one.
if old=$(cat "$pidfile" 2>/dev/null) && [[ "$old" =~ ^[0-9]+$ ]] &&
    ps -o command= -p "$old" 2>/dev/null | grep -q agent-profile-poller; then
  exit 0
fi
echo $$ > "$pidfile"

while panes=$(tmux list-panes -a -F '#{pane_id} #{pane_tty} #{@agent_profile}' 2>/dev/null); do
  fg=$(ps -Ao tty=,pid=,pgid=,tpgid=,comm= 2>/dev/null |
    awk '$3 == $4 && $5 ~ /(^|\/)codex$/ { print $1, $2 }')
  personal_ttys=" "
  if [[ -n "$fg" ]]; then
    pids=$(awk '{ printf "%s%s", sep, $2; sep = "," }' <<< "$fg")
    personal=$(ps eww -o pid=,command= -p "$pids" 2>/dev/null |
      awk -v expected="$expected" '
        { for (i = 2; i <= NF; i++) if ($i == expected) { print $1; next } }')
    for pid in $personal; do
      personal_ttys+="$(awk -v pid="$pid" '$2 == pid { print $1 }' <<< "$fg") "
    done
  fi

  cmd=()
  while read -r pane tty profile; do
    want=""
    [[ "$personal_ttys" == *" ${tty#/dev/} "* ]] && want=personal
    [[ "$want" == "$profile" ]] && continue
    if [[ -n "$want" ]]; then
      cmd+=(set -p -t "$pane" @agent_profile "$want" \;)
    else
      cmd+=(set -pu -t "$pane" @agent_profile \;)
    fi
  done <<< "$panes"
  ((${#cmd[@]})) && tmux "${cmd[@]}" 2>/dev/null

  sleep "$interval"
done
[[ "$(cat "$pidfile" 2>/dev/null)" == "$$" ]] && rm -f "$pidfile"
