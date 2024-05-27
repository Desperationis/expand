"""
    We will start with two strict rule:
        * Containers can only draw within themselves.

    Let's make a giant container that fits the entire screen without a
    parent. This is the root container that allows us to potentially
    render to the entire terminal whatever we want. There's nothing for
    now, so let's move on.

    Let's add another rule:
        * Containers can have other containers inside them.

    We can subdivide this giant container into, let's say, two
    containers that fill up the screen side by side to each other. But
    right now, containers are a little boring. While they can draw
    things inside them, there is nothing for them to draw! So let's
    make a subclass of a container called a "component". Components are
    containers, but they use some code to actually render things inside
    them. 

    Cool, so we have containers that do nothing and components that do
    something. But, how do we arrange them and organize them in space?
    We should look for a method that is not only easy to visualize, but
    also works when the terminal is resized. One way we can do this is
    to have every container have a "parent" that can used for relative
    positioning, but have each component have its own global
    coordinate. 

    So let's make some more rules:
        * Every component must know its parent.
        * Every component knows its global position.

    But now there's other issue. If we want to be reactive, who takes
    charge? Does the parent move the child, or does the child move
    itself? In some sense, it's actually both. The parent must somehow
    be able to move the child when it itself changes size, and the
    child has to know when it moves so that it itself can update its
    own children. We don't want the parents to directly know about
    their children and directly update them, as that is just bad
    practice waiting to happen. In addition, the method we choose must
    have properties that make it easy to react to other events, such as
    change in focus and mouse clicks, in case we ever want those in the
    future. The method should also not break cohesion, as every
    component should only worry about itself and not its children. A
    framework that is a good for is PubSub. 

    So let's define more rules:
        * Components have the power to move themselves anywhere within
        their parent as long as they don't escape it.
        * Component-Component communication about ANY event is done through PubSub.
        * Components can never directly access their parent or their
        children, they can only at most know their IDs.
        * All messages in PubSub carry data.
        * Every single component must be able to access one PubSub system.
        * When a component receives a PubSub message, it relays it to its
        children as well.

    Cool, so we have a reactive hierarchical system that can handle a
    lot given some patience. When a component receives the event that
    their parent has changed size, they can cache their new parent's
    bound such that all subsequent calculations about their own
    position can be based on their parents so as to not break any
    rules. If they receive a click event, they just need to check to
    see if the coordinates hit inside them. So with that, here are the
    list of rules that govern `expand`:
        0. Containers are rectangular objects with origin in the
        topleft such that (1,1) is to the bottomright of (0,0)

        1. Containers can only draw within themselves.

        2. Containers can have other containers inside them.

        3. Every component must know its parent.

        4. Every component must know its global position.

        5. Components have the power to move themselves anywhere within
        their parent as long as they don't escape it.

        6. Component-Component communication about ANY event is done
        through PubSub.

        7. Components can never directly access their parent or their
        children, they can only at most know their IDs.

        8. All messages in PubSub carry data.

        9. Every single component must be able to access one PubSub system.

        10. When a component receives a PubSub message, it relays it to its
        children as well.



    Here's how I am going to implement this project using only these rules.

    0. Put all keyboard events as PubSub messages.
    1. Create a container that fits the screen. 
    2. Put another container inside of it that is able to move itself relative
    to its parent as well as use alignment.
    3. Create `textcomponent`, which renders text in goofy colors and such. Its
    container should be just big enough to wrap a single line of text. If it
    knows it is out of frame, it should be smart enough to know not to render.
    4. Create `branchcomponent`. It should have the capability of changing size
    (height) by adding and hiding text components. On resize, it sends a
    message via pub size that it changed size. There should be a message that
    tells it to expand and such.
    5. Create `stackcomponent`. It's whole purpose is to stack any components
    on top of each other, even if they change size. It can request components
    to move to a different spot if needed if one expands.
    6. Create `choosecomponent`. It uses some sort of PubSub message to be able
    to send messages to the text components to show a cursor icon. When the
    user presses enter, it reads the text and does things with it.
    7. Create a subclass of `textcomponent` called `playbookcomponent`, which
    is the same thing but can display its own little checks independently.
"""


