class EventBus:
    def __init__(self):
        self.listeners = {}

    def subscribe(self, event_type, callback):
        """Subscribe to an event with a specific callback."""
        if event_type not in self.listeners:
            self.listeners[event_type] = []
        self.listeners[event_type].append(callback)

    def emit(self, event_type, *args, **kwargs):
        """Emit an event and call all registered callbacks for that event type."""
        if event_type in self.listeners:
            for callback in self.listeners[event_type]:
                callback(*args, **kwargs)

    def unsubscribe(self, event_type, callback):
        """Unsubscribe a specific callback from an event."""
        if event_type in self.listeners:
            try:
                self.listeners[event_type].remove(callback)
                if not self.listeners[event_type]:  # Clean up if no listeners are left
                    del self.listeners[event_type]
            except ValueError:
                # If callback is not found, ignore
                pass


# Dictionary to store shared EventBus instances
_shared_event_buses = {}


def create_or_get_shared_event_bus(name="glavna"):
    """
    Factory method to create or get a shared EventBus instance.

    Args:
        name (str): The name of the shared EventBus instance.

    Returns:
        EventBus: The shared EventBus instance.
    """
    if name not in _shared_event_buses:
        _shared_event_buses[name] = EventBus()
    return _shared_event_buses[name]


def get_shared_event_bus(name="glavna"):
    """
    Retrieves an existing shared EventBus instance by name.

    Args:
        name (str): The name of the shared EventBus instance.

    Returns:
        EventBus: The shared EventBus instance, or None if it doesn't exist.
    """
    return _shared_event_buses.get(name)
