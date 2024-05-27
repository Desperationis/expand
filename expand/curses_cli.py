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

            # We keep making new groups to catch window resizes
            rows, cols = self.stdscr.getmaxyx()
            root_container = Container("root", brect(0, 0, cols, rows))
            sub_container = Container("sub", brect(100, 100, cols // 4, rows // 4))
            root_container.add_child("sub")
            TextComponent(
                "text1",
                "hi there cutie patotie",
                flags=(TextComponent.ALIGN_H_MIDDLE | TextComponent.ALIGN_V_TOP),
            )
            TextComponent(
                "text2",
                "HEHEHEHEHEHE",
                flags=(TextComponent.ALIGN_H_MIDDLE),
            )
            TextComponent(
                "text3",
                "HAHAHAHAHHAHAH",
                flags=(TextComponent.ALIGN_H_MIDDLE),
            )
            TextComponent(
                "text4",
                "EEEEEEEEEEEEEEEEEEE",
                flags=(TextComponent.ALIGN_H_MIDDLE),
            )
            b = BranchComponent("branch", brect(10, 3, 10, 10))
            root_container.add_child("branch")
            sub_container.add_child("text1")
            b.add_child("text2")
            b.add_child("text3")
            b.add_child("text4")

            offset = brect.calculate_alignment_offset(
                sub_container.rect, root_container.rect, (0, 1)
            )
            sub_container.rect.x += offset[0]
            sub_container.rect.y += offset[1]
            PubSub.invoke_to(ParentRectMessage("sub", sub_container.rect), "text1")

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
