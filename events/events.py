# Pattern: Observer — these are the event objects passed between publishers and subscribers.
from dataclasses import dataclass, field
from datetime import datetime

def _now():
    return datetime.now().strftime("%H:%M:%S")

@dataclass
class BaseEvent:

    timestamp: str = field(default_factory=_now)

    def get_type(self) -> str:
        return self.__class__.__name__

@dataclass
class LowStockEvent(BaseEvent):

    product_id: str = ""
    product_name: str = ""
    remaining_quantity: int = 0

    def __str__(self):
        return f"[{self.timestamp}] ⚠ LOW STOCK: {self.product_name} — {self.remaining_quantity} units left"

@dataclass
class HardwareFailureEvent(BaseEvent):

    component: str = ""
    error_message: str = ""
    severity: str = "medium"  # low | medium | high | critical

    def __str__(self):
        return f"[{self.timestamp}] 🔧 HARDWARE FAILURE: {self.component} — {self.error_message}"

@dataclass
class EmergencyModeActivatedEvent(BaseEvent):

    reason: str = ""
    location: str = ""

    def __str__(self):
        return f"[{self.timestamp}] 🚨 EMERGENCY MODE: {self.reason}"

@dataclass
class ModeChangedEvent(BaseEvent):

    old_mode: str = ""
    new_mode: str = ""

    def __str__(self):
        return f"[{self.timestamp}] \U0001f504 MODE: {self.old_mode.upper()} -> {self.new_mode.upper()}"

@dataclass
class PricingChangedEvent(BaseEvent):

    old_strategy: str = ""
    new_strategy: str = ""
    product_id: str = ""
    old_price: float = 0.0
    new_price: float = 0.0
    reason: str = "Strategy change"

    def __str__(self):
        if self.new_strategy:
            return f"[{self.timestamp}] 💰 PRICING: {self.old_strategy} → {self.new_strategy}"
        return f"[{self.timestamp}] 💰 PRICING CHANGED: {self.product_id} Rs.{self.old_price:.2f} → Rs.{self.new_price:.2f} ({self.reason})"

@dataclass
class InventoryUpdateEvent(BaseEvent):

    product_id: str = ""
    change_type: str = ""  # ADD, DELETE, RESTOCK, REDUCTION
    quantity: int = 0
    reason: str = ""

    def __str__(self):
        icon_map = {
            "ADD": "✨",
            "DELETE": "🗑️",
            "RESTOCK": "📦",
            "REDUCTION": "📉"
        }
        icon = icon_map.get(self.change_type, "📦")
        return f"[{self.timestamp}] {icon} INVENTORY: {self.product_id} ({self.change_type}) {self.quantity} — {self.reason}"

@dataclass
class TransactionEvent(BaseEvent):

    transaction_id: str = ""
    product_name: str = ""
    quantity: int = 0
    amount: float = 0.0
    success: bool = True

    def __str__(self):
        icon = "✅" if self.success else "❌"
        return f"[{self.timestamp}] {icon} PURCHASE: {self.product_name} x{self.quantity} — Rs.{self.amount:.2f}"

@dataclass
class RestockEvent(BaseEvent):

    product_name: str = ""
    quantity_added: int = 0

    def __str__(self):
        return f"[{self.timestamp}] 📦 RESTOCKED: {self.product_name} +{self.quantity_added} units"

@dataclass
class FailureHandledEvent(BaseEvent):

    handler_name: str = ""
    failure_component: str = ""
    resolution: str = ""
    success: bool = False

    def __str__(self):
        icon = "✅" if self.success else "⏭"
        return f"[{self.timestamp}] {icon} {self.handler_name}: {self.resolution}"
