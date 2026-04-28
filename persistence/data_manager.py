import json
import os
from typing import Any

class DataManager:

    BASE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")

    @classmethod
    def _path(cls, filename: str) -> str:
        return os.path.join(cls.BASE_DIR, filename)

    @classmethod
    def load(cls, filename: str) -> Any:
        path = cls._path(filename)
        if not os.path.exists(path):
            return {}
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    @classmethod
    def save(cls, filename: str, data: Any) -> None:
        os.makedirs(cls.BASE_DIR, exist_ok=True)
        with open(cls._path(filename), "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

    @classmethod
    def load_inventory(cls) -> list:
        data = cls.load("inventory.json")
        return data.get("products", [])

    @classmethod
    def save_inventory(cls, products: list) -> None:
        cls.save("inventory.json", {"products": products})

    @classmethod
    def _inventory_filename_for_kiosk(cls, kiosk_type: str) -> str:
        return f"inventory_{kiosk_type}.json"

    @classmethod
    def _default_products_for_kiosk(cls, kiosk_type: str, all_products: list) -> list:

        if kiosk_type == "pharmacy":
            allowed = {"medicine", "medical", "safety", "health"}
            subset = [p for p in all_products if p.get("category") in allowed]
            return subset or all_products

        if kiosk_type == "food":
            allowed = {"food", "beverage", "electronics"}
            subset = [p for p in all_products if p.get("category") in allowed]
            return subset or all_products

        if kiosk_type == "emergency":
            subset = [p for p in all_products if p.get("essential", False) or p.get("category") in {"safety", "medical"}]
            return subset or all_products

        return all_products

    @classmethod
    def load_inventory_for_kiosk(cls, kiosk_type: str) -> list:

        filename = cls._inventory_filename_for_kiosk(kiosk_type)
        data = cls.load(filename)
        products = data.get("products", []) if isinstance(data, dict) else []
        if products:
            return products

        all_products = cls.load_inventory()
        defaults = cls._default_products_for_kiosk(kiosk_type, all_products)
        cls.save(filename, {"products": defaults})
        return defaults

    @classmethod
    def save_inventory_for_kiosk(cls, kiosk_type: str, products: list) -> None:
        filename = cls._inventory_filename_for_kiosk(kiosk_type)
        cls.save(filename, {"products": products})

    @classmethod
    def load_config(cls) -> dict:
        return cls.load("config.json")

    @classmethod
    def save_config(cls, config: dict) -> None:
        cls.save("config.json", config)

    @classmethod
    def load_transactions(cls) -> dict:
        return cls.load("transactions.json")

    @classmethod
    def append_transaction(cls, txn: dict) -> None:
        data = cls.load_transactions()
        data.setdefault("transactions", []).append(txn)
        data["total_revenue"] = round(data.get("total_revenue", 0) + txn.get("total_amount", 0), 2)
        data["total_items_sold"] = data.get("total_items_sold", 0) + txn.get("quantity", 0)
        cls.save("transactions.json", data)
