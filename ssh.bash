#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ARCHIVE="$SCRIPT_DIR/data/ssh/ssh.tar.age"

if ! command -v age &> /dev/null; then
    echo "Error: age is not installed. Install it first (e.g. via expand's age.yaml)."
    exit 1
fi

if [ ! -d "$HOME/.ssh" ]; then
    echo "Error: ~/.ssh does not exist."
    exit 1
fi

TMPDIR="$(mktemp -d)"
trap 'rm -rf "$TMPDIR"' EXIT

tar -cf "$TMPDIR/ssh.tar" -C "$HOME" .ssh
age -p -o "$ARCHIVE" "$TMPDIR/ssh.tar"

echo "Encrypted ~/.ssh to $ARCHIVE"
