import os
import json


def list_presets(presets_dir):
    """Return a sorted list of preset names (filenames without .json) in presets_dir."""
    if not os.path.isdir(presets_dir):
        return []
    return sorted(
        os.path.splitext(f)[0]
        for f in os.listdir(presets_dir)
        if f.endswith(".json")
    )


def load_preset_file(preset_name, presets_dir):
    """Load and return a preset dict from presets_dir/<preset_name>.json.

    Raises FileNotFoundError if the file doesn't exist.
    Raises ValueError if JSON is invalid or missing required "packages" key.
    """
    path = os.path.join(presets_dir, preset_name + ".json")
    with open(path) as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in {path}: {e}")
    if "packages" not in data:
        raise ValueError(f"Preset file {path} missing required 'packages' key")
    return data


def resolve_preset_selections(preset_packages, categories, should_hide_fn):
    """Resolve preset package names into a set of package_select objects.

    Args:
        preset_packages: list of package filenames (e.g. ["fish.yaml", "git.yaml"])
        categories: list[tuple[str, list[Choice]]] — the categories data structure
        should_hide_fn: callable(choice) -> bool — visibility filter

    Returns:
        set of package_select objects for visible, matching packages.
    """
    from expand.curses_cli import package_select

    selections = set()
    for pkg_name in preset_packages:
        for cat_idx, (_, choices) in enumerate(categories):
            for choice_idx, choice in enumerate(choices):
                if choice.name == pkg_name:
                    if not should_hide_fn(choice):
                        selections.add(package_select(cat_idx, choice_idx))
                    break
    return selections


def load_and_resolve_preset(preset_name, presets_dir, categories, should_hide_fn):
    """Load a preset file and resolve its packages into selections.

    Combines load_preset_file + resolve_preset_selections into a single call.
    Returns set of package_select. Propagates exceptions from load_preset_file.
    """
    data = load_preset_file(preset_name, presets_dir)
    return resolve_preset_selections(data["packages"], categories, should_hide_fn)


def export_installed_preset(preset_name, workers=4):
    """Scan all ansible packages, detect which are installed, and write a preset file.

    Writes to presets/<preset_name>.json with all packages whose installed probes
    report "Installed".
    """
    from concurrent.futures import ThreadPoolExecutor
    from expand.gui_elements import Choice
    from expand import util

    base_dir = "ansible/"
    presets_dir = "presets"

    # Build the same data structure the TUI uses
    all_choices = []
    for entry in sorted(os.scandir(base_dir), key=lambda e: e.name):
        if entry.is_dir() and not entry.name.startswith('.'):
            dir_path = os.path.join(base_dir, entry.name)
            files = util.get_files(dir_path)
            for name, file_path in files.items():
                all_choices.append(Choice(name, file_path))

    # Precompute installed statuses in parallel
    print(f"Checking installed status of {len(all_choices)} packages...")
    with ThreadPoolExecutor(max_workers=workers) as executor:
        executor.map(lambda c: c.installed_status(), all_choices)

    # Collect packages that are detected as installed
    installed = sorted(
        c.name for c in all_choices if c.installed_status() == "Installed"
    )

    # Write preset file
    os.makedirs(presets_dir, exist_ok=True)
    out_path = os.path.join(presets_dir, preset_name + ".json")
    data = {"name": preset_name, "packages": installed}
    with open(out_path, "w") as f:
        json.dump(data, f, indent=2)
        f.write("\n")

    print(f"Exported {len(installed)} installed packages to {out_path}")
