# Pattern: Priority Queue
from typing import List, Optional
from enum import Enum
from events.events import Event
import heapq
import threading

class EventPriority(Enum):

    LOW = 1          # Normal transactions, routine updates
    MEDIUM = 3       # Inventory notifications, mode changes
    HIGH = 5         # Hardware failures, supply chain alerts
    CRITICAL = 10    # Emergency mode, system failures

class PriorityEvent:

    
    def __init__(self, event: Event, priority: EventPriority):

        self.event = event
        self.priority = priority.value
        self.timestamp = threading.current_thread().ident
    
    def __lt__(self, other):

        # Reverse comparison for max-heap behavior
        if self.priority != other.priority:
            return self.priority > other.priority
        return self.timestamp < other.timestamp
    
    def __eq__(self, other):
        return self.priority == other.priority
    
    def __le__(self, other):
        return not (self < other)

class EventPriorityQueue:

    
    def __init__(self):

        self._queue: List[PriorityEvent] = []
        self._lock = threading.RLock()
        self._event_handlers = {}
    
    def enqueue(self, event: Event) -> None:

        priority = self._determine_priority(event)
        priority_event = PriorityEvent(event, priority)
        
        with self._lock:
            heapq.heappush(self._queue, priority_event)
    
    def _determine_priority(self, event: Event) -> EventPriority:

        event_type = type(event).__name__
        
        # CRITICAL: Emergency events that override everything
        if "Emergency" in event_type:
            return EventPriority.CRITICAL
        
        # HIGH: Hardware issues requiring immediate attention
        if "HardwareFailure" in event_type or "Technician" in event_type:
            return EventPriority.HIGH
        
        # MEDIUM: System state changes and inventory updates
        if "PricingChanged" in event_type or "InventoryUpdate" in event_type or "Mode" in event_type:
            return EventPriority.MEDIUM
        
        # LOW: Normal transactions and routine events
        return EventPriority.LOW
    
    def dequeue(self) -> Optional[Event]:

        with self._lock:
            if self._queue:
                priority_event = heapq.heappop(self._queue)
                return priority_event.event
            return None
    
    def peek(self) -> Optional[Event]:

        with self._lock:
            if self._queue:
                return self._queue[0].event
            return None
    
    def size(self) -> int:

        with self._lock:
            return len(self._queue)
    
    def is_empty(self) -> bool:

        with self._lock:
            return len(self._queue) == 0
    
    def clear(self) -> None:

        with self._lock:
            self._queue.clear()
    
    def process_all(self, callback) -> int:

        count = 0
        while not self.is_empty():
            event = self.dequeue()
            if event:
                try:
                    callback(event)
                    count += 1
                except Exception as e:
                    print(f"Error processing event: {e}")
        return count
