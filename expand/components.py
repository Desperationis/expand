import curses
from abc import ABC, abstractmethod
from typing import Optional
from .enums import CHOICE, SCENES, SelectedOption
from .brect import brect
import string
import logging
import threading
import subprocess


class component(ABC):
    def __init__(self, offset=(0, 0)):
        self.offset = offset

    @abstractmethod
    def draw(self, stdscr):
        pass

    @abstractmethod
    def handleinput(self, c: int):
        pass


class textcomponent(component):
    NONE = 0b00000000
    TEXT_CENTERED = 0b00000001
    BOTTOM = 0b00000010
    MIDDLE = 0b00000100
    BAR = 0b00001000

    def __init__(self, text, flags=NONE, offset=(0, 0)):
        super().__init__(offset)
        self.text = text
        self.flags = flags

    def draw(self, stdscr):
        x = self.offset[0]
        y = self.offset[1]
        rows, cols = stdscr.getmaxyx()
        textAttr = curses.A_NORMAL

        if self.flags & self.BOTTOM:
            y = rows - 1

        if self.flags & self.TEXT_CENTERED:
            x = (cols - 1) // 2 - len(self.text) // 2

        if self.flags & self.MIDDLE:
            y = (rows - 1) // 2

        if self.flags & self.BAR:
            leftPadding = 0
            rightPadding = (cols - 1) - len(self.text) - x

            if self.flags & self.TEXT_CENTERED:
                leftPadding = x
                x = 0

            self.text = " " * leftPadding + self.text + " " * rightPadding
            textAttr = curses.A_REVERSE

        try:
            stdscr.addstr(y, x, self.text, textAttr)
        except curses.error:
            pass

    def handleinput(self, c):
        pass


class choicecomponent(component):
    def __init__(self, choices: list[str], back=False, rect=brect(0, 0, 10, 10)):
        super().__init__((0, 0))
        self.choices = choices
        self.choice = SelectedOption()
        self.back = back
        self.brect = rect
        self.selectChar = "> "

        self.elements = []
        self.elementIndex = 0

        self.elements.extend(self.choices)
        if back:
            self.elements.append(CHOICE.BACK)

    def draw(self, stdscr):
        # -1 for back button
        numChoicesVisible = self.brect.h - 1

        startingIndex = max(0, (self.elementIndex + 1) - numChoicesVisible)

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
        """If nothing selected, CHOICE.NONE + None"""
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
