#!/bin/bash
set -euo pipefail

SESSION="default"
SHELLS_REGEX='^(bash|zsh|fish|sh)$'

# Optional: set DRY_RUN=1 to preview which panes would be killed.
DRY_RUN="${DRY_RUN:-0}"

# Ensure the session exists
if ! tmux has-session -t "$SESSION" 2>/dev/null; then
  echo "tmux session '$SESSION' not found."
  exit 1
fi

# List every pane in the session and kill the unused ones
tmux list-panes -s -t "$SESSION" -F '#{pane_id} #{pane_current_command} #{pane_dead}' \
| while read -r pane_id pane_cmd pane_dead; do
    if [[ "$pane_dead" == "1" || "$pane_cmd" =~ $SHELLS_REGEX ]]; then
      if [[ "$DRY_RUN" == "1" ]]; then
        echo "Would kill pane $pane_id (cmd='$pane_cmd', dead=$pane_dead)"
      else
        tmux kill-pane -t "$pane_id"
      fi
    fi
  done


# Close all alacritty windows 
i3-msg '[class="^Alacritty$"] kill'
