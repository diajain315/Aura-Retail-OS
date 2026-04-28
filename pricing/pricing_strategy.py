# Pattern: Strategy (Abstract Strategy)
from abc import ABC, abstractmethod

class PricingStrategy(ABC):

    @abstractmethod
    def calculate_price(self, base_price: float) -> float:

        pass

    @abstractmethod
    def get_strategy_name(self) -> str:

        pass

    @abstractmethod
    def get_multiplier(self) -> float:

        pass

    def get_description(self) -> str:
        pct = int((self.get_multiplier() - 1) * 100)
        sign = "+" if pct >= 0 else ""
        return f"{self.get_strategy_name()} Pricing ({sign}{pct}%)"
