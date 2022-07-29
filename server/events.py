"""
Event data types for the Message-Bus/Event-Driven Architecture

    - Makes it easier to create multiple listeners for different events
"""
from dataclasses import dataclass
from typing import Any, Dict


class Event:
    """
    Base class for all events

        - Implements some useful helper functions
        - Useful for exception handling/type hints
    """

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        """
        Create a new event instance from a dict of data

        Args:
            data (Dict[Any, Any]): Fields and values for event type

        Returns:
            Event: an instance of an event
        """
        return cls(**data)

    def to_dict(self) -> Dict[str, Any]:
        """
        Parse/Dump the fields of an event instance to a dictionary

        Returns:
            Dict: Fields and values of the event
        """
        fields = self.__dataclass_fields__.keys()
        data = {field: getattr(self, field) for field in fields}
        return data


@dataclass
class NewTextMessage(Event):
    """Emitted whenever a new message is created"""

    client_username: str
    client_id: str
    room_id: str
    data: Any

    type: str = "new-text-message"


@dataclass
class NewClientConnection(Event):
    """Emitted whenever a new client joins our websocket channel"""

    client_username: str
    client_id: str
    data: Any

    type: str = "new-client-connection"


@dataclass
class ClosedClientConnection(Event):
    """Emitted whenever a client leaves our websocket channel"""

    client_username: str
    client_id: str
    data: Any

    type: str = "closed-client-connection"


@dataclass
class ClientJoinedRoom(Event):
    """Emitted whenever a client is added to a chat room"""

    room_id: str
    client_username: str
    client_id: str
    data: Any

    type: str = "client-joined-room"


@dataclass
class ClientLeftRoom(Event):
    """Emitted whenever a client leaves/is removed from a chat room"""

    room_id: str
    client_username: str
    client_id: str
    data: Any

    type: str = "client-left-room"


@dataclass
class RoomSubdivided(Event):
    """Emitted whenever a chat room is split in two randomly"""

    room_id: str
    data: Any

    type: str = "client-joined-room"
