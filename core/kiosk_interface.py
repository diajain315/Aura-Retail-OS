# Pattern: Facade
from datetime import datetime
from core.kiosk import Kiosk
from transactions.purchase_command import PurchaseItemCommand
from transactions.restock_command import RestockCommand
from events.events import (
    TransactionEvent, RestockEvent, LowStockEvent,
    HardwareFailureEvent, EmergencyModeActivatedEvent,
    ModeChangedEvent, PricingChangedEvent,
    InventoryUpdateEvent
)

class KioskInterface:

    def __init__(self, kiosk: Kiosk, registry, data_manager=None, kiosk_type: str = "food"):
        self.kiosk = kiosk
        self.registry = registry
        self.data_manager = data_manager
        self.kiosk_type = kiosk_type

    # ── Purchases ─────────────────────────────────────────────────────────

    def purchase_item(self, product_id: str, quantity: int = 1) -> dict:
        cmd = PurchaseItemCommand(
            kiosk=self.kiosk,
            product_id=product_id,
            quantity=quantity,
            pricing_strategy=self.kiosk.pricing_strategy
        )
        result = self.kiosk.execute_command(cmd)

        if result["success"]:
            # Update stats
            self.registry.update_stats(result["total_amount"], result["quantity"])
            # Publish transaction event
            self.kiosk.event_bus.publish(TransactionEvent(
                product_name=result["product_name"],
                quantity=result["quantity"],
                amount=result["total_amount"],
                transaction_id=result["transaction_id"],
                success=True
            ))
            # Persist
            if self.data_manager:
                self.data_manager.append_transaction(result)
            self._persist_inventory()
            # Check for low stock
            self._check_low_stock(product_id)
        else:
            self.kiosk.event_bus.publish(TransactionEvent(
                product_name=product_id, quantity=quantity,
                amount=0.0, transaction_id="FAIL", success=False
            ))

        return result

    def refund_transaction(self) -> dict:

        result = self.kiosk.undo_last()
        if result.get("success"):
            self._persist_inventory()
            
            # Update stats backwards
            refund_amt = result.get("refund_amount", 0.0)
            qty = result.get("quantity", 0)
            pid = result.get("product_id", "")
            
            if refund_amt or qty:
                self.registry.update_stats(-refund_amt, -qty)
            
            # Always publish an event so UI can refresh
            self.kiosk.event_bus.publish(InventoryUpdateEvent(
                product_id=pid if pid else "ALL",
                change_type="ADD", 
                quantity=qty,
                reason="Undo action performed"
            ))
                
        return result

    # ── Inventory ─────────────────────────────────────────────────────────

    def restock_inventory(self, product_id: str, quantity: int) -> dict:
        cmd = RestockCommand(self.kiosk, product_id, quantity)
        result = self.kiosk.execute_command(cmd)
        if result["success"]:
            self.kiosk.event_bus.publish(RestockEvent(
                product_name=result.get("product_name", product_id),
                quantity_added=quantity
            ))
            self._persist_inventory()
        return result

    def restock_all(self, quantity: int = 50) -> None:

        for p in self.kiosk.inventory_manager.get_all_products():
            self.restock_inventory(p["id"], quantity)

    # ── Mode & Pricing ─────────────────────────────────────────────────────

    def set_mode(self, new_state, mode_name: str) -> None:
        old = self.kiosk.state.get_mode_name()
        self.kiosk.set_state(new_state)
        self.registry.current_mode = mode_name

        self.kiosk.event_bus.publish(ModeChangedEvent(old_mode=old, new_mode=mode_name))

        if "emergency" in mode_name.lower():
            self.kiosk.event_bus.publish(EmergencyModeActivatedEvent(
                reason="Emergency mode manually activated",
                location=self.kiosk.location
            ))

    def set_pricing(self, strategy, strategy_name: str) -> None:
        old = self.kiosk.pricing_strategy.get_strategy_name()
        self.kiosk.set_pricing_strategy(strategy)
        self.registry.current_pricing = strategy_name
        self.kiosk.event_bus.publish(PricingChangedEvent(
            old_strategy=old, new_strategy=strategy_name
        ))

    # ── Hardware ───────────────────────────────────────────────────────────

    def trigger_hardware_failure(self, component: str, severity: str = "medium",
                                  log_cb=None) -> dict:

        error_msg = f"Unexpected fault in {component}"
        self.kiosk.event_bus.publish(HardwareFailureEvent(
            component=component, error_message=error_msg, severity=severity
        ))
        return self.kiosk.trigger_hardware_failure(component, error_msg, severity, log_cb)

    # ── Diagnostics ────────────────────────────────────────────────────────

    def run_diagnostics(self) -> dict:
        return self.kiosk.state.handle_diagnostics(self.kiosk)

    # ── Helpers ────────────────────────────────────────────────────────────

    def _check_low_stock(self, product_id: str) -> None:
        threshold = self.registry.low_stock_threshold
        product = self.kiosk.inventory_manager.get_product(product_id)
        if product and product["quantity"] <= threshold:
            self.kiosk.event_bus.publish(LowStockEvent(
                product_id=product_id,
                product_name=product["name"],
                remaining_quantity=product["quantity"]
            ))

    def _persist_inventory(self) -> None:
        if not self.data_manager:
            return
        products = self.kiosk.inventory_manager.get_all_products()
        self.data_manager.save_inventory_for_kiosk(self.kiosk_type, products)
