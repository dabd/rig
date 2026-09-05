#!/usr/bin/env bash
set -euo pipefail

# install.sh
# Sets up the /audit-docs skill for documentation audit cycles.

SKILL_DIR="$(cd "$(dirname "$0")/.." && pwd)"
CONFIG_DIR="$HOME/.config/audit-docs"
CONFIG_FILE="$CONFIG_DIR/audit-docs.yaml"

echo "======================================"
echo "  audit-docs Skill Installer"
echo "======================================"
echo ""

# --- Verify skill files exist ---

if [ ! -f "$SKILL_DIR/SKILL.md" ]; then
  echo "Error: SKILL.md not found at $SKILL_DIR/SKILL.md"
  echo "Run this script from the audit-docs skill directory."
  exit 1
fi
echo "✓ SKILL.md found"

# --- Check dependencies ---

# The skill needs no external tools beyond what Claude Code provides (Read, Edit, Bash).
# However, find/grep/jq are used for file resolution and should be present.

MISSING_DEPS=()

if ! command -v find &>/dev/null; then
  MISSING_DEPS+=("find")
fi

if ! command -v grep &>/dev/null; then
  MISSING_DEPS+=("grep")
fi

if ! command -v jq &>/dev/null; then
  MISSING_DEPS+=("jq")
fi

if [ ${#MISSING_DEPS[@]} -gt 0 ]; then
  echo ""
  echo "Missing dependencies: ${MISSING_DEPS[*]}"
  if command -v brew &>/dev/null; then
    read -p "Install via Homebrew? [Y/n]: " INSTALL_DEPS
    INSTALL_DEPS="${INSTALL_DEPS:-Y}"
    if [[ "$INSTALL_DEPS" =~ ^[Yy] ]]; then
      brew install "${MISSING_DEPS[@]}"
    else
      echo "⚠ Skill may not function correctly without: ${MISSING_DEPS[*]}"
    fi
  else
    echo "⚠ Install these manually: ${MISSING_DEPS[*]}"
  fi
else
  echo "✓ All dependencies present (find, grep, jq)"
fi

# --- Configuration ---

echo ""
echo "The /audit-docs skill can be configured with project-specific defaults."
echo "This is optional — the skill works without configuration by auto-detecting targets."
echo ""

mkdir -p "$CONFIG_DIR"

if [ -f "$CONFIG_FILE" ]; then
  echo "Existing config found at $CONFIG_FILE"
  read -p "Overwrite with fresh config? [y/N]: " OVERWRITE
  OVERWRITE="${OVERWRITE:-N}"
  if [[ ! "$OVERWRITE" =~ ^[Yy] ]]; then
    echo "Keeping existing config."
    echo ""
    echo "======================================"
    echo "  Installation complete!"
    echo "======================================"
    echo ""
    echo "Usage:"
    echo "  /audit-docs docs/plans/"
    echo "  /audit-docs all plan documents"
    echo "  /audit-docs phase 3 and phase 1.5"
    echo "  /audit-docs"
    exit 0
  fi
fi

# --- Gather defaults ---

echo "Configure default behavior (press Enter to skip any):"
echo ""

read -p "Default docs directory []: " DEFAULT_DIR
read -p "File extensions to include (comma-separated) [md,mdx]: " FILE_EXTENSIONS
FILE_EXTENSIONS="${FILE_EXTENSIONS:-md,mdx}"

read -p "Maximum audit cycles before pausing [5]: " MAX_CYCLES
MAX_CYCLES="${MAX_CYCLES:-5}"

echo ""
echo "Severity policy — which levels should be fixed automatically?"
echo "  Options: critical,high,medium (default) or critical,high (stricter threshold)"
read -p "Fix severities [critical,high,medium]: " FIX_SEVERITIES
FIX_SEVERITIES="${FIX_SEVERITIES:-critical,high,medium}"

echo ""
echo "Should the skill expand cross-references automatically?"
echo "  (i.e., if audited files reference other files, include those too)"
read -p "Auto-expand cross-references? [Y/n]: " AUTO_EXPAND
AUTO_EXPAND="${AUTO_EXPAND:-Y}"
if [[ "$AUTO_EXPAND" =~ ^[Yy] ]]; then
  AUTO_EXPAND_VAL="true"
else
  AUTO_EXPAND_VAL="false"
fi

# --- Write config ---

cat > "$CONFIG_FILE" << EOF
# ~/.config/audit-docs/audit-docs.yaml
# Configuration for the /audit-docs skill.

# Default directory to audit when no argument is provided.
# Leave empty to auto-detect from project structure.
default_directory: "${DEFAULT_DIR}"

# File extensions to include in audits (comma-separated, no dots).
file_extensions: "${FILE_EXTENSIONS}"

# Maximum audit cycles before pausing to ask the user.
# Prevents infinite loops from oscillating fixes.
max_cycles: ${MAX_CYCLES}

# Severity levels that trigger automatic fixes.
# Issues below this threshold are reported but not fixed.
# Options: critical,high,medium | critical,high | critical
fix_severities: "${FIX_SEVERITIES}"

# Whether to automatically include files referenced by audited documents.
# When true, cross-referenced files are added to the audit scope.
auto_expand_crossrefs: ${AUTO_EXPAND_VAL}

# Directories or patterns to exclude from audits (one per line).
# Uses gitignore-style patterns.
exclude:
  - node_modules/
  - dist/
  - .git/
  - "*.generated.md"
EOF

echo ""
echo "✓ Created config at $CONFIG_FILE"

# --- Summary ---

echo ""
echo "======================================"
echo "  Installation complete!"
echo "======================================"
echo ""
echo "Configuration:"
echo "  Config file:      $CONFIG_FILE"
echo "  Default dir:      ${DEFAULT_DIR:-<auto-detect>}"
echo "  File extensions:  $FILE_EXTENSIONS"
echo "  Max cycles:       $MAX_CYCLES"
echo "  Fix severities:   $FIX_SEVERITIES"
echo "  Cross-ref expand: $AUTO_EXPAND_VAL"
echo ""
echo "Usage (start a new Claude Code session first):"
echo "  /audit-docs docs/plans/                    # explicit path"
echo "  /audit-docs src/**/*.md                    # glob pattern"
echo "  /audit-docs all plan documents             # natural language"
echo "  /audit-docs the UAC phase plans            # natural language"
echo "  /audit-docs                                # auto-detect"
echo ""
echo "Edit config anytime:"
echo "  $CONFIG_FILE"
