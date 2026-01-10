# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

`expand` is a TUI (curses-based) for running Ansible playbooks with dependency checking. It runs as root and allows installing packages/configs either globally or for a specific user.

## Commands

**Bootstrap and run:**
```bash
# Must run as root
. activate.sh        # or . activate.fish
python3 -m expand              # Install for root
python3 -m expand --user=john  # Install for specific user
```

**Run tests:**
```bash
pytest test.py
```

**Verbose mode (writes expand.log):**
```bash
python3 -m expand -v
```

## Architecture

### Core Components

- **`expand/curses_cli.py`**: Main UI loop. Draws categories/selections, handles keyboard input (vim keys supported), runs selected ansible playbooks via subprocess
- **`expand/expansion_card.py`**: Parses the special header format in ansible files to extract privilege level, compatibility probes, and description
- **`expand/probes.py`**: Compatibility checks (`AmdProbe`, `ArmProbe`, `AptProbe`, `WhichProbe`, `ExistenceProbe`) that determine if a playbook can run on the system
- **`expand/priviledge.py`**: Three privilege levels - `OnlyRoot`, `AnyUserNoEscalation`, `AnyUserEscalation`

### Ansible File Format

Every ansible file in `ansible/` must follow this header format (see `ansible/example.yaml`):
```yaml
# OnlyRoot() | AnyUserEscalation() | AnyUserNoEscalation()
# [AmdProbe(), AptProbe(), WhichProbe("bash"), ...]
# Description text here
#
# Additional description paragraphs

- name: "Playbook Name"
  hosts: localhost
  ...
```

Line 1: Privilege level class
Line 2: List of compatibility probes
Line 3+: Description (consecutive `#` lines)

### Directory Structure

- `ansible/`: Ansible playbooks organized by category (each subdirectory becomes a tab in the UI)
- `data/config/`: Configuration files copied by ansible playbooks
- `data/scripts/`: Shell scripts installed by ansible playbooks
