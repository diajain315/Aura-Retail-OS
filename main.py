import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from persistence.data_manager import DataManager
from gui.login import LoginWindow


def main():
    # ── Step 1: Login ─────────────────────────────────────────────────────
    # Skip login screen, default to user directly
    user = {"name": "Customer", "role": "user", "username": "guest"}

    # ── Step 2: Load persisted data ───────────────────────────────────────
    config   = DataManager.load_config()
    products = DataManager.load_inventory() 

    # ── Step 3: Singleton registry ────────────────────────────────────────
    from core.central_registry import CentralRegistry
    registry = CentralRegistry()
    registry.initialize(config)

    # ── Step 4: Build kiosk ───────────────────────────────────────────────
    from core.kiosk import Kiosk
    from inventory.inventory_manager import InventoryManager
    from strategy.standard_pricing import StandardPricing

    kiosk = Kiosk(
        kiosk_id="AURA-GEN-001",
        name="Aura Retail Prototype",
        location="Central Plaza",
        inventory_manager=InventoryManager(products),
        initial_pricing_strategy=StandardPricing()
    )

    # ── Step 5: ────────────────────────────────────────────────────
    from core.kiosk_interface import KioskInterface
    ki = KioskInterface(kiosk, registry, data_manager=DataManager)

    # ── Step 6: Launch GUI (pass authenticated user) ──────────────────────
    from gui.app import AuraRetailOSApp
    app = AuraRetailOSApp(ki, registry, user=user)

    app.run()


if __name__ == "__main__":
    main()
