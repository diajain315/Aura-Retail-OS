# Pattern: Strategy pattern
from inventory.inventory_manager import InventoryManager
from events.event_system import EventBus
from transactions.command import CommandInvoker
from hardware.failure_handler import FailureHandler

class Kiosk:

    def __init__(self, kiosk_id: str, name: str, location: str,
                 inventory_manager: InventoryManager,
                 event_bus: EventBus,
                 initial_state,
                 initial_pricing_strategy,
                 failure_chain: FailureHandler = None):

        self.kiosk_id = kiosk_id
        self.name = name
        self.location = location
        self.inventory_manager = inventory_manager
        self.event_bus = event_bus
        self.state = initial_state
        self.pricing_strategy = initial_pricing_strategy
        self.failure_chain = failure_chain
        self.invoker = CommandInvoker()

    def set_state(self, new_state) -> None:

        self.state = new_state

    def set_pricing_strategy(self, strategy) -> None:

        self.pricing_strategy = strategy

    def execute_command(self, command) -> dict:

        return self.invoker.execute(command)

    def undo_last(self) -> dict:
        return self.invoker.undo_last()

    def trigger_hardware_failure(self, component: str, error_msg: str,
                                  severity: str = "medium", log_cb=None) -> dict:

        if not self.failure_chain:
            return {"resolved": False, "message": "No failure handlers configured."}
        failure = {"component": component, "error_message": error_msg, "severity": severity}
        return self.failure_chain.handle(failure, log_cb)

    def __str__(self):
        return f"Kiosk[{self.kiosk_id}] @ {self.location} | Mode: {self.state}"
