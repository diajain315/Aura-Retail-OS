from typing import Dict, List, Optional

class InventoryManager:

    def __init__(self, products: List[dict]):
        self._products: Dict[str, dict] = {}      # product_id -> product data
        self._reserved: Dict[str, int] = {}        # items held in active txns
        self._hw_unavailable: Dict[str, bool] = {} # marked unavailable by hardware

        for p in products:
            pid = p["id"]
            self._products[pid] = p.copy()
            self._reserved[pid] = 0
            self._hw_unavailable[pid] = False

    # ── Read ───────────────────────────────────────────────────────────────

    def get_product(self, product_id: str) -> Optional[dict]:
        return self._products.get(product_id)

    def get_all_products(self) -> List[dict]:
        return list(self._products.values())

    def get_available_stock(self, product_id: str) -> int:
        if self._hw_unavailable.get(product_id, False):
            return 0
        p = self._products.get(product_id)
        if not p:
            return 0
        return max(0, p["quantity"] - self._reserved.get(product_id, 0))

    def get_low_stock_products(self, threshold: int = 10) -> List[dict]:
        return [p for p in self._products.values() if p["quantity"] <= threshold]

    # ── Write ──────────────────────────────────────────────────────────────

    def reserve(self, product_id: str, quantity: int) -> bool:
        if self.get_available_stock(product_id) >= quantity:
            self._reserved[product_id] = self._reserved.get(product_id, 0) + quantity
            return True
        return False

    def release(self, product_id: str, quantity: int) -> None:

        self._reserved[product_id] = max(0, self._reserved.get(product_id, 0) - quantity)

    def deduct(self, product_id: str, quantity: int) -> bool:

        p = self._products.get(product_id)
        if not p:
            return False
        self.release(product_id, quantity)
        p["quantity"] -= quantity
        return True

    def restock(self, product_id: str, quantity: int) -> bool:
        p = self._products.get(product_id)
        if not p:
            return False
        p["quantity"] += quantity
        return True

    def set_hardware_unavailable(self, product_id: str, state: bool) -> None:
        self._hw_unavailable[product_id] = state

    # ── Snapshot (Memento support) ─────────────────────────────────────────

    def get_snapshot(self) -> Dict[str, int]:

        return {pid: p["quantity"] for pid, p in self._products.items()}

    def restore_snapshot(self, snapshot: Dict[str, int]) -> None:

        for pid, qty in snapshot.items():
            if pid in self._products:
                self._products[pid]["quantity"] = qty

    def add_product(self, product: dict) -> bool:

        if product["id"] in self._products:
            return False  # Product already exists
        self._products[product["id"]] = product.copy()
        self._reserved[product["id"]] = 0
        self._hw_unavailable[product["id"]] = False
        return True

    def remove_product(self, product_id: str) -> bool:

        if product_id not in self._products:
            return False
        del self._products[product_id]
        del self._reserved[product_id]
        del self._hw_unavailable[product_id]
        return True

    def add_stock(self, product_id: str, quantity: int) -> bool:

        p = self._products.get(product_id)
        if not p:
            return False
        p["quantity"] += quantity
        return True
