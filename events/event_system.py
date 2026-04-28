# Pattern: Observer
from typing import Dict, List, Callable, Type
from events.events import BaseEvent

class EventBus:

    def __init__(self):
        # {event_class_name: [list of callbacks]}
        self._subscribers: Dict[str, List[Callable]] = {}
        self._event_log: List[BaseEvent] = []

    def subscribe(self, event_type: Type[BaseEvent], callback: Callable) -> None:

        key = event_type.__name__
        if key not in self._subscribers:
            self._subscribers[key] = []
        if callback not in self._subscribers[key]:
            self._subscribers[key].append(callback)

    def unsubscribe(self, event_type: Type[BaseEvent], callback: Callable) -> None:

        key = event_type.__name__
        if key in self._subscribers and callback in self._subscribers[key]:
            self._subscribers[key].remove(callback)

    def publish(self, event: BaseEvent) -> int:

        self._event_log.append(event)
        key = event.__class__.__name__
        callbacks = self._subscribers.get(key, [])
        for cb in callbacks:
            try:
                cb(event)
            except Exception as e:
                print(f"[EventBus] Subscriber error for {key}: {e}")
        return len(callbacks)

    def get_event_log(self) -> List[BaseEvent]:

        return list(self._event_log)

    def clear_log(self) -> None:
        self._event_log.clear()
