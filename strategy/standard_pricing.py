from strategy.pricing_strategy import PricingStrategy

class StandardPricing(PricingStrategy):
    """Standard prices — uses a base multiplier, typically 1.0."""

    def __init__(self, multiplier: float = 1.0):
        self.multiplier = multiplier

    def calculate_price(self, base_price: float) -> float:
        return round(base_price * self.multiplier, 2)

    def get_strategy_name(self) -> str:
        return "Standard"

    def get_multiplier(self) -> float:
        return self.multiplier
