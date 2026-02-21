import os
import pwd
import curses
import threading
from expand import util
from expand.probes import CompatibilityProbe, InstalledProbe
from expand.failure_cache import FailureCache
from expand.colors import expand_color_palette
from expand.expansion_card import ExpansionCard
from expand.line_buffer import LineBuffer
from expand.priviledge import OnlyRoot, AnyUserEscalation, AnyUserNoEscalation, AnyUserNoEscalationOnDarwin
import platform

class ChoicePreview:
    """
    Shows a box that displays the description of a ansible file.
    """

    def __init__(self, name, file_path):
        self.name = name
        self.file_path = file_path
        self.expansion_card = ExpansionCard(file_path)

    def draw(self, stdscr, y, x, width, height):
        # Draw divider on left edge 
        for i in range(height):
            try:
                stdscr.addstr(y + i, x, "|", curses.A_BOLD)
            except curses.error:
                pass

        # Draw name of the file
        try:
            stdscr.addstr(y + 1, x + 3, self.name, curses.A_BOLD)
        except curses.error:
            pass

        # Draw Wrapped Text
        description = self.expansion_card.get_ansible_description(width - 1 - 6)
        for i, line in enumerate(description):
            try:
                stdscr.addstr(y + i + 3, x + 3, line, 0)
            except curses.error:
                pass




class Choice:
    # Columns arranged by index, second element is width. -1 for auto width
    ORDER = [
        ("select", 2),
        ("name", 22),
        ("URL", 2),
        ("priviledge", 21),
        ("installed", 15),
        ("compatibility", 35)
    ]

    def __init__(self, name, file_path):
        self.name = name
        self.file_path = file_path
        self.expansion_card = ExpansionCard(file_path)
        self.chosen = False
        self.hover = False

        # Load cache
        self.has_urls()
        self.failing_probes()
        self.failing_urls_task = threading.Thread(target=self.failing_urls)
        self.failing_urls_task.start()

    @staticmethod
    def get_min_width() -> int:
        widths = map(lambda c: c[1], Choice.ORDER)
        return sum(filter(lambda w: w > -1, widths))


    def has_urls(self) -> bool:
        """
        Does this ansible file have any URL's in it?
        """
        if hasattr(self, "_has_urls"):
            return self._has_urls

        with open(self.file_path, "r", encoding="UTF-8") as file:
            links = util.filter_str_for_urls(file.read())
            self._has_urls = len(links) > 0

        return self._has_urls

    def failing_urls(self) -> list[str]:
        """
        If there are urls in this ansible file, get a list of URLs that aren't
        working. If no files exist, return [].
        """
        if hasattr(self, "_broken_urls"):
            return self._broken_urls

        self._broken_urls = []

        with open(self.file_path, "r", encoding="UTF-8") as file:
            links = util.filter_str_for_urls(file.read())
            for link in links:
                if not util.is_url_up(link):
                    self._broken_urls.append(link)

        return self._broken_urls

    def failing_probes(self) -> list[CompatibilityProbe]:
        if hasattr(self, "_failing_probes"):
            return self._failing_probes

        self.probes = self.expansion_card.get_probes()
        self._failing_probes = util.get_failing_probes(self.probes)

        return self._failing_probes

    def installed_status(self) -> str:
        if hasattr(self, "_installed_status"):
            return self._installed_status

        # First check failure cache - if failed, return "Failure"
        if FailureCache.has_failed(self.name):
            self._installed_status = "Failure"
            return self._installed_status

        # Then run installed probes
        installed_probes = self.expansion_card.get_installed_probes()
        if len(installed_probes) == 0:
            # No probes defined, status is unknown
            self._installed_status = "Unknown"
        elif all(probe.is_installed() for probe in installed_probes):
            self._installed_status = "Installed"
        else:
            self._installed_status = "Not Installed"

        return self._installed_status

    def clear_installed_status(self):
        """Clear cached installed status to force re-evaluation."""
        if hasattr(self, "_installed_status"):
            delattr(self, "_installed_status")


    def set_chosen(self, chosen: bool):
        self.chosen = chosen

    def set_hover(self, hover: bool):
        self.hover = hover

    def draw(self, stdscr, y, x, width):
        data = {}

        data["select"] = ("■ " if self.chosen else "☐ "), "NORMAL"
            
        data["name"] = self.name, "NORMAL"

        # Add URL Indictor
        if not self.has_urls():
            data["URL"] = "", "NORMAL"
        elif self.failing_urls_task.is_alive():
            data["URL"] = "-", "YELLOW"
        elif len(self.failing_urls()) != 0:
            data["URL"] = "✘", "RED"
        else:
            data["URL"] = "✔", "GREEN"

        # If package was able to be installed or not
        status = self.installed_status()
        if status == "Failure":
            data["installed"] = status, "RED"
        elif status == "Installed":
            data["installed"] = status, "GREEN"
        elif status == "Unknown":
            data["installed"] = status, "NORMAL"
        else:
            data["installed"] = status, "YELLOW"

        level = self.expansion_card.get_priviledge_level()
        if isinstance(level, OnlyRoot):
            if os.getuid() != 0:
                data["priviledge"] = "OnlyRoot", "RED"
            else:
                data["priviledge"] = "OnlyRoot", "GREEN"
        elif isinstance(level, AnyUserNoEscalation):
            data["priviledge"] = "AnyUserNoEscalation", "GREEN"
        elif isinstance(level, AnyUserEscalation):
            if os.geteuid() != 0:
                data["priviledge"] = "AnyUserEscalation", "RED"
            else:
                data["priviledge"] = "AnyUserEscalation", "YELLOW"
        elif isinstance(level, AnyUserNoEscalationOnDarwin):
            if platform.system() == "Darwin":
                if os.getuid() == 0:
                    data["priviledge"] = "AnyUserNoEscalation", "RED"
                else:
                    data["priviledge"] = "AnyUserNoEscalation", "GREEN"
            else:
                if os.getuid() != 0:
                    data["priviledge"] = "OnlyRoot", "RED"
                else:
                    data["priviledge"] = "OnlyRoot", "GREEN"
        else:
            raise Exception(f"Unknown Priviledge: {level}")

        # Add Message of Any Failing Probes
        data["compatibility"] = "", "GREEN"
        if len(self.failing_probes()) > 0:
            data["compatibility"] = self.failing_probes()[0].get_error_message(), "RED"

        # Crop Data to Column Sizes
        columns = [ data[name][0] for name, _ in Choice.ORDER ]
        widths = map(lambda c: c[1], Choice.ORDER)
        columns = util.get_formatted_columns(columns, width, list(widths))

        for i, c in enumerate(columns):
            column_name = Choice.ORDER[i][0]
            column_color = data[column_name][1]
            attrs = expand_color_palette[column_color]

            if self.hover:
                attrs |= curses.A_REVERSE

            try:
                stdscr.addstr(y, x + c[1], c[0], attrs)
            except curses.error:
                pass


