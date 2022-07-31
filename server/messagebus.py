"""
Message Bus for Events/Messages (EDA)

- Maps Handlers and services to Events
"""
import events

HANDLERS = {
    events.NewClientConnection: [],
    events.ClientJoinedRoom: [],
}

INSTALLED_APPS = ()


def handle_event(event: events.Event):
    """Invoked handler for events

    Args:
        event (events.Event): Event/Message instance to handle
    """
    # Default message/event handlers
    for handler in HANDLERS[type(event)]:
        handler(event)

    # 3rd Party apps
    for app in INSTALLED_APPS:
        app.handle_event(event)
