import os
import json

class FailureCache:
    """
    Tracks recent installation failures. This is a simplified cache that only
    remembers packages that failed to install, not successful installations.

    The format for the cache file (failures.json) is:
        {
            "failures": ["package1.yaml", "package2.yaml", ...]
        }

    Real-time probes detect installed software; this cache only overlays
    failure information on top.
    """

    CACHE_FILE = "failures.json"

    @staticmethod
    def _get_json() -> dict:
        if not os.path.exists(FailureCache.CACHE_FILE):
            return {"failures": []}

        try:
            with open(FailureCache.CACHE_FILE, "r", encoding="UTF-8") as file:
                data = json.load(file)
        except (json.JSONDecodeError, ValueError):
            return {"failures": []}
        # Ensure failures key exists
        if "failures" not in data:
            data["failures"] = []
        return data

    @staticmethod
    def _write_json(data: dict):
        with open(FailureCache.CACHE_FILE, "w+", encoding="UTF-8") as file:
            file.write(json.dumps(data, sort_keys=True, indent=4))

    @staticmethod
    def has_failed(package_name: str) -> bool:
        """Return True if the package has a recorded failure."""
        data = FailureCache._get_json()
        return package_name in data["failures"]

    @staticmethod
    def set_failed(package_name: str):
        """Record that a package failed to install."""
        data = FailureCache._get_json()
        if package_name not in data["failures"]:
            data["failures"].append(package_name)
            FailureCache._write_json(data)

    @staticmethod
    def clear_failed(package_name: str):
        """Clear failure status for a package (called on successful install)."""
        data = FailureCache._get_json()
        if package_name in data["failures"]:
            data["failures"].remove(package_name)
            FailureCache._write_json(data)
