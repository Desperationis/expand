"""
Classes that test if the system has certain properties.
"""

import os
import platform
import subprocess
from abc import ABC, abstractmethod
from shutil import which


class CompatibilityProbe(ABC):
    @abstractmethod
    def get_error_message(self) -> str:
        pass

    @abstractmethod
    def is_compatible(self) -> bool:
        pass

# Used to be x86Probe
class AmdProbe(CompatibilityProbe):
    def get_error_message(self) -> str:
        return "Not on amd64."

    def is_compatible(self) -> bool:
        machine = platform.machine().lower()
        return machine in {'x86_64', 'amd64', 'x86', 'i386'}

class ArmProbe(CompatibilityProbe):
    def get_error_message(self) -> str:
        return "Not on arm."

    def is_compatible(self) -> bool:
        machine = platform.machine().lower()
        return machine in {'arm64', 'aarch64', 'armv7l', 'arm'}

# Used to be DebianProbe
class AptProbe(CompatibilityProbe):
    def get_error_message(self) -> str:
        return "apt doesn't exist"

    def is_compatible(self) -> bool:
        return which("apt") is not None


class WhichProbe(CompatibilityProbe):
    def __init__(self, command) -> None:
        self.command = command

    def get_error_message(self) -> str:
        return f"{self.command} is not installed."

    def is_compatible(self) -> bool:
        result = subprocess.run(
            f"which {self.command} > /dev/null 2>&1", shell=True, check=False
        )
        return result.returncode == 0


class ExistenceProbe(CompatibilityProbe):
    def __init__(self, path) -> None:
        self.path = os.path.expanduser(path)

    def get_error_message(self) -> str:
        return f"{self.path} does not exist."

    def is_compatible(self) -> bool:
        return os.path.exists(self.path)


class DisplayProbe(CompatibilityProbe):
    def get_error_message(self) -> str:
        return "No display/GUI detected."

    def is_compatible(self) -> bool:
        # Check if currently in a graphical session
        if os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY"):
            return True

        # Check if system has GUI capability (desktop sessions installed)
        session_dirs = ["/usr/share/xsessions", "/usr/share/wayland-sessions"]
        for session_dir in session_dirs:
            if os.path.isdir(session_dir) and os.listdir(session_dir):
                return True

        return False




