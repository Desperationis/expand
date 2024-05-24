import curses
import logging
from abc import ABC, abstractmethod
from typing import Optional, Self
from .enums import CHOICE, SCENES, SelectedOption
from .brect import brect

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

class Message(ABC):
    def __init__(self, sender_id: str, data):
        self._sender_id = sender_id
        self.data = data

    def get_sender_id(self) -> str:
        return self._sender_id


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

class PubSub:
    _instance = None
    listeners = {}
    id_to_callback = {}
    
    def __new__(cls):
        if not hasattr(cls, 'instance'):
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

        # For private lookup
        if id not in PubSub.id_to_callback:
            PubSub.id_to_callback[id] = {}
        if event_class not in PubSub.id_to_callback[id]:
            PubSub.id_to_callback[id][event_class] = []

        PubSub.id_to_callback[id][event_class].append(callback)

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
        self.children = set()

        PubSub.add_listener(self.id, AdoptionMessage, lambda m: self.set_parent(m.get_parent_id()))
        PubSub.add_listener(self.id, RunawayMessage, lambda m: self.remove_child(m.get_child_id()))
        PubSub.add_listener(self.id, DrawMessage, lambda m: self.draw(m.stdscr()))

    def set_parent(self, parent_id):
        if self.parent_id == parent_id:
            return

        if self.parent_id != None:
            PubSub.invoke_to(RunawayMessage(self.id), self.parent_id)
        self.parent_id = parent_id

    def add_child(self, child_id):
        self.children.add(child_id)
        PubSub.invoke_to(AdoptionMessage(self.id), child_id)

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


