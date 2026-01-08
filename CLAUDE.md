# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

expand is a TUI application for running Ansible playbooks with an interactive menu interface. It provides categorized browsing, compatibility checking, privilege management, and installation status tracking.

## Running the Application

```bash
# Activate environment (required before running)
. activate.sh        # bash
. activate.fish      # fish

# Run as root
python3 -m expand

# Run as specific user
python3 -m expand --user=<username>

# Verbose logging
python3 -m expand --verbose
```

## Testing

```bash
python3 -m pytest test.py              # Run all tests
python3 -m pytest test.py::test_name   # Run specific test
```

## Architecture

### Core Modules

- `expand.py` - Main application logic, CLI argument parsing, privilege handling
- `curses_cli.py` - Terminal UI rendering and event loop
- `expansion_card.py` - Ansible file parser extracting metadata from YAML comments
- `gui_elements.py` - UI components (Choice, ChoicePreview)
- `probes.py` - Compatibility checking (AmdProbe, ArmProbe, AptProbe, WhichProbe, ExistenceProbe)
- `priviledge.py` - Privilege levels (OnlyRoot, AnyUserEscalation, AnyUserNoEscalation)
- `cache.py` - Installation status persistence (installed.json)

### Ansible Playbook Metadata Format

Playbooks in `ansible/` subdirectories use a specific comment format for expand to parse:

```yaml
# PrivilegeLevel()           # Line 1: OnlyRoot, AnyUserNoEscalation, or AnyUserEscalation
# [Probe1(), Probe2(), ...]  # Line 2: Compatibility probes list
# Description text           # Lines 3+: Multi-line description
# More description...
---
# Actual Ansible content follows
```

The privilege and probe lines are evaluated with `eval()`, allowing direct Python objects in playbook files.

### Probe System

All probes inherit from `CompatibilityProbe` with:
- `is_compatible()` - Returns boolean
- `get_error_message()` - Returns failure reason

Available probes: `AmdProbe`, `ArmProbe`, `AptProbe`, `WhichProbe(cmd)`, `ExistenceProbe(path)`

### Cache System

`installed.json` tracks installation status:
- OnlyRoot packages: tracked globally by package name
- AnyUser* packages: tracked per-user per package

### Privilege Model

- **OnlyRoot**: Must run as root (UID=0, EUID=0)
- **AnyUserNoEscalation**: Runs as current user without sudo
- **AnyUserEscalation**: Runs with root privileges but preserves user environment

User switching uses POSIX `setuid`/`setgid` directly rather than subprocess sudo.

## Dependencies

- Python 3.10+ (uses modern type hints)
- humanize, requests, docopt, ansible
- Linux/Unix environment (curses, pwd, grp modules)
