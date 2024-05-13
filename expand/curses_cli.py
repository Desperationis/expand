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

        while True:
            self.stdscr.erase()

            # Draw HERE
            text = textcomponent("test", flags=textcomponent.TEXT_CENTERED)
            text.draw(self.stdscr)

            self.stdscr.refresh()


            time.sleep(1)



    def end(self):
        curses.nocbreak()
        self.stdscr.keypad(False)
        curses.echo()
        curses.curs_set(1)
        curses.endwin()

        self.is_setup = False


