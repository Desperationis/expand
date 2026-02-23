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

# Used to be DebianProbe
class AptProbe(CompatibilityProbe):
    def get_error_message(self) -> str:
        return "apt doesn't exist"

    def is_compatible(self) -> bool:
        return which("apt") is not None


class BrewProbe(CompatibilityProbe):
    def get_error_message(self) -> str:
        return "brew doesn't exist"

    def is_compatible(self) -> bool:
        return which("brew") is not None


class DarwinProbe(CompatibilityProbe):
    def get_error_message(self) -> str:
        return "Not on macOS."

    def is_compatible(self) -> bool:
        return platform.system() == "Darwin"


class LinuxProbe(CompatibilityProbe):
    def get_error_message(self) -> str:
        return "Not on Linux."

    def is_compatible(self) -> bool:
        return platform.system() == "Linux"


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


class DisplayProbe(CompatibilityProbe):
    def get_error_message(self) -> str:
        return "No display/GUI detected."

    def is_compatible(self) -> bool:
        # macOS always has a display
        if platform.system() == "Darwin":
            return True

        # Check if currently in a graphical session
        if os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY"):
            return True

        # Check if system has GUI capability (desktop sessions installed)
        session_dirs = ["/usr/share/xsessions", "/usr/share/wayland-sessions"]
        for session_dir in session_dirs:
            if os.path.isdir(session_dir) and os.listdir(session_dir):
                return True

        return False


# =============================================================================
# InstalledProbe classes - Real-time detection of installed software
# =============================================================================

class InstalledProbe(ABC):
    """Abstract base class for probes that detect if software is installed."""

    @abstractmethod
    def is_installed(self) -> bool:
        """Return True if the software is detected as installed."""
        pass


class CommandProbe(InstalledProbe):
    """Check if a command exists in PATH."""

    def __init__(self, command: str) -> None:
        self.command = command

    def is_installed(self) -> bool:
        return which(self.command) is not None


class FileProbe(InstalledProbe):
    """Check if a file or directory exists. Supports glob patterns."""

    def __init__(self, path: str) -> None:
        self.path = os.path.expanduser(path)

    def is_installed(self) -> bool:
        import glob
        return len(glob.glob(self.path)) > 0


class AptPackageProbe(InstalledProbe):
    """Check if an apt package is installed."""

    def __init__(self, package: str) -> None:
        self.package = package

    def is_installed(self) -> bool:
        result = subprocess.run(
            ["dpkg", "-s", self.package],
            capture_output=True,
            check=False
        )
        return result.returncode == 0


class BrewPackageProbe(InstalledProbe):
    """Check if a Homebrew package is installed (formula or cask)."""

    def __init__(self, package: str) -> None:
        self.package = package

    def is_installed(self) -> bool:
        result = subprocess.run(
            ["brew", "list", "--formula", self.package],
            capture_output=True,
            check=False
        )
        if result.returncode == 0:
            return True
        result = subprocess.run(
            ["brew", "list", "--cask", self.package],
            capture_output=True,
            check=False
        )
        return result.returncode == 0


class PipxProbe(InstalledProbe):
    """Check if a pipx package is installed."""

    def __init__(self, package: str) -> None:
        self.package = package

    def is_installed(self) -> bool:
        result = subprocess.run(
            ["pipx", "list", "--short"],
            capture_output=True,
            text=True,
            check=False
        )
        if result.returncode != 0:
            return False
        # pipx list --short outputs "package version" per line
        for line in result.stdout.splitlines():
            parts = line.split()
            if parts and parts[0] == self.package:
                return True
        return False


class GroupMemberProbe(InstalledProbe):
    """Check if the current user is a member of a group."""

    def __init__(self, group: str) -> None:
        self.group = group

    def is_installed(self) -> bool:
        import grp
        import pwd
        try:
            user = pwd.getpwuid(os.getuid()).pw_name
            group_info = grp.getgrnam(self.group)
            return user in group_info.gr_mem or group_info.gr_gid == os.getgid()
        except KeyError:
            return False


class AllProbes(InstalledProbe):
    """All probes must pass for is_installed to return True."""

    def __init__(self, probes: list) -> None:
        self.probes = probes

    def is_installed(self) -> bool:
        return all(probe.is_installed() for probe in self.probes)


class AnyProbes(InstalledProbe):
    """Any probe passing makes is_installed return True."""

    def __init__(self, probes: list) -> None:
        self.probes = probes

    def is_installed(self) -> bool:
        return any(probe.is_installed() for probe in self.probes)


class FileMatchProbe(InstalledProbe):
    """Check if a deployed file exactly matches its source in the repo."""

    _project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    def __init__(self, source: str, dest: str) -> None:
        self.source = os.path.join(self._project_root, source)
        self.dest = os.path.expanduser(dest)

    def is_installed(self) -> bool:
        if not os.path.isfile(self.dest):
            return False
        try:
            with open(self.source, "rb") as sf, open(self.dest, "rb") as df:
                return sf.read() == df.read()
        except (IOError, OSError):
            return False



class GrepProbe(InstalledProbe):
    """Check if a pattern exists in a file."""

    def __init__(self, path: str, pattern: str) -> None:
        self.path = os.path.expanduser(path)
        self.pattern = pattern

    def is_installed(self) -> bool:
        if not os.path.exists(self.path):
            return False
        try:
            with open(self.path, "r", encoding="UTF-8") as f:
                return self.pattern in f.read()
        except (IOError, UnicodeDecodeError):
            return False




