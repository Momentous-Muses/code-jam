#! /usr/bin/env python

"""User management classes."""
from __future__ import annotations

from . import rooms


class User:
    """This will be used to store a single user's details while they are connected.

    Note that an instance will last at most one session, since users connect with a new UUID every time.
    """

    def __init__(self, id: str):
        self.id = id

        self.room: rooms.Room = None

        self.nick = "AnonymousUser"

    def connect_room(self, room: rooms.Room):
        """Connect user to room."""
        self.room = room

        # May contain more complex code at some time.

    def add_nick(self, nick: str) -> None:
        """Add a nickname to the user."""
        self.nick = nick

        # This will need to also send a packet to all users in the user's room that the nick has changed.
