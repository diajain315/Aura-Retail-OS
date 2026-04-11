from inventory.inventory_manager import InventoryManager
from command.command import CommandInvoker


class Kiosk:

    def __init__(self, kiosk_id: str, name: str, location: str,
                 inventory_manager: InventoryManager,
                 initial_pricing_strategy):

        self.kiosk_id = kiosk_id
        self.name = name
        self.location = location
        self.inventory_manager = inventory_manager
        self.pricing_strategy = initial_pricing_strategy
        self.invoker = CommandInvoker()

    def set_pricing_strategy(self, strategy) -> None:
        """Swap pricing strategy at runtime (Strategy Pattern)."""
        self.pricing_strategy = strategy

    def execute_command(self, command) -> dict:
        """Run a command through the invoker (Command Pattern)."""
        return self.invoker.execute(command)

    def undo_last(self) -> dict:
        return self.invoker.undo_last()

    def __str__(self):
        return f"Kiosk[{self.kiosk_id}] @ {self.location} | Pricing: {self.pricing_strategy.__class__.__name__}"
