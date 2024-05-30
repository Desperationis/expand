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
    SIZES = [2, 25, 2, 25, 15, 35]
    MIN_WIDTH = sum(filter(lambda a: a > -1, SIZES))

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
        colors = {}
        data = {}

        data["select"] = ("■ " if self.chosen else "☐ ")
        colors["select"] = expand_color_palette["NORMAL"]
            
        data["name"] = self.name
        colors["name"] = expand_color_palette["NORMAL"]

        # Add URL Indictor
        if not self.has_urls():
            data["URL"] = ""
            colors["URL"] = expand_color_palette["NORMAL"]
        elif self.failing_urls_task.is_alive():
            data["URL"] = "-"
            colors["URL"] = expand_color_palette["YELLOW"]
        elif len(self.failing_urls()) != 0:
            data["URL"] = "✘"
            colors["URL"] = expand_color_palette["RED"]
        else:
            data["URL"] = "✔"
            colors["URL"] = expand_color_palette["GREEN"]

        # Add Last Updated
        last_updated_delta = util.timedelta_since_last_update(self.file_path)
        last_updated = util.timedelta_pretty(last_updated_delta)
        data["last_updated"] = last_updated
        colors["last_updated"] = expand_color_palette["CYAN"]

        # If package was able to be installed or not
        data["installed"] = self.installed_status()
        if self.installed_status() == "Failure":
            colors["installed"] = expand_color_palette["RED"]
        elif self.installed_status() == "Installed":
            colors["installed"] = expand_color_palette["GREEN"]
        else:
            colors["installed"] = expand_color_palette["YELLOW"]

        # Add Message of Any Failing Probes
        data["compatibility"] = ""
        colors["compatibility"] = expand_color_palette["RED"]
        if len(self.failing_probes()) > 0:
            data["compatibility"] = self.failing_probes()[0].get_error_message()

        columns = [ data["select"], data["name"], data["URL"], data["last_updated"], data["installed"], data["compatibility"] ]

        # Select, Name, URL, Last Updated, Failing Message
        columns = util.get_formatted_columns(columns, width, Choice.SIZES)
        for i, c in enumerate(columns):
            attrs = 0
            if self.hover:
                attrs |= curses.A_REVERSE

            if i == 0:
                attrs |= colors["select"]
            if i == 1:
                attrs |= colors["name"]
            if i == 2:
                attrs |= colors["URL"]
            if i == 3:
                attrs |= colors["last_updated"]
            if i == 4:
                attrs |= colors["installed"]
            if i == 5:
                attrs |= colors["compatibility"]

            try:
                stdscr.addstr(y, x + c[1], c[0], attrs)
            except curses.error:
                pass