class OutputPanel:
    """
    Full-screen panel that displays streaming output from a subprocess.
    Owns a LineBuffer and draws it to the curses screen with a title,
    divider, scrollable output area, and a status bar.
    """

    def __init__(self, title):
        self.title = title
        self.buffer = LineBuffer()
        self.status_text = "Running..."
        self.status_color = "YELLOW"

    def append(self, line):
        self.buffer.append(util.strip_ansi(line))

    def set_status(self, text, color):
        self.status_text = text
        self.status_color = color

    def draw(self, stdscr, rows, cols, scroll_offset):
        # Row 0: bold title
        try:
            stdscr.addstr(0, 0, self.title[:cols], curses.A_BOLD)
        except curses.error:
            pass

        # Row 1: horizontal divider
        try:
            stdscr.addstr(1, 0, "\u2500" * cols, 0)
        except curses.error:
            pass

        # Rows 2..(rows-2): output lines from buffer
        content_height = max(0, rows - 3)
        visible = self.buffer.get_visible(content_height, scroll_offset)
        for i, line in enumerate(visible):
            try:
                stdscr.addstr(2 + i, 0, line[:cols], 0)
            except curses.error:
                pass

        # Row (rows-1): status bar
        try:
            attrs = expand_color_palette.get(self.status_color, 0)
            stdscr.addstr(rows - 1, 0, self.status_text[:cols], attrs | curses.A_BOLD)
        except curses.error:
            pass

