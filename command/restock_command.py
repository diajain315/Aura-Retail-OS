from command.command import Command

class RestockCommand(Command):
    def __init__(self, kiosk, product_id: str, quantity: int):
        self.kiosk = kiosk
        self.product_id = product_id
        self.quantity = quantity
        self._executed = False

    def execute(self) -> dict:

        success = self.kiosk.inventory_manager.restock(self.product_id, self.quantity)
        if success:
            self._executed = True
            p = self.kiosk.inventory_manager.get_product(self.product_id)
            return {"success": True, "message": f" Restocked {p['name']} +{self.quantity}",
                    "product_id": self.product_id, "quantity_added": self.quantity,
                    "product_name": p["name"]}
        return {"success": False, "message": "Restock failed."}

    def undo(self) -> dict:
        if not self._executed:
            return {"success": False, "message": "Nothing to undo."}
        p = self.kiosk.inventory_manager.get_product(self.product_id)
        if p and p["quantity"] >= self.quantity:
            p["quantity"] -= self.quantity
            self._executed = False
            return {"success": True, "message": f"Restock undone for {p['name']}"}
        return {"success": False, "message": "Cannot undo restock."}

    def get_description(self) -> str:
        p = self.kiosk.inventory_manager.get_product(self.product_id)
        return f"Restock: {p['name'] if p else self.product_id} +{self.quantity}"
