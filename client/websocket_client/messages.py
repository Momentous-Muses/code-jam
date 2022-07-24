from __future__ import annotations

import abc
import typing as t

from .utils import UNINITIALIZED

if t.TYPE_CHECKING:
    import typing_extensions as te


_channel_and_type_to_class: t.Final[dict[tuple[str, str], type[Message]]] = {}


class UnknownMessageTypeError(ValueError):
    """Raised when a message with an unknown type is received."""


class _MessageMeta(type):
    """
    Message metaclass that enforces the `channel` and `type_` class variables.

    Classes with the fields initialized are added to the `_channel_and_type_to_class` dict.
    """

    def __new__(
        cls, name: str, bases: tuple[type, ...], attrs: dict[str, object]
    ) -> te.Self:
        match attrs:
            case {"channel": channel, "type_": type_}:
                pass
            case _:
                raise ValueError(
                    "The message's `channel` and `type_` have to be specified."
                )
        klass = super().__new__(cls, name, bases, attrs)

        if channel is not UNINITIALIZED:
            if (channel, type_) in _channel_and_type_to_class:
                raise RuntimeError(
                    "Only one message class can be registered for a channel with a given message type."
                )
            # Initialized channel and type only come from message subclasses.
            _channel_and_type_to_class[(channel, type_)] = klass  # type: ignore

        return klass


class _MessageABCMeta(_MessageMeta, abc.ABCMeta):
    """Class for a metaclass that's both an abc, and a _MessageMeta."""


class Message(metaclass=_MessageABCMeta):
    """
    A message that can be received or sent to a server.

    `to_json` and `from_json_dict` provide serialization and deserialization for communication.

    Subclassing this will register a new message type with the given `channel` and `type_`,
    after it's registered the class will be used to create messages from the server in the client.
    """

    # Access from anywhere outside this class will be str.
    channel: t.ClassVar[str] = UNINITIALIZED  # type: ignore
    type_: t.ClassVar[str] = UNINITIALIZED  # type: ignore

    @abc.abstractmethod
    def to_json(self) -> str:
        """Create JSON to send to the server for this message."""

    @classmethod
    @abc.abstractmethod
    def from_json_dict(cls, json_: dict[str, t.Any]) -> te.Self:
        # TODO: json_ could have structure described with TypedDict and subclasses
        """Create a message from the `json` JSON dict."""


def message_from_dict(json_: dict[str, t.Any]) -> Message:
    """
    Get a message instance with the registered channel and type from the `json_` dict.

    If no message is registered for the type in the given channel, raise UnknownMessageTypeError.
    """
    message_class = _channel_and_type_to_class.get((json_["channel"], json_["type"]))
    if message_class is None:
        raise UnknownMessageTypeError()
    return message_class.from_json_dict(json_)
