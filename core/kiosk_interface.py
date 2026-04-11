from datetime import datetime
from core.kiosk import Kiosk
from command.purchase_command import PurchaseItemCommand
from command.restock_command import RestockCommand


class KioskInterface:

    def __init__(self, kiosk: Kiosk, registry, data_manager=None):
        self.kiosk = kiosk
        self.registry = registry
        self.data_manager = data_manager

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
            
            # Persist inventory + transaction log
            if self.data_manager:
                self.data_manager.append_transaction(result)
                self.data_manager.save_inventory(
                    self.kiosk.inventory_manager.get_all_products()
                )

        return result

    def refund_transaction(self) -> dict:
        """Undo the last transaction (Command undo + Memento restore)."""
        result = self.kiosk.undo_last()
        return result

    # ── Inventory ─────────────────────────────────────────────────────────

    def restock_inventory(self, product_id: str, quantity: int) -> dict:
        cmd = RestockCommand(self.kiosk, product_id, quantity)
        result = self.kiosk.execute_command(cmd)
        if result["success"]:
            # Persist inventory after restock
            if self.data_manager:
                self.data_manager.save_inventory(
                    self.kiosk.inventory_manager.get_all_products()
                )
        return result

    def restock_all(self, quantity: int = 50) -> None:
        """Restock every product to ensure stock."""
        for p in self.kiosk.inventory_manager.get_all_products():
            self.restock_inventory(p["id"], quantity)

    # ── Pricing ─────────────────────────────────────────────────────

    def set_pricing(self, strategy, strategy_name: str) -> None:
        self.kiosk.set_pricing_strategy(strategy)
        self.registry.current_pricing = strategy_name

        # Persist pricing for cross-session sync
        if self.data_manager:
            config = self.data_manager.load_config()
            config["current_pricing"] = strategy_name
            self.data_manager.save_config(config)

