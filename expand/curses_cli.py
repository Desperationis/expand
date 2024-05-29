"""
This file is in charge of drawing the UI to the screen.
"""


import curses
from expand import util


class Choice:
    def __init__(self, name, file_path):
        self.name = name
        self.file_path = file_path
        self.chosen = False
        self.hover = False
        self.probes = util.get_probes_from_file(file_path)
        self.failing_probes = util.get_failing_probes(self.probes)
        self.broken_urls = self.failing_urls() if self.has_urls() else None

    def has_urls(self) -> bool:
        """
        Does this ansible file have any URL's in it?
        """
        with open(self.file_path, "r", encoding="UTF-8") as file:
            links = util.filter_str_for_urls(file.read())
            return len(links) > 0

    def failing_urls(self) -> list[str]:
        """
        If there are urls in this ansible file, get a list of URLs that aren't
        working. If there aren't, return an exception.
        """

        if not self.has_urls():
            raise Exception()

        broken_links = []

        with open(self.file_path, "r", encoding="UTF-8") as file:
            links = util.filter_str_for_urls(file.read())
            for link in links:
                if not util.is_url_up(link):
                    broken_links.append(link)

        return broken_links

    def set_chosen(self, chosen: bool):
        self.chosen = chosen

    def set_hover(self, hover: bool):
        self.hover = hover

    def draw(self, stdscr, y, x, width):
        columns = []

        columns.append("■ " if self.chosen else "☐ ")
        columns.append(self.name)

        if not self.has_urls():
            columns.append("")
        else:
            columns.append("✔" if len(self.broken_urls) == 0 else "✘")

        last_updated_delta = util.timedelta_since_last_update(self.file_path)
        last_updated = util.timedelta_pretty(last_updated_delta)
        columns.append(last_updated)

        if len(self.failing_probes) > 0:
            columns.append(self.failing_probes[0].get_error_message())
        else:
            columns.append("")

        columns = util.get_formatted_columns(columns, width, [2, 25, -1, -1, 50])
        for i, c in enumerate(columns):
            attrs = 0
            if i == 1 and self.hover:
                attrs |= curses.A_REVERSE
            if i == 4:
                attrs |= curses.color_pair(2)

            try:
                stdscr.addstr(y, x + c[1], c[0], attrs)
            except curses.error:
                pass


class curses_cli:
    def __init__(self) -> None:
        self.stdscr = curses.initscr()
        self.is_setup = False

    def setup(self):
        curses.noecho()
        curses.cbreak()
        curses.curs_set(0)
        curses.start_color()
        curses.use_default_colors()  # Without this color pair has no transparent background
        curses.set_escdelay(25)  # Without this there is a lag when pressing escape
        self.stdscr.keypad(True)

        curses.init_pair(1, curses.COLOR_CYAN, -1)
        curses.init_pair(2, curses.COLOR_RED, -1)

        self.is_setup = True

    def loop(self):
        if not self.is_setup:
            self.setup()

        files = util.get_files("ansible")
        display = list(map(lambda name: Choice(name, files[name]), files))

        selections = set()
        hover = 0

        while True:
            _, cols = self.stdscr.getmaxyx()

            self.stdscr.erase()
            self.stdscr.addstr(0, 0, "Please Select Packages:", 0)

            for i, elem in enumerate(display):
                elem.set_chosen(False)
                elem.set_hover(False)

                if i in selections or i == hover:
                    elem.set_chosen(True)

                if i == hover:
                    elem.set_hover(True)

                y = i + 5
                x = 5
                elem.draw(self.stdscr, y, x, cols - x - 5)

            c = self.stdscr.getch()
            if c == curses.KEY_UP or c == ord("k"):
                hover -= 1
            elif c == curses.KEY_DOWN or c == ord("j"):
                hover += 1
            elif c == 9:  # Tab
                if hover in selections:
                    selections.remove(hover)
                else:
                    selections.add(hover)
            hover %= len(display)

            self.stdscr.refresh()

    def end(self):
        curses.nocbreak()
        self.stdscr.keypad(False)
        curses.echo()
        curses.curs_set(1)
        curses.endwin()

        self.is_setup = False
