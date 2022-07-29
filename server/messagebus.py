"""
Message Bus for Events/Messages (EDA)

- Maps Handlers and services to Events
"""

import events

HANDLERS = {
    events.NewClientConnection: [],
    events.ClientJoinedRoom: [],
}


def handle_event(event: events.Event):
    """Invoked handler for events

    Args:
        event (events.Event): Event/Message instance to handle
    """
    for handler in HANDLERS[type(event)]:
        handler(event)
