import curses
import threading
from expand import util
from expand.probes import CompatibilityProbe
from expand.cache import InstalledCache

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
        self.failing_urls_task = threading.Thread(target=self.run_failing_urls)
        self.failing_urls_task.start()

    def run_failing_urls(self):
        return self.failing_urls()


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
        columns = []

        # Add Select
        columns.append("■ " if self.chosen else "☐ ")

        # Add name of file
        columns.append(self.name)

        # Add URL Indictor
        if not self.has_urls():
            columns.append("")
        elif self.failing_urls_task.is_alive():
            columns.append("-")
        else:
            if len(self.failing_urls()) == 0:
                columns.append("✔")
            else:
                columns.append("✘")

        # Add Last Updated
        last_updated_delta = util.timedelta_since_last_update(self.file_path)
        last_updated = util.timedelta_pretty(last_updated_delta)
        columns.append(last_updated)

        # If package was able to be installed or not
        columns.append(self.installed_status())

        # Add Message of Any Failing Probes
        if len(self.failing_probes()) > 0:
            columns.append(self.failing_probes()[0].get_error_message())
        else:
            columns.append("")

        # Select, Name, URL, Last Updated, Failing Message
        columns = util.get_formatted_columns(columns, width, Choice.SIZES)
        for i, c in enumerate(columns):
            attrs = 0
            if self.hover:
                attrs |= curses.A_REVERSE
            if i == 2:
                if self.failing_urls_task.is_alive():
                    attrs |= curses.color_pair(4) # Yellow
                elif len(self.failing_urls()) == 0:
                    attrs |= curses.color_pair(3) # Green
                else:
                    attrs |= curses.color_pair(2) # Red

            if i == 4:
                if self.installed_status() == "Not Installed":
                    attrs |= curses.color_pair(4) # Yellow
                elif self.installed_status() == "Installed":
                    attrs |= curses.color_pair(3) # Green
                elif self.installed_status() == "Failure":
                    attrs |= curses.color_pair(2) # Red
                    
            if i == 5:
                attrs |= curses.color_pair(2) # Red

            try:
                stdscr.addstr(y, x + c[1], c[0], attrs)
            except curses.error:
                pass




