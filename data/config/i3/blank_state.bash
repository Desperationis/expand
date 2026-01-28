#!/bin/bash
#
# blank_state.bash - Restore i3 to initial application state
#
# This script:
# 1. Moves initial applications back to their configured workspaces
# 2. Starts any missing initial applications
# 3. Moves other applications to available workspaces (sorted by PID ascending)
#

# ============================================================================
# CONFIGURATION - Add/modify initial applications here
# ============================================================================
# Format: "WM_CLASS:WORKSPACE:LAUNCH_COMMAND"
# WM_CLASS can be found with: xprop | grep CLASS (use the second value)
# WORKSPACE is the number (1-10)
# LAUNCH_COMMAND is the full path to launch the application

INITIAL_APPS=(
    "firefox-esr:1:/usr/bin/firefox"
    "Google-chrome:2:/usr/bin/google-chrome-stable"
    "discord:4:/usr/bin/discord"
)

# Maximum workspace number to use
MAX_WORKSPACE=10

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

# Get all window IDs and their classes from i3
get_all_windows() {
    i3-msg -t get_tree | jq -r '
        recurse(.nodes[]?, .floating_nodes[]?) |
        select(.window) |
        select(.window_properties.class) |
        select(.window_properties.class != "i3bar") |
        "\(.window):\(.window_properties.class)"
    '
}

# Get the PID for a window ID using xprop
get_window_pid() {
    local win_id="$1"
    xprop -id "$win_id" _NET_WM_PID 2>/dev/null | awk '{print $3}'
}

# Move a window to a workspace by window ID
move_window_to_workspace() {
    local win_id="$1"
    local workspace="$2"
    i3-msg "[id=$win_id] move container to workspace number $workspace" >/dev/null 2>&1
}

# Check if a window with given class exists
window_exists_with_class() {
    local class="$1"
    i3-msg -t get_tree | jq -e --arg class "$class" '
        recurse(.nodes[]?, .floating_nodes[]?) |
        select(.window_properties.class == $class) |
        .window
    ' >/dev/null 2>&1
}

# Get window ID by class (first match)
get_window_by_class() {
    local class="$1"
    i3-msg -t get_tree | jq -r --arg class "$class" '
        [recurse(.nodes[]?, .floating_nodes[]?) |
        select(.window_properties.class == $class) |
        .window] | first // empty
    '
}

# Get all window IDs for a class
get_all_windows_by_class() {
    local class="$1"
    i3-msg -t get_tree | jq -r --arg class "$class" '
        recurse(.nodes[]?, .floating_nodes[]?) |
        select(.window_properties.class == $class) |
        .window
    '
}

# ============================================================================
# MAIN LOGIC
# ============================================================================

echo "Restoring i3 to blank state..."

# Build list of reserved workspaces and class-to-workspace mapping
declare -A CLASS_TO_WORKSPACE
declare -A CLASS_TO_COMMAND
declare -a RESERVED_WORKSPACES=()

for entry in "${INITIAL_APPS[@]}"; do
    IFS=':' read -r class workspace command <<< "$entry"
    CLASS_TO_WORKSPACE["$class"]="$workspace"
    CLASS_TO_COMMAND["$class"]="$command"
    RESERVED_WORKSPACES+=("$workspace")
done

# Also handle case variations for chrome
CLASS_TO_WORKSPACE["google-chrome"]="2"

# Step 1 & 2: Handle initial applications
echo "Step 1/2: Moving/starting initial applications..."

for entry in "${INITIAL_APPS[@]}"; do
    IFS=':' read -r class workspace command <<< "$entry"

    # Check if app is running
    win_id=$(get_window_by_class "$class")

    if [[ -n "$win_id" ]]; then
        echo "  Moving $class to workspace $workspace"
        move_window_to_workspace "$win_id" "$workspace"
    else
        echo "  Starting $class (will go to workspace $workspace)"
        # Launch in background, i3 assign rules will place it correctly
        nohup $command >/dev/null 2>&1 &
        disown
    fi
done

# Small delay to let windows settle
sleep 0.5

# Step 3: Move other applications to available workspaces
echo "Step 3: Moving other applications to available workspaces..."

# Build list of all classes that are initial apps (for matching)
declare -A INITIAL_CLASSES
for entry in "${INITIAL_APPS[@]}"; do
    IFS=':' read -r class workspace command <<< "$entry"
    INITIAL_CLASSES["$class"]=1
done
# Add case variations
INITIAL_CLASSES["google-chrome"]=1

# Get all windows with their PIDs, excluding initial app classes
declare -a OTHER_WINDOWS=()

while IFS=: read -r win_id class; do
    [[ -z "$win_id" ]] && continue

    # Skip if this is an initial application class
    if [[ -n "${INITIAL_CLASSES[$class]}" ]]; then
        continue
    fi

    # Get PID for this window
    pid=$(get_window_pid "$win_id")
    [[ -z "$pid" ]] && pid=999999999  # Fallback for windows without PID

    OTHER_WINDOWS+=("$pid:$win_id:$class")
done < <(get_all_windows)

# Sort by PID ascending
IFS=$'\n' SORTED_WINDOWS=($(sort -t: -k1 -n <<< "${OTHER_WINDOWS[*]}"))
unset IFS

# Build list of available workspaces (not reserved by initial apps)
declare -a AVAILABLE_WORKSPACES=()
for ws in $(seq 1 $MAX_WORKSPACE); do
    is_reserved=0
    for reserved in "${RESERVED_WORKSPACES[@]}"; do
        if [[ "$ws" == "$reserved" ]]; then
            is_reserved=1
            break
        fi
    done
    if [[ $is_reserved -eq 0 ]]; then
        AVAILABLE_WORKSPACES+=("$ws")
    fi
done

# Move other windows to available workspaces
ws_index=0
for entry in "${SORTED_WINDOWS[@]}"; do
    [[ -z "$entry" ]] && continue

    IFS=':' read -r pid win_id class <<< "$entry"

    if [[ $ws_index -lt ${#AVAILABLE_WORKSPACES[@]} ]]; then
        target_ws="${AVAILABLE_WORKSPACES[$ws_index]}"
        echo "  Moving $class (PID: $pid) to workspace $target_ws"
        move_window_to_workspace "$win_id" "$target_ws"
        ((ws_index++))
    else
        echo "  Warning: No available workspace for $class (PID: $pid)"
    fi
done

# Focus workspace 1
i3-msg "workspace number 1" >/dev/null 2>&1

echo "Done! Initial apps: workspaces ${RESERVED_WORKSPACES[*]}"
echo "Other apps moved to: workspaces ${AVAILABLE_WORKSPACES[*]:0:$ws_index}"
