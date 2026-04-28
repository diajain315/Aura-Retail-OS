import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

from gui.styles import *
from gui.admin_dialogs import AdminLoginDialog, AdminPanel
from admin.admin_authenticator import AdminAuthenticator
from admin.admin_manager import AdminManager
from pricing.standard_pricing import StandardPricing
from pricing.discounted_pricing import DiscountedPricing
from pricing.emergency_pricing import EmergencyPricing
from state.active_state import ActiveState
from state.power_saving_state import PowerSavingState
from state.maintenance_state import MaintenanceState
from state.emergency_state import EmergencyLockdownState

# Event color tags for the log widget
EVENT_TAG_COLORS = {
    "✅": SUCCESS,
    "❌": DANGER,
    "⚠":  WARNING,
    "🔧": WARNING,
    "🚨": DANGER,
    "🔄": PRIMARY,
    "💰": "#A9DFBF",
    "📦": SUCCESS,
    "🏙": TEXT_MUTED,
    "🔙": WARNING,
    "⚙":  PRIMARY,
    "🚒": DANGER,
    "📧": TEXT_MUTED,
}

class AuraRetailOSApp:

    def __init__(self, kiosk_interface, registry):
        self.ki = kiosk_interface
        self.registry = registry
        self.event_history = []
        
        # Initialize admin components
        self.admin_auth = AdminAuthenticator()
        self.admin_manager = AdminManager(
            kiosk_interface.kiosk.event_bus,
            kiosk_interface.kiosk.inventory_manager,
            data_manager=kiosk_interface.data_manager,
            kiosk_type=kiosk_interface.kiosk_type,
        )
        self.admin_panel = None
        self.is_admin = False
        
        self.root = tk.Tk()
        self._setup_window()
        self._build_ui()
        self._subscribe_to_events()
        self._start_clock()

    # ── Window setup ───────────────────────────────────────────────────────

    def _setup_window(self):
        self.root.title("Aura Retail OS v2.0 — Smart Kiosk Simulation")
        self.root.geometry("1280x780")
        self.root.minsize(1100, 680)
        self.root.configure(bg=BG)
        try:
            self.root.state("zoomed")
        except Exception:
            pass

    # ── UI Construction ────────────────────────────────────────────────────

    def _build_ui(self):
        self._build_header()
        self._build_main_area()
        self._build_status_bar()

    def _build_header(self):
        hdr = tk.Frame(self.root, bg=SURFACE, height=64)
        hdr.pack(fill=tk.X, pady=(0, 2))
        hdr.pack_propagate(False)

        # Left: logo + name
        left = tk.Frame(hdr, bg=SURFACE)
        left.pack(side=tk.LEFT, padx=PAD)
        tk.Label(left, text="⬡", font=("Segoe UI Emoji", 28), bg=SURFACE,
                 fg=PRIMARY).pack(side=tk.LEFT)
        title_fr = tk.Frame(left, bg=SURFACE)
        title_fr.pack(side=tk.LEFT, padx=(6, 0))
        tk.Label(title_fr, text="AURA RETAIL OS", font=FONT_TITLE,
                 bg=SURFACE, fg=TEXT).pack(anchor=tk.W)
        tk.Label(title_fr, text=f"Smart Kiosk · {self.registry.location}",
                 font=FONT_SMALL, bg=SURFACE, fg=TEXT_MUTED).pack(anchor=tk.W)

        # Centre: mode badge
        self.mode_badge = tk.Label(hdr, text="● ACTIVE", font=FONT_BTN,
                                   bg=SUCCESS, fg=BG, padx=10, pady=4,
                                   relief=tk.FLAT)
        self.mode_badge.pack(side=tk.LEFT, padx=20)

        # Right: admin button + clock
        right = tk.Frame(hdr, bg=SURFACE)
        right.pack(side=tk.RIGHT, padx=PAD)
        
        admin_btn = tk.Button(right, text="👨‍💼 ADMIN", font=FONT_BTN,
                              bg=WARNING if not self.is_admin else SUCCESS,
                              fg=BG, relief=tk.FLAT, cursor="hand2",
                              command=self._admin_login)
        admin_btn.pack(side=tk.LEFT, padx=(0, 10))
        self._bind_hover(admin_btn, WARNING, "#E67E22")
        self.admin_btn = admin_btn
        
        self.clock_lbl = tk.Label(right, text="", font=FONT_BODY, bg=SURFACE, fg=TEXT_MUTED)
        self.clock_lbl.pack(side=tk.LEFT)

    def _build_main_area(self):
        container = tk.Frame(self.root, bg=BG)
        container.pack(fill=tk.BOTH, expand=True, padx=PAD, pady=(0, PAD_SM))
        container.columnconfigure(0, weight=3)
        container.columnconfigure(1, weight=2)
        container.columnconfigure(2, weight=3)
        container.rowconfigure(0, weight=1)

        self._build_products_panel(container)
        self._build_user_hint(container)
        self._build_user_log(container)

    def _build_user_hint(self, parent):
        frame = tk.Frame(parent, bg=SURFACE, padx=PAD, pady=PAD)
        frame.grid(row=0, column=1, sticky="nsew", padx=(0, PAD_SM))
        tk.Label(frame, text="Quick Purchase", font=FONT_HEADING,
                 bg=SURFACE, fg=TEXT).pack(anchor=tk.W, pady=(0, PAD_SM))
        tk.Label(frame, text="Choose a kiosk item to buy. Admin tools are available through the login button.",
                 font=FONT_BODY, bg=SURFACE, fg=TEXT_MUTED, wraplength=260, justify=tk.LEFT).pack(anchor=tk.W)
        tk.Label(frame, text="Fast, simple, and ready for sales.",
                 font=FONT_SMALL, bg=SURFACE, fg=TEXT_MUTED).pack(anchor=tk.W, pady=(PAD, 0))

        # Refund Button
        refund_btn = tk.Button(frame, text="🔙 Refund Last Purchase", font=FONT_BTN, bg=WARNING, fg=BG,
                               relief=tk.FLAT, cursor="hand2", padx=8, pady=6,
                               command=self._sim_undo)
        refund_btn.pack(fill=tk.X, pady=(PAD * 2, 0))
        self._bind_hover(refund_btn, WARNING, "#E67E22")

    def _build_user_log(self, parent):
        frame = tk.Frame(parent, bg=SURFACE, padx=PAD, pady=PAD)
        frame.grid(row=0, column=2, sticky="nsew")

        tk.Label(frame, text="📋 Event Log", font=FONT_HEADING,
                 bg=SURFACE, fg=TEXT).pack(anchor=tk.W, pady=(0, PAD_SM))

        self.log_text = tk.Text(frame, bg=LOG_BG, fg=TEXT, font=FONT_MONO,
                                state=tk.DISABLED, wrap=tk.WORD,
                                relief=tk.FLAT, padx=6, pady=6)
        log_scroll = ttk.Scrollbar(frame, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=log_scroll.set)
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        log_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        for icon, color in EVENT_TAG_COLORS.items():
            self.log_text.tag_configure(icon, foreground=color)
        self.log_text.tag_configure("muted", foreground=TEXT_MUTED)
        self.log_text.tag_configure("success", foreground=SUCCESS)
        self.log_text.tag_configure("danger", foreground=DANGER)

        tk.Button(frame, text="Clear Log", font=FONT_SMALL, bg=BORDER, fg=TEXT_MUTED,
                  relief=tk.FLAT, cursor="hand2", command=self._clear_log).pack(fill=tk.X, pady=(PAD_SM, 0))

        self._log("🚀 Aura Retail OS v2.0 started", "success")
        self._log(f"📍 Kiosk: {self.registry.kiosk_name} @ {self.registry.location}", "muted")
        self._log("──────────────────────────────────", "muted")

    # ── Products Panel ─────────────────────────────────────────────────────

    def _build_products_panel(self, parent):
        frame = tk.Frame(parent, bg=SURFACE, padx=PAD, pady=PAD)
        frame.grid(row=0, column=0, sticky="nsew", padx=(0, PAD_SM))

        tk.Label(frame, text="🛒  Products", font=FONT_HEADING,
                 bg=SURFACE, fg=TEXT).pack(anchor=tk.W, pady=(0, PAD_SM))

        # Scrollable canvas
        canvas = tk.Canvas(frame, bg=SURFACE, highlightthickness=0)
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        self.products_frame = tk.Frame(canvas, bg=SURFACE)

        self.products_frame.bind("<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self.products_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Bind mousewheel
        canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(-1*(e.delta//120), "units"))

        self._populate_products()

    def _populate_products(self):
        for widget in self.products_frame.winfo_children():
            widget.destroy()

        products = self.ki.kiosk.inventory_manager.get_all_products()
        cols = 2
        for i, p in enumerate(products):
            row, col = divmod(i, cols)
            self._make_product_card(self.products_frame, p, row, col)

    def _make_product_card(self, parent, product, row, col):
        pid = product["id"]
        available = self.ki.kiosk.inventory_manager.get_available_stock(pid)
        price = self.ki.kiosk.pricing_strategy.calculate_price(product["base_price"])
        essential = product.get("essential", False)

        card = tk.Frame(parent, bg=CARD, pady=PAD, padx=PAD,
                        relief=tk.FLAT, bd=1)
        card.grid(row=row, column=col, sticky="nsew", padx=PAD_SM//2, pady=PAD_SM//2)
        parent.columnconfigure(col, weight=1)

        # Essential badge
        if essential:
            tk.Label(card, text="ESSENTIAL", font=("Segoe UI", 7, "bold"),
                     bg=SUCCESS, fg=BG, padx=4).pack(anchor=tk.E)

        # Icon
        tk.Label(card, text=product["icon"], font=FONT_ICON,
                 bg=CARD, fg=TEXT).pack()

        # Name
        tk.Label(card, text=product["name"], font=FONT_HEADING,
                 bg=CARD, fg=TEXT).pack(pady=(0, 2))

        # Description
        tk.Label(card, text=product["description"], font=FONT_SMALL,
                 bg=CARD, fg=TEXT_MUTED, wraplength=130).pack()

        # Price
        self_price_lbl = tk.Label(card, text=f"Rs.{price:.2f}", font=FONT_PRICE,
                                  bg=CARD, fg=PRIMARY)
        self_price_lbl.pack(pady=(4, 0))

        # Stock indicator
        stock_color = DANGER if available <= 5 else WARNING if available <= 10 else SUCCESS
        tk.Label(card, text=f"In Stock: {available}", font=FONT_SMALL,
                 bg=CARD, fg=stock_color).pack()

        # User-side shopping action always stays as BUY.
        btn_state = tk.NORMAL if available > 0 else tk.DISABLED
        btn_text = "BUY" if available > 0 else "OUT OF STOCK"
        btn = tk.Button(card, text=btn_text, font=FONT_BTN,
                        bg=PRIMARY if available > 0 else BORDER, fg=TEXT,
                        relief=tk.FLAT, cursor="hand2", padx=8, pady=4,
                        state=btn_state,
                        command=lambda p=product["id"]: self._buy(p))
        btn.pack(fill=tk.X, pady=(PAD_SM, 0))
        self._bind_hover(btn, PRIMARY, PRIMARY_DK)

    # ── Event Log ──────────────────────────────────────────────────────────

    def _build_event_log(self, parent):
        frame = tk.Frame(parent, bg=SURFACE, padx=PAD, pady=PAD)
        frame.grid(row=0, column=2, sticky="nsew")

        tk.Label(frame, text="📋  Event Log", font=FONT_HEADING,
                 bg=SURFACE, fg=TEXT).pack(anchor=tk.W, pady=(0, PAD_SM))

        self.log_text = tk.Text(frame, bg=LOG_BG, fg=TEXT, font=FONT_MONO,
                                 state=tk.DISABLED, wrap=tk.WORD,
                                 relief=tk.FLAT, padx=6, pady=6)
        log_scroll = ttk.Scrollbar(frame, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=log_scroll.set)
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        log_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        # Define colour tags
        for icon, color in EVENT_TAG_COLORS.items():
            self.log_text.tag_configure(icon, foreground=color)
        self.log_text.tag_configure("muted", foreground=TEXT_MUTED)
        self.log_text.tag_configure("success", foreground=SUCCESS)
        self.log_text.tag_configure("danger", foreground=DANGER)

        # Clear button
        tk.Button(frame, text="Clear Log", font=FONT_SMALL, bg=BORDER, fg=TEXT_MUTED,
                  relief=tk.FLAT, cursor="hand2",
                  command=self._clear_log).pack(fill=tk.X, pady=(PAD_SM, 0))

        self._log("🚀 Aura Retail OS v2.0 started", "success")
        self._log(f"📍 Kiosk: {self.registry.kiosk_name} @ {self.registry.location}", "muted")
        self._log("──────────────────────────────────", "muted")

    # ── Status Bar ─────────────────────────────────────────────────────────

    def _build_status_bar(self):
        bar = tk.Frame(self.root, bg=SURFACE, height=30)
        bar.pack(fill=tk.X, side=tk.BOTTOM)
        bar.pack_propagate(False)

        current_mode = self.ki.kiosk.state.get_mode_name()
        current_pricing = self.ki.kiosk.pricing_strategy.get_strategy_name()

        self.status_mode_lbl  = tk.Label(bar, text=f"Mode: {current_mode}", font=FONT_STATUS,
                                          bg=SURFACE, fg=SUCCESS)
        self.status_mode_lbl.pack(side=tk.LEFT, padx=PAD)

        tk.Label(bar, text="|", bg=SURFACE, fg=BORDER).pack(side=tk.LEFT)

        self.status_price_lbl = tk.Label(bar, text=f"Pricing: {current_pricing}", font=FONT_STATUS,
                                          bg=SURFACE, fg=TEXT_MUTED)
        self.status_price_lbl.pack(side=tk.LEFT, padx=PAD)

        tk.Label(bar, text="City: Zephyrus · Aura Retail OS © 2025",
                 font=FONT_STATUS, bg=SURFACE, fg=BORDER).pack(side=tk.RIGHT, padx=PAD)

    # ── Event Subscriptions ────────────────────────────────────────────────

    def _subscribe_to_events(self):
        from events.events import (
            TransactionEvent, LowStockEvent, HardwareFailureEvent,
            EmergencyModeActivatedEvent, ModeChangedEvent, PricingChangedEvent,
            RestockEvent, FailureHandledEvent, InventoryUpdateEvent
        )
        bus = self.ki.kiosk.event_bus
        bus.subscribe(TransactionEvent,          self._on_transaction)
        bus.subscribe(LowStockEvent,             self._on_low_stock)
        bus.subscribe(HardwareFailureEvent,      self._on_hw_failure)
        bus.subscribe(EmergencyModeActivatedEvent, self._on_emergency)
        bus.subscribe(ModeChangedEvent,          self._on_mode_changed)
        bus.subscribe(PricingChangedEvent,       self._on_pricing_changed)
        bus.subscribe(RestockEvent,              self._on_restock)
        bus.subscribe(InventoryUpdateEvent,      self._on_inventory_update)

    def _on_transaction(self, ev):
        from events.events import TransactionEvent
        self._log(str(ev))
        self._update_stats()
        self._populate_products()

    def _on_low_stock(self, ev):
        self._log(str(ev))

    def _on_hw_failure(self, ev):
        self._log(str(ev))

    def _on_emergency(self, ev):
        self._log(str(ev))

    def _on_mode_changed(self, ev):
        self._log(str(ev))
        self._refresh_mode_ui(ev.new_mode)

    def _on_pricing_changed(self, ev):
        self._log(str(ev))
        self._populate_products()
        if ev.new_strategy:
            self._refresh_pricing_ui(ev.new_strategy)

    def _on_restock(self, ev):
        self._log(str(ev))
        self._populate_products()

    def _on_inventory_update(self, ev):
        self._log(str(ev))
        self._populate_products()

    # ── Actions ────────────────────────────────────────────────────────────

    def _buy(self, product_id):
        result = self.ki.purchase_item(product_id, 1)
        self._populate_products()
        if not result["success"]:
            messagebox.showwarning("Purchase Failed", result["message"])

    def _change_mode(self, name, state_obj):
        self.ki.set_mode(state_obj, name)

    def _change_pricing(self, name, strategy):
        self.ki.set_pricing(strategy, name)

    def _sim_failure(self):
        import random
        components = ["Dispenser Motor", "Payment Reader", "Touch Screen", "Refrigeration Unit"]
        severities = ["low", "medium", "high", "critical"]
        comp = random.choice(components)
        sev = random.choice(severities)
        self._log(f"\n── Hardware Failure Simulation ──────────────────", "muted")
        self.ki.trigger_hardware_failure(comp, sev, log_cb=self._log)

    def _sim_emergency(self):
        # Emergency simulation goes through Admin Panel normally. 
        # Left here just in case.
        pass

    def _sim_restock(self):
        self._log("\n── Restocking All Products ──────────────────────", "muted")
        self.ki.restock_all(50)

    def _sim_undo(self):
        result = self.ki.refund_transaction()
        if result.get("success"):
            self._log(result["message"])
            self._update_stats()
            self._populate_products()
        else:
            messagebox.showinfo("Undo", result.get("message", "Nothing to undo."))

    def _sim_diagnostics(self):
        diag = self.ki.run_diagnostics()
        self._log(f"\n── Diagnostics ──────────────────────────────────", "muted")
        for k, v in diag.items():
            self._log(f"  {k}: {v}", "muted")

    # ── Helpers ────────────────────────────────────────────────────────────

    def _log(self, message: str, tag: str = None):
        self.event_history.append((message, tag))
        if tag is None:
            for icon in EVENT_TAG_COLORS:
                if icon in message:
                    tag = icon
                    break
        if hasattr(self, "log_text") and self.log_text.winfo_exists():
            self.log_text.configure(state=tk.NORMAL)
            self.log_text.insert(tk.END, message + "\n", tag or "")
            self.log_text.see(tk.END)
            self.log_text.configure(state=tk.DISABLED)
        if self.admin_panel and hasattr(self.admin_panel, "append_log"):
            self.admin_panel.append_log(message, tag)

    def _clear_log(self):
        self.log_text.configure(state=tk.NORMAL)
        self.log_text.delete("1.0", tk.END)
        self.log_text.configure(state=tk.DISABLED)

    def _update_stats(self):
        # Stats are now handled in Admin Panel
        pass

    def _refresh_mode_ui(self, name: str):
        color = MODE_COLORS.get(name, TEXT)
        self.mode_badge.config(text=f"● {name.upper()}", bg=color,
                               fg=BG if name in ("Active", "Power Saving") else TEXT)
        self.status_mode_lbl.config(text=f"Mode: {name}", fg=color)

    def _refresh_pricing_ui(self, name: str):
        color = PRICING_COLORS.get(name, TEXT)
        self.status_price_lbl.config(text=f"Pricing: {name}", fg=color)

    def _section(self, parent, title: str):
        tk.Label(parent, text=title.upper(), font=("Segoe UI", 9, "bold"),
                 bg=SURFACE, fg=TEXT_MUTED).pack(anchor=tk.W, pady=(0, 2))

    def _bind_hover(self, widget, normal_bg, hover_bg):
        widget.bind("<Enter>", lambda e: widget.config(bg=hover_bg))
        widget.bind("<Leave>", lambda e: widget.config(bg=normal_bg))

    def _start_clock(self):
        now = datetime.now().strftime("%a %d %b   %H:%M:%S")
        self.clock_lbl.config(text=now)
        self.root.after(1000, self._start_clock)

    # ── Admin Operations ───────────────────────────────────────────────────

    def _admin_login(self):

        if self.is_admin:
            # Logout
            self.admin_auth.logout()
            self.is_admin = False
            self.admin_btn.config(bg=WARNING)
            if self.admin_panel:
                try:
                    self.admin_panel.panel.destroy()
                except:
                    pass
                self.admin_panel = None
            self._populate_products()
            messagebox.showinfo("Logout", "Admin session ended")
        else:
            # Show login dialog
            dialog = AdminLoginDialog(self.root, self.admin_auth, 
                                      on_success=self._on_admin_login_success)
            self.root.wait_window(dialog.dialog)
    
    def _on_admin_login_success(self):

        self.is_admin = True
        self.admin_btn.config(bg=SUCCESS)
        self._populate_products()
        # Open admin panel
        self.admin_panel = AdminPanel(self.root, self.admin_manager, self.ki,
                                      on_close=self._on_admin_panel_close)
        for message, tag in self.event_history:
            self.admin_panel.append_log(message, tag)
    
    def _on_admin_panel_close(self):

        self.admin_panel = None

    def _bind_hover(self, btn, normal_color, hover_color):

        btn.bind("<Enter>", lambda e: btn.config(bg=hover_color))
        btn.bind("<Leave>", lambda e: btn.config(bg=normal_color))

    def run(self):
        self.root.mainloop()
