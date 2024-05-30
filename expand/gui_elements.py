import curses
import threading
from expand import util
from expand.probes import CompatibilityProbe
from expand.cache import InstalledCache
from expand.colors import expand_color_palette

class ChoicePreview:
    """
    Shows a box that displays the description of a ansible file.
    """

    def __init__(self, name, file_path):
        self.name = name
        self.file_path = file_path

        with open(self.file_path, "r", encoding="UTF-8") as file:
            self.content = file.read()


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
        description = util.get_ansible_description(self.content, width - 1 - 6)
        for i, line in enumerate(description):
            try:
                stdscr.addstr(y + i + 3, x + 3, line, 0)
            except curses.error:
                pass




class Choice:
    # Columns arranged by index, second element is width. -1 for auto width
    ORDER = [
        ("select", 2),
        ("name", 25),
        ("URL", 2),
        ("installed", 15),
        ("compatibility", 35)
    ]

    def __init__(self, name, file_path):
        self.name = name
        self.file_path = file_path
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

        self.probes = util.get_probes_from_file(self.file_path)
        self._failing_probes = util.get_failing_probes(self.probes)

        return self._failing_probes

    def installed_status(self) -> str:
        if hasattr(self, "_installed_status"):
            return self._installed_status

        if InstalledCache.is_failure(self.name):
            self._installed_status = "Failure"
        elif InstalledCache.is_installed(self.name):
            self._installed_status = "Installed"
        else:
            self._installed_status = "Not Installed"

        return self._installed_status


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
        if self.installed_status() == "Failure":
            data["installed"] = self.installed_status(), "RED"
        elif self.installed_status() == "Installed":
            data["installed"] = self.installed_status(), "GREEN"
        else:
            data["installed"] = self.installed_status(), "YELLOW"

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




