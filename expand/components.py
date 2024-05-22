import curses
import logging
from abc import ABC, abstractmethod
from typing import Optional
from .enums import CHOICE, SCENES, SelectedOption
from .brect import brect


class component(ABC):
    def __init__(self, rect: brect):
        self.rect = rect

    @abstractmethod
    def draw(self, stdscr, parent_rect = None):
        pass

    @abstractmethod
    def handleinput(self, c: int):
        pass

    @staticmethod
    def debug_draw_brect(stdscr, rect, color=None):
        """
        Draw the bounding box to the canvas. Keep in mind that anything
        directly outside the box is considered out of bounds. If a piece of
        text draws OVER the box, it is in bounds. For this reason, please call
        this before the component renders.
        """

        if color is None:
            color = curses.color_pair(0)

        # We use try and except so that we can easily see if the boundary is
        # out of bounds or not.
        try:
            stdscr.addstr(rect.y, rect.x, "^" * rect.w, color)
            stdscr.addstr(rect.y + rect.h - 1, rect.x, "_" * rect.w, color)
        except curses.error:
            pass

        try:
            for i in range(rect.h):
                stdscr.addstr(rect.y + i, rect.x, "|", color)
                stdscr.addstr(rect.y + i, rect.x + rect.w - 1, "|", color)

        except curses.error:
            pass



class groupcomponent(component):
    def __init__(self, rect):
        super().__init__(rect)

        self.rect: brect = rect
        self.components = []

    def add(self, component: component):
        """
        Read this section carefully. 

        g = groupcomponent(brect(3, 4, 10, 10)) 
        c = textcomponent(brect(1,2, 5, 5))
        g.add(c)

        This places textcomponent in the absolute position (4, 6), because this
        function assumes that the component you are adding has coordinates
        relative to the group coordinate.
        
        What if bounding box of added element is bigger than the group?

        g = groupcomponent(brect(3, 4, 10, 10)) 
        c = textcomponent(brect(1,2, 500, 500))
        g.add(c)
    
        In this case, everything will still work as normal. It is expected that
        the draw() function of textcomponent alone is able to use the bounding
        box of the group to restrict rendering.
        """

        self.components.append(component)

    def draw(self, stdscr, parent_rect = None):
        self.debug_draw_brect(stdscr, self.rect)

        for c in self.components:
            c.draw(stdscr, self.rect)

    def handleinput(self, c: int):
        for component in self.components:
            component.handleinput(c)




class textcomponent(component):

    # Standard Text, no modication in display
    NONE = 0

    # Center the text horizontally
    ALIGN_H_LEFT = 1 << 1
    ALIGN_H_MIDDLE = 1 << 2
    ALIGN_H_RIGHT = 1 << 3

    # Center the text vertically
    ALIGN_V_TOP = 1 << 4
    ALIGN_V_MIDDLE = 1 << 5
    ALIGN_V_BOTTOM = 1 << 6

    # Special Effects / Text Attributes
    # NOTE: These may not work depending on the terminal you are using.
    REVERSE = 1 << 7
    BLINK = 1 << 8
    BOLD = 1 << 9
    DIM = 1 << 10
    STANDOUT = 1 << 11
    UNDERLINE = 1 << 12


    def __init__(self, text, rect, flags=NONE, color=NONE):
        super().__init__(rect)

        self.text = text
        self.flags = flags
        self.rect: brect = rect
        self.color = color


    @staticmethod
    def get_cropped_text(text: str, rect: brect) -> str:
        """
        Return cropped text that can fit in bounding box. With unicode
        characters (i.e. emojis), this function might cut it shorter than what
        is liked.
        """
        return text[:rect.w]


    @staticmethod
    def calculate_alignment_offset(text: str, rect: brect, flags):
        """
        Let's say `text` is in the top left of `rect`. If `ALIGN_V_MIDDLE` or
        any of the other flags in textcomponent is enabled in `flags`, this
        method calculates the x and y offset relative to the origin (top left)
        of `rect` the text should be drawn. 

        To get the absolute position of where the text should be drawn, the
        code would look something like this:

            x, y = calculate_alignment_offset(text, rect, flags)
            stdscr.addstr(rect.y + y, rect.x + x, text)
        """

        x, y, w, h = rect.x, rect.y, rect.w, rect.h
        offset_x, offset_y = 0, 0

        if flags & textcomponent.ALIGN_V_TOP:
            pass
        elif flags & textcomponent.ALIGN_V_MIDDLE:
            offset_y = (h - 1) // 2
        elif flags & textcomponent.ALIGN_V_BOTTOM:
            offset_y = h - 1

        if flags & textcomponent.ALIGN_H_LEFT:
            pass
        elif flags & textcomponent.ALIGN_H_MIDDLE:
            offset_x = (w - len(text)) // 2
        elif flags & textcomponent.ALIGN_H_RIGHT:
            offset_x = w - len(text) 

        
        return offset_x, offset_y

    @staticmethod
    def lookup_text_attr(flags):
        """
        Given a list of flags from `textcomponent`, get the conjoined "Special
        Effects" flags in ncurses format.
        """

        lookup = {
            textcomponent.REVERSE: curses.A_REVERSE,
            textcomponent.BLINK: curses.A_BLINK,
            textcomponent.BOLD: curses.A_BOLD,
            textcomponent.DIM: curses.A_DIM,
            textcomponent.STANDOUT: curses.A_STANDOUT,
            textcomponent.UNDERLINE: curses.A_UNDERLINE
        }

        attrs = 0
        for flag in lookup:
            if flags & flag:
                attrs |= lookup[flag]

        if attrs == 0:
            attrs = curses.A_NORMAL

        return attrs


    def draw(self, stdscr, parent_rect=None):
        rect = self.rect.copy()
        if parent_rect is not None:
            rect.w = min(parent_rect.w - rect.x, rect.w)
            rect.h = min(parent_rect.h - rect.y, rect.h)
            rect.x += parent_rect.x
            rect.y += parent_rect.y

        displayed_text = self.get_cropped_text(self.text, rect)
        o_x, o_y = self.calculate_alignment_offset(displayed_text, rect, self.flags)
        x = rect.x + o_x
        y = rect.y + o_y
        attrs = self.lookup_text_attr(self.flags)

        if self.color is not None:
            attrs |= self.color

        self.debug_draw_brect(stdscr, rect)
        logging.debug(self.text[:10])
        logging.debug(displayed_text)

        try:
            stdscr.addstr(y, x, displayed_text, attrs)
        except curses.error:
            pass

    def handleinput(self, c):
        pass