import curses
import logging
from abc import ABC
from typing import Any
from .brect import brect

class Message(ABC):
    def __init__(self, sender_id: str, data):
        self._sender_id = sender_id
        self.data = data

    def get_sender_id(self) -> str:
        return self._sender_id

    def get_data(self) -> Any:
        return self.data


class KeyMessage(Message):
    def __init__(self, sender_id: str, data: str):
        super().__init__(sender_id, data)

    def get_key(self) -> str:
        return self.data


class DrawMessage(Message):
    def stdscr(self):
        return self.data


class AdoptionMessage(Message):
    def __init__(self, sender_id: str):
        super().__init__(sender_id, sender_id)

    def get_parent_id(self) -> str:
        return self.data


class RunawayMessage(Message):
    def __init__(self, sender_id: str):
        super().__init__(sender_id, sender_id)

    def get_child_id(self) -> str:
        return self.data


class SuicideMessage(Message):
    def __init__(self, sender_id: str):
        super().__init__(sender_id, sender_id)


class ParentBRectMessage(Message):
    def __init__(self, sender_id: str, data: brect):
        super().__init__(sender_id, data)

    def get_brect(self) -> brect:
        return self.data

class NudgeMessage(Message):
    """
    This "nudges" a component to a certain coordinate on the screen.
    """

    def __init__(self, sender_id: str, data: tuple[int, int]):
        super().__init__(sender_id, data)

    def get_coordinates(self) -> tuple[int, int]:
        return self.data


class PubSub:
    _instance = None
    listeners = {}
    id_to_callback = {}

    def __new__(cls):
        if not hasattr(cls, "instance"):
            cls._instance = super(PubSub, cls).__new__(cls)

        return cls._instance

    @staticmethod
    def reset():
        PubSub.listeners.clear()
        PubSub.id_to_callback.clear()
        PubSub._instance = None

    @staticmethod
    def add_listener(id, event_class, callback):
        # Global Listeners
        event_class = hash(event_class)
        if event_class not in PubSub.listeners:
            PubSub.listeners[event_class] = []
        PubSub.listeners[event_class].append(callback)

        # For private lookup / garbage cleanup
        if id not in PubSub.id_to_callback:
            PubSub.id_to_callback[id] = {}
        if event_class not in PubSub.id_to_callback[id]:
            PubSub.id_to_callback[id][event_class] = []

        PubSub.id_to_callback[id][event_class].append(callback)

    @staticmethod
    def remove_listener(id):
        if id not in PubSub.id_to_callback:
            return

        for event_class in PubSub.id_to_callback[id]:
            for callback in PubSub.id_to_callback[id][event_class]:
                PubSub.listeners[event_class].remove(callback)

        PubSub.id_to_callback[id].clear()
        del PubSub.id_to_callback[id]

    @staticmethod
    def invoke_to(message, id):
        if id not in PubSub.id_to_callback:
            return

        class_type = hash(type(message))
        if class_type in PubSub.id_to_callback[id]:
            for l in PubSub.id_to_callback[id][class_type]:
                l(message)

    @staticmethod
    def invoke_global(message):
        class_type = hash(type(message))
        if PubSub.listeners[class_type]:
            for l in PubSub.listeners[class_type]:
                l(message)


