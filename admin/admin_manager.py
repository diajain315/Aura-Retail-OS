# Pattern: Observer (notifies UI of changes)
from typing import List, Dict, Optional, Callable
from events.events import InventoryUpdateEvent, PricingChangedEvent, TransactionEvent, RestockEvent
from events.event_system import EventBus

class AdminManager:

    
    def __init__(self, event_bus: EventBus, inventory_manager, data_manager=None, kiosk_type: str = "food"):

        self.event_bus = event_bus
        self.inventory_manager = inventory_manager
        self.data_manager = data_manager
        self.kiosk_type = kiosk_type
        self.observers: List[Callable] = []
        self._prices_changed_subscribers = []
        self._inventory_changed_subscribers = []
        
        # Subscribe to global events so admin side updates when others change state
        self.event_bus.subscribe(InventoryUpdateEvent, self._handle_inventory_event)
        self.event_bus.subscribe(PricingChangedEvent, self._handle_pricing_event)
        self.event_bus.subscribe(TransactionEvent, self._handle_transaction_event)
        self.event_bus.subscribe(RestockEvent, self._handle_restock_event)

    def _handle_transaction_event(self, event: TransactionEvent):
        if event.success:
            for prod in self.inventory_manager.get_all_products():
                if prod["name"] == event.product_name:
                    current_stock = prod.get("quantity", 0)
                    self.notify_inventory_changes(prod["id"], current_stock)
                    break

    def _handle_restock_event(self, event: RestockEvent):
        for prod in self.inventory_manager.get_all_products():
            if prod["name"] == event.product_name or prod["id"] == event.product_name:
                current_stock = prod.get("quantity", 0)
                self.notify_inventory_changes(prod["id"], current_stock)
                break

    def _handle_inventory_event(self, event: InventoryUpdateEvent):
        if event.product_id:
            if event.product_id == "ALL":
                for prod in self.inventory_manager.get_all_products():
                    self.notify_inventory_changes(prod["id"], prod.get("quantity", 0))
            else:
                product = self.inventory_manager.get_product(event.product_id)
                current_stock = product.get("quantity", 0) if product else 0
                self.notify_inventory_changes(event.product_id, current_stock)

    def _handle_pricing_event(self, event: PricingChangedEvent):
        if event.product_id:
            self.notify_price_changes(event.product_id, event.new_price)
        else:
            # Re-notify all if strategy changes
            self.notify_price_changes("ALL", 0.0)

    def _persist_inventory(self):
        if not self.data_manager:
            return
        self.data_manager.save_inventory_for_kiosk(self.kiosk_type, self.inventory_manager.get_all_products())
    
    def subscribe_to_price_changes(self, callback: Callable):

        self._prices_changed_subscribers.append(callback)
    
    def subscribe_to_inventory_changes(self, callback: Callable):

        self._inventory_changed_subscribers.append(callback)
    
    def notify_price_changes(self, product_id: str, new_price: float):

        for callback in self._prices_changed_subscribers:
            try:
                callback(product_id, new_price)
            except Exception as e:
                print(f"Error notifying price change subscriber: {e}")
    
    def notify_inventory_changes(self, product_id: str, new_stock: int):

        for callback in self._inventory_changed_subscribers:
            try:
                callback(product_id, new_stock)
            except Exception as e:
                print(f"Error notifying inventory change subscriber: {e}")
    
    def add_new_product(self, product_data: Dict) -> bool:

        try:
            # Validate required fields
            required_fields = ["id", "name", "description", "icon", "base_price", "quantity"]
            if not all(field in product_data for field in required_fields):
                return False
            
            # Add to inventory
            added = self.inventory_manager.add_product({
                "id": product_data["id"],
                "name": product_data["name"],
                "description": product_data["description"],
                "icon": product_data["icon"],
                "base_price": float(product_data["base_price"]),
                "quantity": int(product_data["quantity"]),
                "essential": product_data.get("essential", False)
            })
            if not added:
                return False
            
            # Publish event
            event = InventoryUpdateEvent(
                timestamp="",
                product_id=product_data["id"],
                change_type="ADD",
                quantity=int(product_data["quantity"]),
                reason="Admin added new product"
            )
            self.event_bus.publish(event)
            
            # Notify subscribers
            self.notify_inventory_changes(product_data["id"], int(product_data["quantity"]))
            self._persist_inventory()
            return True
            
        except Exception as e:
            print(f"Error adding product: {e}")
            return False
    
    def update_product_price(self, product_id: str, new_price: float) -> bool:

        try:
            product = self.inventory_manager.get_product(product_id)
            if not product:
                return False
            
            old_price = product.get("base_price", 0)
            product["base_price"] = float(new_price)
            
            # Publish event
            event = PricingChangedEvent(
                timestamp="",
                product_id=product_id,
                old_price=old_price,
                new_price=float(new_price),
                reason="Admin updated price"
            )
            self.event_bus.publish(event)
            
            # Notify subscribers
            self.notify_price_changes(product_id, float(new_price))
            self._persist_inventory()
            return True
            
        except Exception as e:
            print(f"Error updating product price: {e}")
            return False
    
    def update_product_stock(self, product_id: str, new_stock: int) -> bool:

        try:
            product = self.inventory_manager.get_product(product_id)
            if not product:
                return False
            
            current_stock = product.get("quantity", 0)
            change = new_stock - current_stock
            
            if change > 0:
                self.inventory_manager.add_stock(product_id, change)
                reason = f"Admin restocked (+{change})"
            elif change < 0:
                # Directly reduce quantity (similar to deduct but applied by admin)
                product["quantity"] = new_stock
                reason = f"Admin reduced stock ({change})"
            else:
                return True
            
            # Publish event
            event = InventoryUpdateEvent(
                timestamp="",
                product_id=product_id,
                change_type="RESTOCK" if change > 0 else "REDUCTION",
                quantity=abs(change),
                reason=reason
            )
            self.event_bus.publish(event)
            
            # Notify subscribers
            self.notify_inventory_changes(product_id, new_stock)
            self._persist_inventory()
            return True
            
        except Exception as e:
            print(f"Error updating product stock: {e}")
            return False
    
    def delete_product(self, product_id: str) -> bool:

        try:
            result = self.inventory_manager.remove_product(product_id)
            
            if result:
                # Publish event
                event = InventoryUpdateEvent(
                    timestamp="",
                    product_id=product_id,
                    change_type="DELETE",
                    quantity=0,
                    reason="Admin removed product"
                )
                self.event_bus.publish(event)
                
                # Notify subscribers
                self.notify_inventory_changes(product_id, 0)
                self._persist_inventory()
            
            return result
        except Exception as e:
            print(f"Error deleting product: {e}")
            return False
    
    def get_all_products(self) -> List[Dict]:

        return self.inventory_manager.get_all_products()
    
    def get_product(self, product_id: str) -> Optional[Dict]:

        return self.inventory_manager.get_product(product_id)
