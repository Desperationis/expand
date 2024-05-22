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

        text = textcomponent("theisistEncharacterslong", rect=brect(0,0,10,10), flags=textcomponent.BOLD, color=curses.color_pair(1))
        group = groupcomponent(brect(10, 10, 50, 5))
        group.add(text)

        while True:
            self.stdscr.erase()

            text.draw(self.stdscr)

            c = self.stdscr.getch()
            text.handleinput(c) 

            self.stdscr.refresh()





    def end(self):
        curses.nocbreak()
        self.stdscr.keypad(False)
        curses.echo()
        curses.curs_set(1)
        curses.endwin()

        self.is_setup = False


