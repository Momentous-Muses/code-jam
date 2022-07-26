from __future__ import annotations

import abc
import typing as t

from .utils import UNINITIALIZED

if t.TYPE_CHECKING:
    import typing_extensions as te


_domain_and_type_to_class: t.Final[dict[tuple[str, str], type[Message]]] = {}


class UnknownMessageTypeError(ValueError):
    """Raised when a message with an unknown type is received."""


class _MessageMeta(type):
    """
    Message metaclass that enforces the `domain` and `type_` class variables.

    Classes with the fields initialized are added to the `_domain_and_type_to_class` dict.
    """

    def __new__(
        cls, name: str, bases: tuple[type, ...], attrs: dict[str, object]
    ) -> te.Self:
        match attrs:
            case {"domain": domain, "type_": type_}:
                pass
            case _:
                raise ValueError(
                    "The message's `domain` and `type_` have to be specified."
                )
        klass = super().__new__(cls, name, bases, attrs)

        if domain is not UNINITIALIZED:
            if (domain, type_) in _domain_and_type_to_class:
                raise RuntimeError(
                    "Only one message class can be registered for a domain with a given message type."
                )
            # Initialized domain and type only come from message subclasses.
            _domain_and_type_to_class[(domain, type_)] = klass  # type: ignore

        return klass


class _MessageABCMeta(_MessageMeta, abc.ABCMeta):
    """Class for a metaclass that's both an abc, and a _MessageMeta."""


class Message(metaclass=_MessageABCMeta):
    """
    A message that can be received or sent to a server.

    `to_json` and `from_json_dict` provide serialization and deserialization for communication.

    Subclassing this will register a new message type with the given `domain` and `type_`,
    after it's registered the class will be used to create messages from the server in the client.
    """

    # Access from anywhere outside this class will be str.
    domain: t.ClassVar[str] = UNINITIALIZED  # type: ignore
    type_: t.ClassVar[str] = UNINITIALIZED  # type: ignore

    @abc.abstractmethod
    def to_json_dict(self) -> dict[str, t.Any]:
        """Create JSON to send to the server for this message."""

    @classmethod
    @abc.abstractmethod
    def from_json_dict(cls, json_: dict[str, t.Any]) -> te.Self:
        # TODO: json_ could have structure described with TypedDict and subclasses
        """Create a message from the `json` JSON dict."""


def message_from_dict(json_: dict[str, t.Any]) -> Message:
    """
    Get a message instance with the registered domain and type from the `json_` dict.

    If no message is registered for the type in the given domain, raise UnknownMessageTypeError.
    """
    message_class = _domain_and_type_to_class.get((json_["domain"], json_["type"]))
    if message_class is None:
        raise UnknownMessageTypeError()
    return message_class.from_json_dict(json_)
