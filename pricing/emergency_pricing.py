# Pattern: Strategy (Concrete Strategy)
from pricing.pricing_strategy import PricingStrategy

class EmergencyPricing(PricingStrategy):

    def __init__(self, surge_rate: float = 0.50):
        self.surge_rate = surge_rate  

    def calculate_price(self, base_price: float) -> float:
        return round(base_price * (1 + self.surge_rate), 2)

    def get_strategy_name(self) -> str:
        return "Emergency"

    def get_multiplier(self) -> float:
        return 1.0 + self.surge_rate
