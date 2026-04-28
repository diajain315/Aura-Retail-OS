# Pattern: Singleton
class CentralRegistry:

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def initialize(self, config: dict) -> None:
        if self._initialized:
            return
        self.kiosk_id: str = config.get("kiosk_id", "AURA-000")
        self.kiosk_name: str = config.get("kiosk_name", "Aura Kiosk")
        self.location: str = config.get("location", "Unknown")
        self.city: str = config.get("city", "Zephyrus")
        self.version: str = config.get("version", "2.0")
        self.current_mode: str = config.get("current_mode", "active")
        self.current_pricing: str = config.get("current_pricing", "standard")
        self.emergency_purchase_limit: int = config.get("emergency_purchase_limit", 2)
        self.low_stock_threshold: int = config.get("low_stock_threshold", 10)
        self.total_revenue: float = 0.0
        self.total_items_sold: int = 0
        self._initialized = True

    def update_stats(self, amount: float, items: int) -> None:
        self.total_revenue = round(self.total_revenue + amount, 2)
        self.total_items_sold += items

    def get_summary(self) -> dict:
        return {
            "kiosk_id": self.kiosk_id,
            "kiosk_name": self.kiosk_name,
            "location": self.location,
            "mode": self.current_mode,
            "pricing": self.current_pricing,
            "revenue": self.total_revenue,
            "items_sold": self.total_items_sold,
        }

    @classmethod
    def reset(cls):
        cls._instance = None