class Container:
    def __init__(self, id, rect: brect):
        self.id = id
        self.rect = rect
        self.parent_id = None
        self.parent_rect = None
        self.children = set()

        PubSub.add_listener(
            self.id, AdoptionMessage, lambda m: self.set_parent(m.get_parent_id())
        )
        PubSub.add_listener(
            self.id, RunawayMessage, lambda m: self.remove_child(m.get_child_id())
        )
        PubSub.add_listener(self.id, DrawMessage, lambda m: self.draw(m.stdscr()))
        PubSub.add_listener(
            self.id,
            ParentBRectMessage,
            lambda m: self.update_parent_rect_cache(m.get_brect()),
        )
        PubSub.add_listener(self.id, SuicideMessage, lambda m: self.destroy())

        PubSub.add_listener(self.id, NudgeMessage, lambda m: self.move_to(m.get_coordinates()))

    def move_to(self, coordinate: tuple[int, int]):
        logging.debug(f"{self.id} moving to {coordinate}")
        self.rect.x = coordinate[0]
        self.rect.y = coordinate[1]

    def destroy(self):
        PubSub.remove_listener(self.id)
        for child in self.children:
            PubSub.invoke_to(SuicideMessage(self.id), child)

    def set_parent(self, parent_id):
        if self.parent_id == parent_id:
            return

        if self.parent_id != None:
            PubSub.invoke_to(RunawayMessage(self.id), self.parent_id)
        self.parent_id = parent_id

    def update_parent_rect_cache(self, brect):
        self.parent_rect = brect

    def add_child(self, child_id: str):
        if not isinstance(child_id, str):
            raise Exception()

        self.children.add(child_id)
        PubSub.invoke_to(AdoptionMessage(self.id), child_id)
        PubSub.invoke_to(ParentBRectMessage(self.id, self.rect.copy()), child_id)

    def remove_child(self, child_id):
        self.children.remove(child_id)

    def debug_draw_brect(self, stdscr, color=None):
        """
        Draw the bounding box to the canvas. Keep in mind that anything
        directly outside the box is considered out of bounds. If a piece of
        text draws OVER the box, it is in bounds. For this reason, please call
        this before the component renders.
        """

        rect = self.rect

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

    def draw(self, stdscr):
        self.debug_draw_brect(stdscr)
        logging.debug(self.children)
        for child_id in self.children:
            PubSub.invoke_to(DrawMessage(self.id, stdscr), child_id)


