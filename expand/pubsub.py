import logging
from abc import ABC
from typing import Any
from .brect import brect


class Message(ABC):
    """
    This object is transmitted on any PubSub message. All children just add
    order to this object.
    """

    def __init__(self, sender_id: str, data):
        self._sender_id = sender_id
        self.data = data

    def get_sender_id(self) -> str:
        return self._sender_id

    def get_data(self) -> Any:
        return self.data


class DrawMessage(Message):
    """
    This message orders a component to draw itself immediately.
    """

    def stdscr(self):
        return self.data


class AdoptionMessage(Message):
    """
    This message orders a component to switch parents. The new parent will be
    the sender of this message.
    """

    def __init__(self, sender_id: str):
        super().__init__(sender_id, sender_id)

    def get_parent_id(self) -> str:
        return self.data


class RunawayMessage(Message):
    """
    When a component switches to a new parent, they send their old parent this
    message to let them know they aren't with them anymore. The child is the
    sender.
    """

    def __init__(self, sender_id: str):
        super().__init__(sender_id, sender_id)

    def get_child_id(self) -> str:
        return self.data


class SuicideMessage(Message):
    """
    This message was included to help with garbage collection. Normally
    Component instances would disappear when out of scope like regular python
    objects, but since PubSub holds callbacks to components they remain alive. 

    This message tells the component to deregister from PubSub entirely. This
    in essence makes the component "dead", as it doesn't react to the program
    anymore and can be freed by python.
    """

    def __init__(self):
        super().__init__("DEAD", "DEAD")


class ParentRectMessage(Message):
    """
    When a component updates the coordinates or dimensions of their rect, this
    message is sent to their children so that they can take note of that.
    """

    def __init__(self, sender_id: str, data: brect):
        super().__init__(sender_id, data)

    def get_rect(self) -> brect:
        return self.data

class NudgeMessage(Message):
    """
    This messages orders a component to immediately move to a position.
    However, this doesn't necessarily mean the component will stay at this
    position and could update itself to move to a different one.
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


