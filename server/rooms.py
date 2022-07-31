#! /usr/bin/env python

"""Module to create manage rooms."""

from __future__ import annotations

import uuid
from typing import List

from . import users


class Room:
    """A single room of users.

    This class should contain the necessary functions to manage a single room, such as connecting/disconnecting users,
      adding/removing apps/plugins, etc.
    """

    def __init__(self):
        self.connected_users: List[users.User] = []  # Stores user objects.

        # This may change as we decide fully on how plugins will work.
        self.plugins = []  # Stores plugin objects.

        self.id = self.gen_id()

    def gen_id(self) -> uuid.UUID:
        """Generate a UUID for the Room."""
        return uuid.uuid4()

    def add_plugin(self, plugin) -> None:
        """Install a plugin to a room."""
        self.plugins.append(plugin)

        # Send event to the plugin to initialise it?


class RoomManager:
    """Store/Manage Rooms.

    This class will store and manage all the rooms on an instance of the server.
    """

    def __init__(self):
        self.rooms = []

    def add_room(self, room: Room) -> None:
        """Add a room to the list."""
        self.rooms.append(room)

    def __getitem__(self, index: uuid.UUID):
        """Get a room by its UUID."""
        if isinstance(index, tuple):
            raise ValueError(
                "Multi-dimensional indicies cannot be used with RoomManager."
            )
        elif not isinstance(index, uuid.UUID):
            raise TypeError("Rooms must be indexed by a uuid.UUID.")

        for room in self.rooms:
            if room.id == index:
                return room

        raise ValueError(f"Room with UUID <{str(index)}> not found.")
