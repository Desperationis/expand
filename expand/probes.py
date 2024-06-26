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


class LinuxProbe(CompatibilityProbe):
    def get_error_message(self) -> str:
        return "Not on Linux System."

    def is_compatible(self) -> bool:
        return platform.system() == "Linux"


class x86Probe(CompatibilityProbe):
    def get_error_message(self) -> str:
        return "Not on x86."

    def is_compatible(self) -> bool:
        return platform.system() == "Linux"


class DebianProbe(CompatibilityProbe):
    def get_error_message(self) -> str:
        return "Not Debian based."

    def is_compatible(self) -> bool:
        return which("apt") is not None


class NotInDockerProbe(CompatibilityProbe):
    def get_error_message(self) -> str:
        return "This is a Docker container."

    def is_compatible(self) -> bool:
        # Detects Docker
        # https://stackoverflow.com/questions/43878953/how-does-one-detect-if-one-is-running-within-a-docker-container-within-python
        def text_in_file(text, filename):
            try:
                with open(filename, encoding="utf-8") as lines:
                    return any(text in line for line in lines)
            except OSError:
                return False

        cgroup = "/proc/self/cgroup"
        return not (os.path.exists("/.dockerenv") or text_in_file("docker", cgroup))


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




