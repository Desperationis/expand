"""
This file is in charge of drawing the UI to the screen.
"""


import curses
import subprocess
import os
from expand import util
from expand.cache import InstalledCache
from expand.gui_elements import ChoicePreview, Choice


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
