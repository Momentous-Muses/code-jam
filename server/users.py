#! /usr/bin/env python

"""User management classes."""

import rooms


class User:
    """This will be used to store a single user's details while they are connected.

    Note that an instance will last at most one session, since users connect with a new UUID every time.
    """

    def __init__(self, id: str):
        self.id = id

        self.room: rooms.Room = None

    def connect_room(self, room: rooms.Room):
        """Connect user to room."""
        self.room = room

        # May contain more complex code at some time.
