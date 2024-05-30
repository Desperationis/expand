"""
This file is in charge of drawing the UI to the screen.
"""


import curses
import threading
import subprocess
import os
import sys
import json
from expand import util
from expand.probes import CompatibilityProbe

class InstalledCache:
    @staticmethod
    def _get_json():
        if not os.path.exists("installed.json"):
            return {}

        with open("installed.json", "r", encoding="UTF-8") as file:
            return json.load(file)


    @staticmethod
    def _get_attr(attr):
        data = InstalledCache._get_json()
        return data[attr]

    @staticmethod
    def _write_attr(attr, value):
        data = InstalledCache._get_json()

        with open("installed.json", "w+", encoding="UTF-8") as file:
            data[attr] = value
            file.write(json.dumps(data, sort_keys=True, indent=4))


    @staticmethod
    def is_installed(name):
        try:
            return InstalledCache._get_attr(name) == "installed"
        except:
            return False


    @staticmethod
    def is_failure(name):
        try:
            return InstalledCache._get_attr(name) == "failure"
        except:
            return False

    @staticmethod
    def set_installed(ansible_name):
        InstalledCache._write_attr(ansible_name, "installed")

    @staticmethod
    def set_failure(ansible_name):
        InstalledCache._write_attr(ansible_name, "failure")

class ChoicePreview:
    """
    Shows a box that displays the description of a ansible file.
    """

    def __init__(self, name, file_path):
        self.name = name
        self.file_path = file_path


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

        # Draw Text
        with open(self.file_path, "r", encoding="UTF-8") as file:
            description = util.get_ansible_description(file.read(), width - 1 - 6)

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
        curses.init_pair(3, curses.COLOR_GREEN, -1)
        curses.init_pair(4, curses.COLOR_YELLOW, -1)

        self.is_setup = True

    def create_ansible_data_structure(self):
        categories = []

        files = util.get_files("ansible/packages/")
        display = list(map(lambda name: Choice(name, files[name]), files))
        categories.append(("packages", display))

        files = util.get_files("ansible/config/")
        display = list(map(lambda name: Choice(name, files[name]), files))
        categories.append(("config", display))

        return categories


    def loop(self):
        if not self.is_setup:
            self.setup()

        categories = self.create_ansible_data_structure()

        # Index of Current Category
        current_category = 0

        # For selection
        hover = 0
        selections = set()

        while True:
            current_display = categories[current_category][1]
            rows, cols = self.stdscr.getmaxyx()

            self.stdscr.erase()
            
            for i, elem in enumerate(categories):
                attrs = 0
                if i == current_category:
                    attrs |= curses.A_REVERSE

                self.stdscr.addstr(0, i * 10 + 3, elem[0], attrs)

            self.stdscr.addstr(3, 0, "Please Select", 0)

            for i, elem in enumerate(current_display):
                elem.set_chosen(False)
                elem.set_hover(False)

                if i in selections or i == hover:
                    elem.set_chosen(True)

                if i == hover:
                    elem.set_hover(True)

                y = i + 5
                x = 5
                elem.draw(self.stdscr, y, x, cols - x - 5)

            # 5 from offset of `Choice`, 3 for offset
            x = round(cols - (cols / 3))
            if x + 3 > Choice.MIN_WIDTH + 5:
                preview = ChoicePreview(current_display[hover].name, current_display[hover].file_path)
                preview.draw(self.stdscr, 0, x, cols - x, rows)

            c = self.stdscr.getch()
            if c == curses.KEY_UP or c == ord("k"):
                hover -= 1
            elif c == curses.KEY_DOWN or c == ord("j"):
                hover += 1
            elif c == curses.KEY_RIGHT or c == ord("l"):
                current_category += 1
                hover = 0
                selections.clear()
            elif c == curses.KEY_LEFT or c == ord("h"):
                current_category += 1
                hover = 0
                selections.clear()
            elif c == 9:  # Tab
                if hover in selections:
                    selections.remove(hover)
                else:
                    selections.add(hover)
            elif c == curses.KEY_ENTER or c == 10:
                self.end()

                # Run Playbooks
                for i in selections:
                    file_path = os.path.abspath(current_display[i].file_path)

                    p = subprocess.Popen(f"ansible-playbook \"{file_path}\"", shell=True)
                    p.wait()
                    if p.returncode != 0:
                        InstalledCache.set_failure(current_display[i].name)
                    else:
                        InstalledCache.set_installed(current_display[i].name)

                # Everything ran successfully, reset requirements
                categories = self.create_ansible_data_structure()
                selections.clear()

                self.setup()

            current_category %= len(categories)

            hover %= len(current_display)

            self.stdscr.refresh()

    def end(self):
        curses.nocbreak()
        self.stdscr.keypad(False)
        curses.echo()
        curses.curs_set(1)
        curses.endwin()

        self.is_setup = False
