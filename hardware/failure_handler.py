# Pattern: Chain of Responsibility (Abstract Handler)
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Optional, Callable

class FailureHandler(ABC):

    def __init__(self):
        self._next: Optional[FailureHandler] = None

    def set_next(self, handler: FailureHandler) -> FailureHandler:

        self._next = handler
        return handler

    @abstractmethod
    def handle(self, failure: dict, log_cb: Optional[Callable] = None) -> dict:

        pass

    @abstractmethod
    def get_handler_name(self) -> str:
        pass

    def _forward(self, failure: dict, log_cb: Optional[Callable]) -> dict:

        if self._next:
            return self._next.handle(failure, log_cb)
        return {"resolved": False, "handler": "EndOfChain",
                "message": "All handlers exhausted. Manual intervention required."}
