from abc import ABC, abstractmethod
import platform
import os
import sys
import subprocess
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
        return platform.system() == 'Linux'

class x86Probe(CompatibilityProbe):
    def get_error_message(self) -> str:
        return "Not on x86."

    def is_compatible(self) -> bool:
        return platform.system() == 'Linux'

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
                with open(filename, encoding='utf-8') as lines:
                    return any(text in line for line in lines)
            except OSError:
                return False
        cgroup = '/proc/self/cgroup'
        return not (os.path.exists('/.dockerenv') or text_in_file('docker', cgroup))

class PopOSProbe(CompatibilityProbe):
    def get_error_message(self) -> str:
        return "This is not PopOS."

    def is_compatible(self) -> bool:
        try:
            with open('/etc/os-release', 'r') as f:
                for line in f:
                    if line.startswith('ID='):
                        _, value = line.strip().split('=')
                        return value.strip('"') == 'pop'
            return False
        except FileNotFoundError:
            return False

class NotRootProbe(CompatibilityProbe):
    def get_error_message(self) -> str:
        return "You cannot run this as root."

    def is_compatible(self) -> bool:
        return os.geteuid() != 0

class DockerInstalledProbe(CompatibilityProbe):
    def get_error_message(self) -> str:
        return "docker is not installed."

    def is_compatible(self) -> bool:
        result = subprocess.run("which docker > /dev/null 2>&1", shell=True, check=False)
        return result.returncode == 0

class FishInstalledProbe(CompatibilityProbe):
    def get_error_message(self) -> str:
        return "fish is not installed."

    def is_compatible(self) -> bool:
        result = subprocess.run("which fish > /dev/null 2>&1", shell=True, check=False)
        return result.returncode == 0


