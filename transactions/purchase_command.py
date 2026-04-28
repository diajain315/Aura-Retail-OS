# Pattern: Command (Concrete) + Memento (rollback)
import uuid
from datetime import datetime
from transactions.command import Command
from transactions.transaction_memento import TransactionMemento

class PurchaseItemCommand(Command):

    def __init__(self, kiosk, product_id: str, quantity: int, pricing_strategy):
        self.kiosk = kiosk
        self.product_id = product_id
        self.quantity = quantity
        self.pricing_strategy = pricing_strategy
        self.transaction_id = str(uuid.uuid4())[:8].upper()
        self._memento: TransactionMemento = None
        self._result: dict = None

    def execute(self) -> dict:
        inv = self.kiosk.inventory_manager
        product = inv.get_product(self.product_id)

        if not product:
            return {"success": False, "message": "Product not found.", "transaction_id": self.transaction_id}

        # Ask current state whether purchase is allowed
        state_check = self.kiosk.state.handle_purchase(self.kiosk, self.product_id, self.quantity)
        if not state_check["allowed"]:
            return {"success": False, "message": state_check["message"], "transaction_id": self.transaction_id}

        # Enforce quantity limits from state
        max_qty = state_check.get("max_quantity")
        actual_qty = min(self.quantity, max_qty) if max_qty else self.quantity

        if inv.get_available_stock(self.product_id) < actual_qty:
            return {"success": False, "message": f"Insufficient stock (available: {inv.get_available_stock(self.product_id)}).",
                    "transaction_id": self.transaction_id}

        # Save Memento BEFORE deducting (Memento Pattern)
        self._memento = TransactionMemento(
            transaction_id=self.transaction_id,
            inventory_snapshot=inv.get_snapshot(),
            product_id=self.product_id,
            quantity=actual_qty,
            amount=self.pricing_strategy.calculate_price(product["base_price"]) * actual_qty,
            timestamp=datetime.now().strftime("%H:%M:%S")
        )

        # Execute the deduction
        unit_price = self.pricing_strategy.calculate_price(product["base_price"])
        total = round(unit_price * actual_qty, 2)
        inv.deduct(self.product_id, actual_qty)

        self._result = {
            "success": True,
            "transaction_id": self.transaction_id,
            "product_id": self.product_id,
            "product_name": product["name"],
            "quantity": actual_qty,
            "unit_price": unit_price,
            "total_amount": total,
            "message": f"✅ Purchased {product['name']} x{actual_qty} for Rs.{total:.2f}",
            "state_note": state_check.get("message", "")
        }
        return self._result

    def undo(self) -> dict:

        if not self._memento or not (self._result and self._result.get("success")):
            return {"success": False, "message": "Nothing to undo."}
        self.kiosk.inventory_manager.restore_snapshot(self._memento.get_snapshot())
        return {
            "success": True,
            "message": f"🔙 Rolled back: {self._result['product_name']} x{self._result['quantity']} — Rs.{self._result['total_amount']:.2f} refunded",
            "refund_amount": self._result["total_amount"],
            "product_id": self._result["product_id"],
            "quantity": self._result["quantity"]
        }

    def get_description(self) -> str:
        p = self.kiosk.inventory_manager.get_product(self.product_id)
        name = p["name"] if p else self.product_id
        return f"Purchase: {name} x{self.quantity}"
