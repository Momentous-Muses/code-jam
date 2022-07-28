#! /usr/bin/env python

"""Module to create manage rooms."""

from typing import List

import users
import uuid


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


class RoomManager:
    """Store/Manage Rooms.

    This class will store and manage all the rooms on an instance of the server.
    """

    pass
