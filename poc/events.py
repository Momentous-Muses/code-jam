"""
Event data types for the Message-Bus/Event-Driven Architecture

    - Makes it easier to create multiple listeners for different events
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict


class Event:
    """
    Base class for all events

        - Implements some useful helper functions
        - Useful for exception handling/type hints
    """

    @classmethod
    def from_dict(cls, data: Dict[Any, Any]):
        """
        Create a new event instance from a dict of data

        Args:
            data (Dict[Any, Any]): Fields and values for event type

        Returns:
            Event: an instance of an event
        """
        return cls(**data)

    def to_dict(self):
        """
        Parse/Dump the fields of an event instance to a dictionary

        Returns:
            Dict: Fields and values of the event
        """
        fields = self.__dataclass_fields__.keys()
        data = {field: getattr(self, field) for field in fields}
        return data


@dataclass
class NewMessage(Event):
    """Emitted whenever a new message is created"""

    client_id: str
    room_id: str
    data: Any

    type: str = "new-message"


msg_data = {
    "timestamp": datetime.now().isoformat(),  # ISO format time
    "content": "Message content",
}
msg = NewMessage.from_dict(
    {"client_id": "client_Peter0912", "room_id": "room_9023as", "data": msg_data}
)
print(msg)
print(msg.to_dict())
