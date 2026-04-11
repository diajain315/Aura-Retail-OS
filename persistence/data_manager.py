import json
import os
from typing import Any

class DataManager:
    """Reads and writes JSON data files for system state persistence."""

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

    @classmethod
    def load_users(cls) -> list:
        data = cls.load("users.json")
        return data.get("users", [])

    @classmethod
    def verify_user(cls, username: str, password_hash: str) -> dict:
        """Return user dict if credentials match, else None."""
        for user in cls.load_users():
            if user["username"] == username and user["password"] == password_hash:
                return user
        return None

    # ── Restock Orders ────────────────────────────────────────────────────

    @classmethod
    def load_restock_orders(cls) -> list:
        data = cls.load("restock_orders.json")
        return data.get("restock_orders", [])

    @classmethod
    def save_restock_order(cls, order: dict) -> None:
        """Append a new restock/reorder request to restock_orders.json."""
        data = cls.load("restock_orders.json")
        data.setdefault("restock_orders", []).append(order)
        cls.save("restock_orders.json", data)
