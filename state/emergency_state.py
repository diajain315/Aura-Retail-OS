# Pattern: State (Concrete State)
from state.kiosk_state import KioskState

class EmergencyLockdownState(KioskState):

    def __init__(self, max_per_person: int = 2):
        self.max_per_person = max_per_person

    def handle_purchase(self, kiosk, product_id, quantity):
        product = kiosk.inventory_manager.get_product(product_id)
        if not product:
            return {"allowed": False, "message": "Product not found.", "max_quantity": None}

        if not product.get("essential", False):
            return {
                "allowed": False,
                "message": f"❌ Non-essential items are restricted during emergency lockdown.",
                "max_quantity": 0
            }

        effective_qty = min(quantity, self.max_per_person)
        note = f"⚠ Quantity capped at {self.max_per_person} per person." if quantity > self.max_per_person else ""
        return {
            "allowed": True,
            "message": f"✅ Essential item — purchase allowed. {note}",
            "max_quantity": self.max_per_person
        }

    def handle_restock(self, kiosk, product_id, quantity):
        return {"allowed": True, "message": "Emergency restocking authorised."}

    def handle_diagnostics(self, kiosk):
        return {
            "status": "emergency",
            "mode": self.get_mode_name(),
            "message": "⚠ EMERGENCY LOCKDOWN — essential items only, max 2 per person."
        }

    def get_mode_name(self): return "Emergency Lockdown"
    def can_purchase(self): return True
    def get_status_color(self): return "#FF4757"  # red/danger
