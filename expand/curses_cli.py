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
            # THIS IS ONLY TO MAKE FAKE DATA
            tmp = []
            for i in range(1, 7):
                for c in choices:
                    tmp.append(f"{i}_{c.split('.')[0]}.yaml")

            choices += tmp

            return choices

        # choices = list(map(lambda a: textcomponent(a[1], rect=brect(0, a[0], len(a[1]), 1), flags=textcomponent.ALIGN_H_MIDDLE), enumerate(gen_fake_data())))

        while True:
            self.stdscr.erase()

            # We keep making new groups to catch window resizes
            rows, cols = self.stdscr.getmaxyx()
            root_container = Container("root", brect(0, 0, cols, rows))
            sub_container = Container("sub", brect(100, 100, cols // 4, rows // 4))
            root_container.add_child("sub")
            TextComponent(
                "text1",
                "hi there",
                flags=(TextComponent.ALIGN_H_MIDDLE | TextComponent.ALIGN_V_TOP),
            )
            sub_container.add_child("text1")

            offset = brect.calculate_alignment_offset(
                sub_container.rect, root_container.rect, (0, 1)
            )
            sub_container.rect.x += offset[0]
            sub_container.rect.y += offset[1]
            PubSub.invoke_to(ParentBRectMessage("sub", sub_container.rect), "text1")

            """
            group = groupcomponent(brect(0, 0, cols, rows))
            for i, text in enumerate(choices):
                copy = text.copy()
                if i == cursor:
                    copy.flags |= textcomponent.REVERSE
                group.add(copy)


            logging.debug(group.components)
            group.draw(self.stdscr)
            """

            PubSub.invoke_to(DrawMessage("root", self.stdscr), "root")

            c = self.stdscr.getch()
            """
            if c == curses.KEY_UP or c == ord("k"):
                increment_cursor(-1)
            elif c == curses.KEY_DOWN or c == ord("j"):
                increment_cursor(1)
            """

            root_container.destroy()

            self.stdscr.refresh()

    def end(self):
        curses.nocbreak()
        self.stdscr.keypad(False)
        curses.echo()
        curses.curs_set(1)
        curses.endwin()

        self.is_setup = False
