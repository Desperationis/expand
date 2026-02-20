#!/bin/bash

# Sync installed config files back into this repository
# Run this after making changes to your local configs
# Usage: ./sync_configs.sh <target>

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DATA_CONFIG="$SCRIPT_DIR/data/config"
USER_CONFIG="$HOME/.config"
OS="$(uname -s)"

COMMON_TARGETS="nvim, fish, alacritty, tmux, claude"
LINUX_TARGETS="i3, i3blocks, user-dirs, tlp"

show_usage() {
    echo "Usage: $0 <target>"
    echo "Targets: all, $COMMON_TARGETS"
    if [ "$OS" = "Linux" ]; then
        echo "Linux:   $LINUX_TARGETS"
    fi
}

if [ -z "$1" ]; then
    show_usage
    exit 1
fi

TARGET="$1"

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

sync_fish() {
    sync_dir "$USER_CONFIG/fish" "$DATA_CONFIG/fish" "fish"
    # Remove fisher-managed files that we don't want to track
    rm -rf "$DATA_CONFIG/fish/completions" "$DATA_CONFIG/fish/functions"
    rm -f "$DATA_CONFIG/fish/fish_plugins" "$DATA_CONFIG/fish/fish_variables"
}

sync_claude() {
    sync_file "$HOME/.claude/settings.json" "$DATA_CONFIG/claude/settings.json" "claude settings.json"
    sync_dir "$HOME/.claude/skills" "$DATA_CONFIG/claude/skills" "claude skills"
}

sync_tlp() {
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
}

sync_all_common() {
    sync_dir "$USER_CONFIG/nvim" "$DATA_CONFIG/nvim" "nvim"
    sync_fish
    sync_dir "$USER_CONFIG/alacritty" "$DATA_CONFIG/alacritty" "alacritty"
    sync_dir "$USER_CONFIG/tmux" "$DATA_CONFIG/tmux" "tmux"
    sync_claude
}

sync_all_linux() {
    sync_dir "$USER_CONFIG/i3" "$DATA_CONFIG/i3" "i3"
    sync_dir "$USER_CONFIG/i3blocks" "$DATA_CONFIG/i3blocks" "i3blocks"
    sync_file "$USER_CONFIG/user-dirs.conf" "$DATA_CONFIG/user-dirs.conf" "user-dirs.conf"
    sync_tlp
}

echo "Syncing configs to $DATA_CONFIG ($OS)"
echo

case "$TARGET" in
    all)
        sync_all_common
        if [ "$OS" = "Linux" ]; then
            sync_all_linux
        fi
        ;;
    nvim)
        sync_dir "$USER_CONFIG/nvim" "$DATA_CONFIG/nvim" "nvim"
        ;;
    fish)
        sync_fish
        ;;
    alacritty)
        sync_dir "$USER_CONFIG/alacritty" "$DATA_CONFIG/alacritty" "alacritty"
        ;;
    tmux)
        sync_dir "$USER_CONFIG/tmux" "$DATA_CONFIG/tmux" "tmux"
        ;;
    claude)
        sync_claude
        ;;
    i3)
        sync_dir "$USER_CONFIG/i3" "$DATA_CONFIG/i3" "i3"
        ;;
    i3blocks)
        sync_dir "$USER_CONFIG/i3blocks" "$DATA_CONFIG/i3blocks" "i3blocks"
        ;;
    user-dirs)
        sync_file "$USER_CONFIG/user-dirs.conf" "$DATA_CONFIG/user-dirs.conf" "user-dirs.conf"
        ;;
    tlp)
        sync_tlp
        ;;
    *)
        echo "Unknown target: $TARGET"
        show_usage
        exit 1
        ;;
esac

echo
echo "Done. Run 'git diff' to see changes."
