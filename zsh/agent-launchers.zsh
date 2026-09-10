# Native profile hooks retain their original authentication and state behavior.
# Jig calls these hooks after applying its boundary, avoiding default recursion.
function _jig_native_claude-personal {
  CLAUDE_CONFIG_DIR="$HOME/.claude-personal" \
  CODEX_HOME="$HOME/.codex-personal" \
  CLAUDE_CODE_USE_BEDROCK=0 \
  command claude "$@"
}

# Find the real codex binary, skipping the ~/.local/bin shim.
_codex_real() {
  local dir candidate
  for dir in ${(s.:.)PATH}; do
    [[ "$dir" == "$HOME/.local/bin" ]] && continue
    candidate="$dir/codex"
    if [[ -x "$candidate" ]]; then
      print -r -- "$candidate"
      return 0
    fi
  done

  echo "Real Codex binary not found on PATH outside ~/.local/bin" >&2
  return 1
}

function _jig_native_codex-personal {
  local real_codex
  real_codex="$(_codex_real)" || return 1
  CODEX_HOME="$HOME/.codex-personal" "$real_codex" "$@"
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
        login|logout|mcp|features|completion|help|-h|--help|-V|--version)
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

function claude-personal { _jig_default claude-personal "$@"; }
function codex-personal { _jig_default codex-personal "$@"; }