"""
class choicecomponent(component):
    def __init__(self, offset=(0, 0)):
        super().__init__(offset)


class choicecomponent(component):
    def __init__(self, choices: list[str], rect=brect(0, 0, 10, 10)):
        super().__init__((0, 0))
        self.choices = choices
        self.choice = SelectedOption()
        self.brect = rect
        self.selectChar = "> "

        self.elements = self.choices
        self.elementIndex = 0


    def draw(self, stdscr):
        numChoicesVisible = self.brect.h

        startingIndex = max(0, (self.elementIndex) - numChoicesVisible)

        for i in range(startingIndex, len(self.elements)):
            option = self.elements[i]
            x = self.brect.x + len(self.selectChar)
            y = self.brect.y + (i - startingIndex)
            content = option

            # -1 for back
            if option != CHOICE.BACK and y >= self.brect.bottom():
                continue

            if option == CHOICE.BACK:
                content = "Back"
                y = min(y + 1, self.brect.bottom())

            if i == self.elementIndex:
                x -= len(self.selectChar)
                content = f"{self.selectChar}{content}"

            try:
                if option != CHOICE.BACK and option.endswith("/"):
                    stdscr.addstr(y, x, content, curses.color_pair(1))
                else:
                    stdscr.addstr(y, x, content)
            except curses.error:
                pass

    def cursorOnChoice(self):
        return self.elementIndex >= 0 and self.elementIndex < len(self.choices)

    def cursorOnBack(self):
        return self.elements[self.elementIndex] == CHOICE.BACK

    def getChoice(self) -> SelectedOption:
        return self.choice

    def handleinput(self, c: int):
        if c == curses.KEY_UP or c == ord("k"):
            self.elementIndex -= 1
        elif c == curses.KEY_DOWN or c == ord("j"):
            self.elementIndex += 1
        elif c == ord("u"):
            self.choice = SelectedOption(CHOICE.REFRESH)
        elif c == curses.KEY_ENTER or c == 10:
            if self.cursorOnChoice():
                self.choice = SelectedOption(
                    CHOICE.SELECTED, self.choices[self.elementIndex]
                )
            if self.cursorOnBack():
                self.choice = SelectedOption(CHOICE.BACK)
        elif c == ord("h") and self.back:
            self.choice = SelectedOption(CHOICE.BACK)

        elif c == ord("d"):
            self.choice = SelectedOption(
                CHOICE.DOWNLOAD, self.choices[self.elementIndex]
            )

        elif c == ord("q"):
            self.choice = SelectedOption(CHOICE.QUIT)

        self.elementIndex = self.elementIndex % len(self.elements)

"""
