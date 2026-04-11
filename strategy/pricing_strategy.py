from abc import ABC, abstractmethod

class PricingStrategy(ABC):

    @abstractmethod
    def calculate_price(self, base_price: float) -> float:
        """Compute the final sale price from the item's base price."""
        pass

    @abstractmethod
    def get_strategy_name(self) -> str:
        """Human-readable name for the UI."""
        pass

    @abstractmethod
    def get_multiplier(self) -> float:
        """Price multiplier relative to base price."""
        pass

    def get_description(self) -> str:
        pct = int((self.get_multiplier() - 1) * 100)
        sign = "+" if pct >= 0 else ""
        return f"{self.get_strategy_name()} Pricing ({sign}{pct}%)"
