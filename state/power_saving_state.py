# Pattern: State (Concrete State)
from state.kiosk_state import KioskState

class PowerSavingState(KioskState):

    def handle_purchase(self, kiosk, product_id, quantity):
        return {
            "allowed": True,
            "message": "Purchase allowed (Power Saving — max 5 per item).",
            "max_quantity": 5
        }

    def handle_restock(self, kiosk, product_id, quantity):
        return {"allowed": False, "message": "Restocking disabled in Power Saving mode."}

    def handle_diagnostics(self, kiosk):
        return {"status": "power-saving", "mode": self.get_mode_name(), "message": "Limited features active."}

    def get_mode_name(self): return "Power Saving"
    def can_purchase(self): return True
    def get_status_color(self): return "#FFA502"  # amber