class TextComponent(Container):
    """
    A container that tightly wraps around a single line of text and can
    self-arrange itself when given a parent.
    """

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

    def __init__(self, id, text, flags=NONE, color=NONE):
        rect = brect(0, 0, len(text), 1)
        super().__init__(id, rect)

        self.text = text
        self.flags = flags
        self.color = color

    def copy(self, new_id):
        return TextComponent(new_id, self.text, self.flags, self.color)

    @staticmethod
    def get_cropped_text(text: str, rect: brect) -> str:
        """
        Return cropped text that can fit in bounding box. With unicode
        characters (i.e. emojis), this function might cut it shorter than what
        is liked.
        """
        return text[:rect.w]

    @staticmethod
    def calculate_text_alignment_offset(text_rect: brect, container_rect: brect, flags):
        if (
            flags
            & (
                TextComponent.ALIGN_V_TOP
                | TextComponent.ALIGN_V_MIDDLE
                | TextComponent.ALIGN_V_BOTTOM
                | TextComponent.ALIGN_H_LEFT
                | TextComponent.ALIGN_H_MIDDLE
                | TextComponent.ALIGN_H_RIGHT
            )
            == 0
        ):
            return (0, 0)

        o_x, o_y = 0, 0

        if flags & TextComponent.ALIGN_V_TOP:
            o_y = -1
        elif flags & TextComponent.ALIGN_V_MIDDLE:
            o_y = 0
        elif flags & TextComponent.ALIGN_V_BOTTOM:
            o_y = 1

        if flags & TextComponent.ALIGN_H_LEFT:
            o_x = -1
        elif flags & TextComponent.ALIGN_H_MIDDLE:
            o_x = 0
        elif flags & TextComponent.ALIGN_H_RIGHT:
            o_x = 1

        alignment = brect.calculate_alignment_offset(
            text_rect, container_rect, (o_x, o_y)
        )

        if (
            flags
            & (
                TextComponent.ALIGN_V_TOP
                | TextComponent.ALIGN_V_MIDDLE
                | TextComponent.ALIGN_V_BOTTOM
            )
            == 0
        ):
            return alignment[0], 0

        if (
            flags
            & (
                TextComponent.ALIGN_H_LEFT
                | TextComponent.ALIGN_H_MIDDLE
                | TextComponent.ALIGN_H_RIGHT
            )
            == 0
        ):
            return 0, alignment[1]

        return alignment

    @staticmethod
    def lookup_text_attr(flags):
        """
        Given a list of flags from `TextComponent`, get the conjoined "Special
        Effects" flags in ncurses format.
        """

        lookup = {
            TextComponent.REVERSE: curses.A_REVERSE,
            TextComponent.BLINK: curses.A_BLINK,
            TextComponent.BOLD: curses.A_BOLD,
            TextComponent.DIM: curses.A_DIM,
            TextComponent.STANDOUT: curses.A_STANDOUT,
            TextComponent.UNDERLINE: curses.A_UNDERLINE,
        }

        attrs = 0
        for flag in lookup:
            if flags & flag:
                attrs |= lookup[flag]

        if attrs == 0:
            attrs = curses.A_NORMAL

        return attrs

    @staticmethod
    def get_aligned_rect(rect: brect, container_rect: brect, flags) -> brect:
        """
        Given a `rect`, return a new `rect` such that x and y are aligned to
        `container_rect` given the alignment flags in `flags`. If no alignment
        flags are set, returns a carbon copy of rect `rect` without
        modification.

    TODO
        If after alignment `rect` has negative coordinates relative to the
        parent, they are corrected to the top/left of the parent.

        If after alignment and correction `rect` has dimensions that would make
        it too big to fit in its aligned position, this will return a rect that
        is `rect` with cropped width and height.

        """

        if flags == TextComponent.NONE:
            return rect.copy()
        
        rect_copy = rect.copy()
        offset = TextComponent.calculate_text_alignment_offset(rect_copy, container_rect, flags)

        # Align Rect
        rect_copy.x += offset[0]
        rect_copy.y += offset[1]

        if rect_copy.x - container_rect.x < 0:
            rect_copy.x = container_rect.x
        if rect_copy.y - container_rect.y < 0:
            rect_copy.y = container_rect.y

        # Crop rect if too big
        rect_copy.w = max(min(container_rect.w - (rect_copy.x - container_rect.x), rect_copy.w), 0)
        rect_copy.h = max(min(container_rect.h - (rect_copy.y - container_rect.y), rect_copy.h), 0)

        return rect_copy



    def draw(self, stdscr):
        if self.parent_rect is not None:
            self.rect = self.get_aligned_rect(self.rect, self.parent_rect, self.flags)

            if not self.rect.colliding(self.parent_rect):
                return None


        displayed_text = self.get_cropped_text(self.text, self.rect)
        attrs = self.lookup_text_attr(self.flags)

        if self.color is not None:
            attrs |= self.color

        self.debug_draw_brect(stdscr, curses.color_pair(1))

        try:
            stdscr.addstr(self.rect.y, self.rect.x, displayed_text, attrs)
        except curses.error:
            pass


class BranchComponent(Container):
    def __init__(self, id, rect: brect):
        rect.h = 0
        super().__init__(id, rect)

    def add_child(self, child_id: str):
        super().add_child(child_id)

        self.rect.h += 1

        PubSub.invoke_to(NudgeMessage(self.id, (self.rect.x, self.rect.y + len(self.children) - 1)), child_id)
        PubSub.invoke_to(ParentBRectMessage(self.id, self.rect.copy()), child_id)


    def draw(self, stdscr):
        rect = self.rect.copy()
        self.rect.h = 2

        self.debug_draw_brect(stdscr)

        for child_id in self.children:
            PubSub.invoke_to(DrawMessage(self.id, stdscr), child_id)



