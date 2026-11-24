# Native profile hooks retain their original authentication and state behavior.
# Jig calls these hooks after applying its boundary, avoiding default recursion.
function _jig_native_claude-personal {
  /usr/bin/python3 "$HOME/rig/bin/agent-runtime.py" launch --personal claude -- "$@"
}

# Kept for callers that need the managed Codex path.
_codex_real() {
  /usr/bin/python3 "$HOME/rig/bin/agent-runtime.py" path codex
}

function _jig_native_codex-personal {
  /usr/bin/python3 "$HOME/rig/bin/agent-runtime.py" launch --personal codex -- "$@"
}

_jig_default() {
  local jig_profile="$1"
  shift
  if [[ -n "${JIG_DISPATCHING_PROFILE-}" ]]; then
    print -u2 -- "Jig default launch refused recursive dispatch: $JIG_DISPATCHING_PROFILE -> $jig_profile"
    return 2
  fi

  local native_hook="_jig_native_${jig_profile}"
  case "$jig_profile" in
    claude|claude-personal)
      case "${1-}" in
        auth|doctor|install|update|upgrade|plugin|plugins|setup-token|help|-h|--help|-V|--version)
          "$native_hook" "$@"
          return $?
          ;;
        mcp)
          case "${2-}" in
            ""|help|-h|--help|add|add-json|add-from-claude-desktop|get|list|login|logout|remove|reset-project-choices)
              "$native_hook" "$@"
              return $?
              ;;
          esac
          ;;
      esac
      ;;
    codex|codex-personal)
      case "${1-}" in
        login|logout|mcp|features|completion|help|-h|--help|-V|--version|update|upgrade)
          "$native_hook" "$@"
          return $?
          ;;
      esac
      ;;
    *)
      print -u2 -- "Unknown Jig profile: $jig_profile"
      return 2
      ;;
  esac

  JIG_DISPATCHING_PROFILE="$jig_profile" command jig "$jig_profile" "$@"
}

# jig remains available explicitly; ordinary launches use the native profiles.
function claude-personal { _jig_native_claude-personal "$@"; }
function codex-personal { _jig_native_codex-personal "$@"; }

# Child shells retain their selected profile after version managers alter PATH.
if [[ "${RIG_AGENT_PROFILE-}" == personal ]]; then
  export RIG_AGENT_PERSONAL_BIN="$HOME/rig/bin/personal"
  export PATH="$RIG_AGENT_PERSONAL_BIN:$PATH"
  function codex { _jig_native_codex-personal "$@"; }
  function claude { _jig_native_claude-personal "$@"; }
fi
