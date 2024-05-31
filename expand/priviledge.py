"""
Classes that determine who can run ansible files.
"""

from abc import ABC, abstractmethod

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
    Run this script as a regular user BUT with EUID == 0. This is useful in
    cases where you need access to the user's environmental variables but need
    sudo access. Use this only when strictly necessary.
    """
    pass
