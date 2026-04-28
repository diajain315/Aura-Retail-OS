# Pattern: Decorator/Wrapper
import threading
from typing import Dict, List, Optional

class ThreadSafeInventory:

    
    def __init__(self, inventory_manager):

        self.inventory_manager = inventory_manager
        self._lock = threading.RLock()  # Reentrant lock for nested calls
        self._product_locks: Dict[str, threading.Lock] = {}
        
        # Create per-product locks for fine-grained locking
        for product in inventory_manager.get_all_products():
            self._product_locks[product["id"]] = threading.Lock()
    
    def _get_product_lock(self, product_id: str) -> threading.Lock:

        with self._lock:
            if product_id not in self._product_locks:
                self._product_locks[product_id] = threading.Lock()
            return self._product_locks[product_id]
    
    # ── Read operations (no lock needed for simple reads) ────────────────
    
    def get_product(self, product_id: str) -> Optional[dict]:

        return self.inventory_manager.get_product(product_id)
    
    def get_all_products(self) -> List[dict]:

        return self.inventory_manager.get_all_products()
    
    def get_available_stock(self, product_id: str) -> int:

        with self._get_product_lock(product_id):
            return self.inventory_manager.get_available_stock(product_id)
    
    def get_low_stock_products(self, threshold: int = 10) -> List[dict]:

        with self._lock:
            return self.inventory_manager.get_low_stock_products(threshold)
    
    # ── Write operations (require locks) ───────────────────────────────
    
    def reserve(self, product_id: str, quantity: int) -> bool:

        with self._get_product_lock(product_id):
            # Check if available
            if self.inventory_manager.get_available_stock(product_id) >= quantity:
                return self.inventory_manager.reserve(product_id, quantity)
            return False
    
    def release(self, product_id: str, quantity: int) -> None:

        with self._get_product_lock(product_id):
            self.inventory_manager.release(product_id, quantity)
    
    def deduct(self, product_id: str, quantity: int) -> bool:

        with self._get_product_lock(product_id):
            return self.inventory_manager.deduct(product_id, quantity)
    
    def restock(self, product_id: str, quantity: int) -> bool:

        with self._get_product_lock(product_id):
            return self.inventory_manager.restock(product_id, quantity)
    
    def set_hardware_unavailable(self, product_id: str, state: bool) -> None:

        with self._get_product_lock(product_id):
            self.inventory_manager.set_hardware_unavailable(product_id, state)
    
    # ── Admin operations (use global lock for data consistency) ─────────
    
    def add_product(self, product: dict) -> bool:

        with self._lock:
            result = self.inventory_manager.add_product(product)
            if result:
                self._product_locks[product["id"]] = threading.Lock()
            return result
    
    def remove_product(self, product_id: str) -> bool:

        with self._lock:
            return self.inventory_manager.remove_product(product_id)
    
    def add_stock(self, product_id: str, quantity: int) -> bool:

        with self._get_product_lock(product_id):
            return self.inventory_manager.add_stock(product_id, quantity)
    
    # ── Snapshot operations ────────────────────────────────────────────
    
    def get_snapshot(self) -> Dict[str, int]:

        with self._lock:
            return self.inventory_manager.get_snapshot()
    
    def restore_snapshot(self, snapshot: Dict[str, int]) -> None:

        with self._lock:
            self.inventory_manager.restore_snapshot(snapshot)
