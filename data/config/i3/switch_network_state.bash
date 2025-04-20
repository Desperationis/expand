#!/bin/bash

STATE_FILE="$HOME/.network_toggle_state"

# Read current state
if [[ ! -f "$STATE_FILE" ]]; then
    CURRENT_STATE=0
else
    CURRENT_STATE=$(<"$STATE_FILE")
fi

NEW_STATE=$(( (CURRENT_STATE + 1) % 3 ))

case $NEW_STATE in
    0)
        nmcli radio wifi off
        mapfile -t ETH_DEVICES < <(nmcli -t -f DEVICE,TYPE dev | grep ':ethernet$' | cut -d: -f1)
        for dev in "${ETH_DEVICES[@]}"; do
            nmcli device set "$dev" managed yes
            nmcli device connect "$dev" &>/dev/null
        done
        echo "Ethernet Only"
        ;;
    1)
        nmcli radio wifi on
        mapfile -t ETH_DEVICES < <(nmcli -t -f DEVICE,TYPE dev | grep ':ethernet$' | cut -d: -f1)
        for dev in "${ETH_DEVICES[@]}"; do
            nmcli device disconnect "$dev" &>/dev/null
            nmcli device set "$dev" managed no
        done
        echo "WiFi Only"
        ;;
    2)
        nmcli radio wifi on
        mapfile -t ETH_DEVICES < <(nmcli -t -f DEVICE,TYPE dev | grep ':ethernet$' | cut -d: -f1)
        for dev in "${ETH_DEVICES[@]}"; do
            nmcli device set "$dev" managed yes
            nmcli device connect "$dev" &>/dev/null
        done
        echo "Both Enabled"
        ;;
esac

echo "$NEW_STATE" > "$STATE_FILE"

