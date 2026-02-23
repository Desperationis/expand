"""
Classes that determine who can run ansible files.
"""

from abc import ABC

class PriviledgeLevel(ABC):
    pass


class OnlyRoot(PriviledgeLevel):
    """
    Only root can run this file.
    """
    pass

class AnyUserNoEscalation(PriviledgeLevel):
    """
    Run this script as a regular user without sudo priviledge.
    """
    pass

class AnyUserEscalation(PriviledgeLevel):
    """
    Run this script as root, but set all relevant environmental variables to
    that of any other user. This is useful when you need to install something
    to a specific user's home directory while making sure a set of global tools
    are installed.
    """
    pass

class AnyUserNoEscalationOnDarwin(PriviledgeLevel):
    """
    On Linux: behaves like OnlyRoot — only root can run or see this playbook.
    On macOS (Darwin): behaves like AnyUserNoEscalation — any user can see and
    run this playbook without privilege escalation. This is necessary because
    Homebrew refuses to run as root.
    """
    pass
