import os 
import sys
import curses
import traceback
import time
from rich import print
import logging
from .components import *

"""
if "ACTIVATED_EXPAND" not in os.environ:
    print("[bold bright_red]Please run activate.sh as root first.[/bold bright_red]")
    sys.exit(1)
"""


logging.basicConfig(
    filename="expand.log",
    filemode="a",
    format="%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s",
    datefmt="%H:%M:%S",
    level=logging.DEBUG,
)


stdscr = curses.initscr()

def setup():
    curses.noecho()
    curses.cbreak()
    curses.curs_set(0)
    curses.start_color()
    curses.use_default_colors()  # Without this color pair has no transparent background
    curses.set_escdelay(25)  # Without this there is a lag when pressing escape
    stdscr.keypad(True)

    curses.init_pair(1, curses.COLOR_CYAN, -1)


def end():
    curses.nocbreak()
    stdscr.keypad(False)
    curses.echo()
    curses.curs_set(1)
    curses.endwin()



def main():
    error_str = ""

    try:
        setup()
        while True:
            stdscr.erase()

            # Draw HERE
            text = textcomponent("test", flags=textcomponent.TEXT_CENTERED)
            text.draw(stdscr)

            stdscr.refresh()



            time.sleep(1)


    except Exception as e:
        error_str = traceback.format_exc()

    finally:
        end()
        if len(error_str) > 0:
            logging.error(error_str)

