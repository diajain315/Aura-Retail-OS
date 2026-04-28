# Pattern: Memento
from dataclasses import dataclass
from typing import Dict

@dataclass
class TransactionMemento:

    transaction_id: str
    inventory_snapshot: Dict[str, int]
    product_id: str
    quantity: int
    amount: float
    timestamp: str

    def get_snapshot(self) -> Dict[str, int]:

        return dict(self.inventory_snapshot)

    def __str__(self):
        return f"Memento[{self.transaction_id}] @ {self.timestamp}"
