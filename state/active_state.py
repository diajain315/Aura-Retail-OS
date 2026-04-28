# Pattern: State (Concrete State)
from state.kiosk_state import KioskState

class ActiveState(KioskState):

    def handle_purchase(self, kiosk, product_id, quantity):
        return {"allowed": True, "message": "Purchase allowed in Active mode.", "max_quantity": None}

    def handle_restock(self, kiosk, product_id, quantity):
        return {"allowed": True, "message": "Restock allowed."}

    def handle_diagnostics(self, kiosk):
        return {"status": "operational", "mode": self.get_mode_name(), "message": "All systems normal."}

    def get_mode_name(self): return "Active"
    def can_purchase(self): return True
    def get_status_color(self): return "#00D9A3"  # teal/green
