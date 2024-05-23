import curses
import time
from .components import *

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

        self.is_setup = True


    def loop(self):
        if not self.is_setup:
            self.setup()


        def gen_fake_data():
            choices = [
                    "alacritty.yaml",
                    "nvim.yaml",
                    "installcomputer.yaml",
                    "supercool.yaml",
                ]
            #THIS IS ONLY TO MAKE FAKE DATA
            tmp = []
            for i in range(1, 7):
                for c in choices:
                    tmp.append(f"{i}_{c.split('.')[0]}.yaml")
               
            choices += tmp

            return choices

        choices = list(map(lambda a: textcomponent(a[1], rect=brect(0, a[0], len(a[1]), 1), flags=textcomponent.ALIGN_H_MIDDLE), enumerate(gen_fake_data())))

        cursor = 0
        def increment_cursor(amount):
            nonlocal cursor
            cursor += amount
            cursor %= len(choices)

        while True:
            self.stdscr.erase()

            # We keep making new groups to catch window resizes
            rows, cols = self.stdscr.getmaxyx()
            group = groupcomponent(brect(0, 0, cols, rows))
            for i, text in enumerate(choices):
                copy = text.copy()
                if i == cursor:
                    copy.flags |= textcomponent.REVERSE
                group.add(copy)


            logging.debug(group.components)
            group.draw(self.stdscr)

            c = self.stdscr.getch()
            if c == curses.KEY_UP or c == ord("k"):
                increment_cursor(-1)
            elif c == curses.KEY_DOWN or c == ord("j"):
                increment_cursor(1)

            self.stdscr.refresh()





    def end(self):
        curses.nocbreak()
        self.stdscr.keypad(False)
        curses.echo()
        curses.curs_set(1)
        curses.endwin()

        self.is_setup = False


