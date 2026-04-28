# Pattern: State (Abstract State)
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.kiosk import Kiosk

class KioskState(ABC):

    @abstractmethod
    def handle_purchase(self, kiosk: Kiosk, product_id: str, quantity: int) -> dict:

        pass

    @abstractmethod
    def handle_restock(self, kiosk: Kiosk, product_id: str, quantity: int) -> dict:

        pass

    @abstractmethod
    def handle_diagnostics(self, kiosk: Kiosk) -> dict:

        pass

    @abstractmethod
    def get_mode_name(self) -> str:
        pass

    @abstractmethod
    def can_purchase(self) -> bool:
        pass

    @abstractmethod
    def get_status_color(self) -> str:

        pass

    def __str__(self) -> str:
        return self.get_mode_name()
