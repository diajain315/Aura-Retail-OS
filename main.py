# Pattern: Factory pattern
import sys
import os
import tkinter as tk

# Ensure project root is on the path
sys.path.insert(0, os.path.dirname(__file__))

from core.central_registry import CentralRegistry
from core.kiosk_factory import GeneralKioskFactory, PharmacyKioskFactory, EmergencyReliefKioskFactory
from core.kiosk_interface import KioskInterface
from events.event_system import EventBus
from events.subscribers import MaintenanceService, SupplyChainSystem, CityMonitoringCenter
from persistence.data_manager import DataManager
from gui.app import AuraRetailOSApp
from gui.kiosk_selection import KioskSelectionScreen

def main():
    
    root = tk.Tk()
    selection_screen = KioskSelectionScreen(root)
    root.mainloop()
    root.destroy()
    
    kiosk_type = selection_screen.get_selected_kiosk()
    
    if not kiosk_type:
        return  # User closed without selecting
    
    
    config = DataManager.load_config()
    products = DataManager.load_inventory_for_kiosk(kiosk_type)

    
    registry = CentralRegistry()
    registry.initialize(config)

    
    event_bus = EventBus()

    
    #    GUI callbacks will be registered after app creation
    maintenance_svc = MaintenanceService(event_bus)
    supply_chain    = SupplyChainSystem(event_bus)
    city_monitor    = CityMonitoringCenter(event_bus)

    
    if kiosk_type == "food":
        factory = GeneralKioskFactory()
    elif kiosk_type == "pharmacy":
        factory = PharmacyKioskFactory()
    elif kiosk_type == "emergency":
        factory = EmergencyReliefKioskFactory()
    else:
        factory = GeneralKioskFactory()
    
    kiosk = factory.create_kiosk(products, event_bus)

    
    ki = KioskInterface(
        kiosk,
        registry,
        data_manager=DataManager,
        kiosk_type=kiosk_type,
    )

    
    app = AuraRetailOSApp(ki, registry)

    # Wire subscriber GUI callbacks after app is created
    maintenance_svc.gui_callback = app._log
    supply_chain.gui_callback    = app._log
    city_monitor.gui_callback    = app._log

    app.run()

if __name__ == "__main__":
    main()
