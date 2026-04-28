# Pattern: Strategy (Concrete Strategy)
from pricing.pricing_strategy import PricingStrategy

class DiscountedPricing(PricingStrategy):

    def __init__(self, discount_rate: float = 0.20):
        self.discount_rate = discount_rate  

    def calculate_price(self, base_price: float) -> float:
        return round(base_price * (1 - self.discount_rate), 2)

    def get_strategy_name(self) -> str:
        return "Discounted"

    def get_multiplier(self) -> float:
        return 1.0 - self.discount_rate
