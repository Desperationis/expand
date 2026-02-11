#!/bin/bash

# Sync installed config files back into this repository
# Run this after making changes to your local configs

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DATA_CONFIG="$SCRIPT_DIR/data/config"
USER_CONFIG="$HOME/.config"

sync_dir() {
    local src="$1"
    local dest="$2"
    local name="$3"

    if [ -d "$src" ]; then
        rm -rf "$dest"
        cp -r "$src" "$dest"
        echo "Synced $name"
    else
        echo "Skipped $name (not found)"
    fi
}

sync_file() {
    local src="$1"
    local dest="$2"
    local name="$3"

    if [ -f "$src" ]; then
        cp "$src" "$dest"
        echo "Synced $name"
    else
        echo "Skipped $name (not found)"
    fi
}

echo "Syncing configs to $DATA_CONFIG"
echo

# User configs (~/.config/*)
sync_dir "$USER_CONFIG/i3" "$DATA_CONFIG/i3" "i3"
sync_dir "$USER_CONFIG/i3blocks" "$DATA_CONFIG/i3blocks" "i3blocks"
sync_dir "$USER_CONFIG/nvim" "$DATA_CONFIG/nvim" "nvim"
sync_dir "$USER_CONFIG/fish" "$DATA_CONFIG/fish" "fish"
# Remove fisher-managed files that we don't want to track
rm -rf "$DATA_CONFIG/fish/completions" "$DATA_CONFIG/fish/functions"
rm -f "$DATA_CONFIG/fish/fish_plugins" "$DATA_CONFIG/fish/fish_variables"
sync_dir "$USER_CONFIG/alacritty" "$DATA_CONFIG/alacritty" "alacritty"
sync_dir "$USER_CONFIG/tmux" "$DATA_CONFIG/tmux" "tmux"
sync_file "$USER_CONFIG/user-dirs.conf" "$DATA_CONFIG/user-dirs.conf" "user-dirs.conf"

# Claude Code (~/.claude/)
sync_file "$HOME/.claude/settings.json" "$DATA_CONFIG/claude/settings.json" "claude settings.json"
sync_dir "$HOME/.claude/skills" "$DATA_CONFIG/claude/skills" "claude skills"

# System config (requires root)
if [ -f "/etc/tlp.conf" ]; then
    if [ "$(id -u)" -eq 0 ]; then
        cp /etc/tlp.conf "$DATA_CONFIG/tlp.conf"
        echo "Synced tlp.conf"
    else
        echo "Skipped tlp.conf (need root)"
    fi
else
    echo "Skipped tlp.conf (not found)"
fi

echo
echo "Done. Run 'git diff' to see changes."
