#!/usr/bin/env bash
# Fresh-machine setup. Idempotent: safe to re-run; never overwrites stubs.
set -euo pipefail

repo="$(cd "$(dirname "$0")" && pwd)"
if [ "$repo" != "$HOME/rig" ]; then
  echo "error: repo must live at ~/rig (out-of-store symlinks depend on it), found $repo" >&2
  exit 1
fi

command -v nix >/dev/null 2>&1 || {
  echo "error: install nix first (https://nixos.org/download), then re-run" >&2
  exit 1
}

# Stubs: create once, never overwrite (installers append to the real files).
[ -f "$HOME/.zshrc" ] || cp "$repo/zsh/zshrc.stub" "$HOME/.zshrc"
[ -f "$HOME/.gitconfig" ] || cp "$repo/git/gitconfig.stub" "$HOME/.gitconfig"

# Satellite tools at a stable path.
mkdir -p "$HOME/tools"
# Clone once, then fast-forward on every run so pushed tool fixes reach this
# machine. A dirty or diverged clone only warns: local work is never touched.
for tool in save-our-sessions claude-setup tacit; do
  dir="$HOME/tools/$tool"
  if [ -d "$dir" ]; then
    git -C "$dir" pull --ff-only --quiet || echo "warning: $dir not updated (local changes or diverged); pull it by hand" >&2
  else
    git clone "git@github.com:dabd/$tool.git" "$dir"
  fi
done

# oh-my-zsh + the two custom plugins zshrc.core expects.
[ -d "$HOME/.oh-my-zsh" ] || sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)" "" --unattended
zsh_custom="$HOME/.oh-my-zsh/custom"
[ -d "$zsh_custom/plugins/zsh-autosuggestions" ] || git clone https://github.com/zsh-users/zsh-autosuggestions "$zsh_custom/plugins/zsh-autosuggestions"
[ -d "$zsh_custom/plugins/zsh-syntax-highlighting" ] || git clone https://github.com/zsh-users/zsh-syntax-highlighting.git "$zsh_custom/plugins/zsh-syntax-highlighting"

python3 "$repo/bin/render-agent-policy.py"

if command -v home-manager >/dev/null 2>&1; then
  home-manager switch --flake "$HOME/rig#default" --impure
else
  nix run home-manager/master -- switch --flake "$HOME/rig#default" --impure
fi

python3 "$repo/bin/install-agent-skills.py" --apply
/usr/bin/python3 "$repo/bin/agent-runtime.py" install
/usr/bin/python3 "$repo/bin/agent-runtime.py" check

echo "done. work machines: clone the work overlay repo and run its install.sh."
