import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

from gui.styles import *
from strategy.standard_pricing import StandardPricing
from strategy.discounted_pricing import DiscountedPricing
from strategy.emergency_pricing import EmergencyPricing

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
    """Main application window."""

    def __init__(self, kiosk_interface, registry, user: dict = None, parent_window = None):
        self.ki = kiosk_interface
        self.registry = registry
        self.user = user or {"name": "Guest", "role": "user", "username": "guest"}
        self.is_admin = self.user.get("role") == "admin"
        # Stat label refs — only populated when control panel is built (admin only)
        self.revenue_lbl    = None
        self.sold_lbl       = None
        self.txn_count_lbl  = None
        self._txn_count     = 0
        if parent_window:
            self.root = tk.Toplevel(parent_window)
        else:
            self.root = tk.Tk()
        self._setup_window()
        self._build_ui()
        self._start_clock()
        self._poll_mode_sync()

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


        # Right: logged-in user + role badge + clock
        right = tk.Frame(hdr, bg=SURFACE)
        right.pack(side=tk.RIGHT, padx=PAD)
        
        if not self.is_admin:
            admin_btn = tk.Button(right, text="🔐 Admin Login", font=("Segoe UI", 9, "bold"),
                                  bg=PRIMARY, fg=BG, padx=8, pady=2, relief=tk.FLAT,
                                  cursor="hand2", command=self._prompt_admin_login)
            admin_btn.pack(side=tk.LEFT, padx=(0, PAD))
            self._bind_hover(admin_btn, PRIMARY, PRIMARY_DK)

        role_color = SUCCESS if self.is_admin else PRIMARY
        role_text  = "ADMIN" if self.is_admin else "USER"
        
        info_frame = tk.Frame(right, bg=SURFACE)
        info_frame.pack(side=tk.LEFT)
        tk.Label(info_frame, text=f"👤 {self.user['name']}", font=FONT_BODY,
                 bg=SURFACE, fg=TEXT).pack(anchor=tk.E)
        tk.Label(info_frame, text=role_text, font=("Segoe UI", 8, "bold"),
                 bg=role_color, fg=BG, padx=6, pady=1).pack(anchor=tk.E, pady=(2, 0))
        
        self.clock_lbl = tk.Label(hdr, text="", font=FONT_BODY, bg=SURFACE, fg=TEXT_MUTED)
        self.clock_lbl.pack(side=tk.RIGHT, padx=PAD_SM)

    def _build_main_area(self):
        container = tk.Frame(self.root, bg=BG)
        container.pack(fill=tk.BOTH, expand=True, padx=PAD, pady=(0, PAD_SM))
        container.rowconfigure(0, weight=1)

        if self.is_admin:
            # 3-column layout: products | control | log
            container.columnconfigure(0, weight=3)
            container.columnconfigure(1, weight=2)
            container.columnconfigure(2, weight=2)
            self._build_products_panel(container)
            self._build_control_panel(container)
            self._build_event_log(container)
        else:
            # 2-column layout: products | log  (no control panel)
            container.columnconfigure(0, weight=4)
            container.columnconfigure(1, weight=2)
            self._build_products_panel(container)
            self._build_event_log_col(container, col=1)

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

        # Buy button / Edit button (for Admin)
        if self.is_admin:
            btn_state = tk.NORMAL
            btn_text = "EDIT PRICE"
            btn_cmd = lambda p=product["id"], cp=product["base_price"]: self._edit_price(p, cp)
            btn_color = WARNING
            btn_hover = "#E67E22"
        else:
            btn_state = tk.NORMAL if available > 0 else tk.DISABLED
            btn_text = "BUY" if available > 0 else "OUT OF STOCK"
            btn_cmd = lambda p=product["id"]: self._buy(p)
            btn_color = PRIMARY if available > 0 else BORDER
            btn_hover = PRIMARY_DK

        btn = tk.Button(card, text=btn_text, font=FONT_BTN,
                        bg=btn_color, fg=TEXT,
                        relief=tk.FLAT, cursor="hand2", padx=8, pady=4,
                        state=btn_state,
                        command=btn_cmd)
        btn.pack(fill=tk.X, pady=(PAD_SM, 0))
        if self.is_admin or available > 0:
            self._bind_hover(btn, btn_color, btn_hover)

    # ── Control Panel ──────────────────────────────────────────────────────

    def _build_control_panel(self, parent):
        frame = tk.Frame(parent, bg=SURFACE, padx=PAD, pady=PAD)
        frame.grid(row=0, column=1, sticky="nsew", padx=(0, PAD_SM))

        tk.Label(frame, text="⚙  Control Panel", font=FONT_HEADING,
                 bg=SURFACE, fg=TEXT).pack(anchor=tk.W, pady=(0, PAD))

        # ── Pricing Strategy ──────────────────────────────────
        self._section(frame, "Pricing Strategy")
        self.pricing_var = tk.StringVar(value="Standard")
        
        # We will keep references to the radio buttons so we can update their text directly
        self.pricing_rbs = {}
        
        config = self.ki.data_manager.load_config() if self.ki.data_manager else {}
        pricings = [
            ("Standard",   "Standard"),
            ("Discounted", "Discounted"),
            ("Emergency",  "Emergency"),
        ]
        for name, value in pricings:
            row_frame = tk.Frame(frame, bg=SURFACE)
            row_frame.pack(fill=tk.X, padx=PAD_SM, pady=2)
            
            rb = tk.Radiobutton(row_frame, variable=self.pricing_var, value=value,
                                font=FONT_BODY, bg=SURFACE, fg=TEXT,
                                selectcolor=CARD, activebackground=SURFACE,
                                activeforeground=TEXT,
                                command=lambda n=value: self._change_pricing(n))
            rb.pack(side=tk.LEFT)
            self.pricing_rbs[value] = rb
            
            edit_btn = tk.Button(row_frame, text="✏", font=("Segoe UI Emoji", 10), bg=SURFACE, fg=TEXT_MUTED,
                                 relief=tk.FLAT, cursor="hand2", command=lambda v=value: self._edit_pricing_rule(v))
            edit_btn.pack(side=tk.RIGHT, padx=5)
            self._bind_hover(edit_btn, SURFACE, CARD)
            
        self._update_pricing_rb_labels()

        ttk.Separator(frame, orient="horizontal").pack(fill=tk.X, pady=PAD)

        # ── Stats ─────────────────────────────────────────────
        self._section(frame, "Live Statistics")
        stats_frame = tk.Frame(frame, bg=CARD, padx=PAD, pady=PAD_SM)
        stats_frame.pack(fill=tk.X)

        self.revenue_lbl = tk.Label(stats_frame, text="Revenue:  Rs.0.00",
                                    font=FONT_BODY, bg=CARD, fg=SUCCESS, anchor=tk.W)
        self.revenue_lbl.pack(fill=tk.X)
        self.sold_lbl = tk.Label(stats_frame, text="Items Sold:  0",
                                 font=FONT_BODY, bg=CARD, fg=TEXT, anchor=tk.W)
        self.sold_lbl.pack(fill=tk.X)
        self.txn_count_lbl = tk.Label(stats_frame, text="Transactions:  0",
                                      font=FONT_BODY, bg=CARD, fg=TEXT, anchor=tk.W)
        self.txn_count_lbl.pack(fill=tk.X)
        self._txn_count = 0

    # ── Event Log ──────────────────────────────────────────────────────────

    def _build_event_log(self, parent):
        """Admin layout: event log in column 2."""
        self._create_log_widget(parent, col=2)

    def _build_event_log_col(self, parent, col: int):
        """User layout: event log in specified column."""
        self._create_log_widget(parent, col=col)

    def _create_log_widget(self, parent, col: int):
        frame = tk.Frame(parent, bg=SURFACE, padx=PAD, pady=PAD)
        frame.grid(row=0, column=col, sticky="nsew")

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

        role_info = f"Role: {'Administrator' if self.is_admin else 'Customer'}"
        self._log("🚀 Aura Retail OS v2.0 started", "success")
        self._log(f"👤 Logged in: {self.user['name']} ({role_info})", "muted")
        self._log(f"📍 Kiosk: {self.registry.kiosk_name} @ {self.registry.location}", "muted")
        self._log("──────────────────────────────────", "muted")

    # ── Status Bar ─────────────────────────────────────────────────────────

    def _build_status_bar(self):
        bar = tk.Frame(self.root, bg=SURFACE, height=30)
        bar.pack(fill=tk.X, side=tk.BOTTOM)
        bar.pack_propagate(False)

        self.status_mode_lbl  = tk.Label(bar, text="Mode: Active", font=FONT_STATUS,
                                          bg=SURFACE, fg=SUCCESS)
        self.status_mode_lbl.pack(side=tk.LEFT, padx=PAD)

        tk.Label(bar, text="|", bg=SURFACE, fg=BORDER).pack(side=tk.LEFT)

        self.status_price_lbl = tk.Label(bar, text="Pricing: Standard", font=FONT_STATUS,
                                          bg=SURFACE, fg=TEXT_MUTED)
        self.status_price_lbl.pack(side=tk.LEFT, padx=PAD)

        tk.Label(bar, text="|", bg=SURFACE, fg=BORDER).pack(side=tk.LEFT)

        self.status_rev_lbl   = tk.Label(bar, text="Revenue: Rs.0.00", font=FONT_STATUS,
                                          bg=SURFACE, fg=TEXT_MUTED)
        self.status_rev_lbl.pack(side=tk.LEFT, padx=PAD)

        tk.Label(bar, text="City: Zephyrus · Aura Retail OS © 2025",
                 font=FONT_STATUS, bg=SURFACE, fg=BORDER).pack(side=tk.RIGHT, padx=PAD)

    # ── Actions ────────────────────────────────────────────────────────────

    def _buy(self, product_id):
        result = self.ki.purchase_item(product_id, 1)
        if not result["success"]:
            messagebox.showwarning("Purchase Failed", result["message"])
        else:
            self._log(result["message"])
            self._update_stats()
            self._populate_products()

    def _update_stats(self):
        rev = getattr(self.registry, 'total_revenue', 0.0)
        sold = getattr(self.registry, 'total_items_sold', 0)
        if hasattr(self, '_txn_count'):
            self._txn_count += 1
        
        if hasattr(self, 'revenue_lbl'):
            self.revenue_lbl.config(text=f"Revenue:  Rs.{rev:.2f}")
        if hasattr(self, 'sold_lbl'):
            self.sold_lbl.config(text=f"Items Sold:  {sold}")
        if hasattr(self, 'txn_count_lbl'):
            self.txn_count_lbl.config(text=f"Transactions:  {getattr(self, '_txn_count', 0)}")

    def _update_pricing_rb_labels(self):
        if not hasattr(self, 'pricing_rbs'):
            return
        config = self.ki.data_manager.load_config() if self.ki.data_manager else {}
        std_mult = config.get("standard_multiplier", 1.0)
        disc_rate = config.get("discount_rate", 0.20)
        emerg_rate = config.get("emergency_rate", 0.50)
        
        if "Standard" in self.pricing_rbs:
            self.pricing_rbs["Standard"].config(text=f"💲  Standard  (×{std_mult:.2f})")
        if "Discounted" in self.pricing_rbs:
            self.pricing_rbs["Discounted"].config(text=f"🏷  Discounted  (−{disc_rate*100:.0f}%)")
        if "Emergency" in self.pricing_rbs:
            self.pricing_rbs["Emergency"].config(text=f"🚨  Emergency  (+{emerg_rate*100:.0f}%)")

    def _change_pricing(self, name, strategy=None, force_recreate=False):
        if strategy is None or force_recreate:
            config = self.ki.data_manager.load_config() if self.ki.data_manager else {}
            if name == "Standard":
                strategy = StandardPricing(config.get("standard_multiplier", 1.0))
            elif name == "Discounted":
                strategy = DiscountedPricing(config.get("discount_rate", 0.20))
            elif name == "Emergency":
                strategy = EmergencyPricing(config.get("emergency_rate", 0.50))
        self.ki.set_pricing(strategy, name)
        
        self._populate_products()
        if hasattr(self, '_refresh_pricing_ui'):
            self._refresh_pricing_ui(name)
        self._log(f"💰 Admin set pricing: {name}")

    def _edit_price(self, product_id, current_price):
        import tkinter.simpledialog as sd
        new_price = sd.askfloat("Edit Price", f"Enter new base price for {product_id}:", initialvalue=current_price)
        if new_price is not None and new_price >= 0:
            product = self.ki.kiosk.inventory_manager.get_product(product_id)
            if product:
                product["base_price"] = new_price
                if self.ki.data_manager:
                    self.ki.data_manager.save_inventory(self.ki.kiosk.inventory_manager.get_all_products())
                self._populate_products()
                self._log(f"⚙ Admin updated base price of {product['name']} to Rs.{new_price:.2f}")

    def _edit_pricing_rule(self, rule_type):
        config = self.ki.data_manager.load_config() if self.ki.data_manager else {}
        
        top = tk.Toplevel(self.root)
        top.title("Edit Pricing Rule")
        top.geometry("300x160")
        top.configure(bg=SURFACE)
        top.grab_set()  # Make window modal
        top.transient(self.root)
        
        tk.Label(top, text=f"Edit {rule_type} Rule", font=("Segoe UI", 11, "bold"), bg=SURFACE, fg=TEXT).pack(pady=(15, 5))
        
        input_frame = tk.Frame(top, bg=SURFACE)
        input_frame.pack(pady=10)
        
        var = tk.StringVar()
        
        if rule_type == "Standard":
            current = config.get("standard_multiplier", 1.0)
            tk.Label(input_frame, text="×", font=("Segoe UI", 12), bg=SURFACE, fg=TEXT).pack(side=tk.LEFT)
            var.set(f"{current:.2f}")
        elif rule_type == "Discounted":
            current = int(config.get("discount_rate", 0.20) * 100)
            tk.Label(input_frame, text="−", font=("Segoe UI", 12, "bold"), bg=SURFACE, fg=TEXT).pack(side=tk.LEFT)
            var.set(str(current))
        elif rule_type == "Emergency":
            current = int(config.get("emergency_rate", 0.50) * 100)
            tk.Label(input_frame, text="+", font=("Segoe UI", 12, "bold"), bg=SURFACE, fg=TEXT).pack(side=tk.LEFT)
            var.set(str(current))
            
        entry = tk.Entry(input_frame, textvariable=var, font=("Segoe UI", 12), width=6, justify="center")
        entry.pack(side=tk.LEFT, padx=5)
        
        if rule_type in ("Discounted", "Emergency"):
            tk.Label(input_frame, text="%", font=("Segoe UI", 12), bg=SURFACE, fg=TEXT).pack(side=tk.LEFT)

        def save():
            val_str = var.get()
            try:
                if rule_type == "Standard":
                    config["standard_multiplier"] = float(val_str)
                elif rule_type == "Discounted":
                    config["discount_rate"] = abs(float(val_str)) / 100.0
                elif rule_type == "Emergency":
                    config["emergency_rate"] = abs(float(val_str)) / 100.0
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid number.", parent=top)
                return
                
            if self.ki.data_manager:
                self.ki.data_manager.save_config(config)
                
            self._log(f"⚙ Admin updated {rule_type} pricing rule.")
            self._update_pricing_rb_labels()
            
            # Apply new strategy explicitly to trigger UI updates
            current_strat_name = self.pricing_var.get()
            if current_strat_name == rule_type:
                self._change_pricing(current_strat_name, force_recreate=True)
                
            top.destroy()

        btn_frame = tk.Frame(top, bg=SURFACE)
        btn_frame.pack(pady=10)
        
        save_btn = tk.Button(btn_frame, text="Save", command=save, bg=PRIMARY, fg=BG, font=FONT_BTN, relief=tk.FLAT, padx=15)
        save_btn.pack(side=tk.LEFT, padx=5)
        self._bind_hover(save_btn, PRIMARY, PRIMARY_DK)
        
        cancel_btn = tk.Button(btn_frame, text="Cancel", command=top.destroy, bg=BORDER, fg=TEXT_MUTED, font=FONT_BTN, relief=tk.FLAT, padx=10)
        cancel_btn.pack(side=tk.LEFT, padx=5)
        
        # Center the popup
        top.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() - top.winfo_width()) // 2
        y = self.root.winfo_y() + (self.root.winfo_height() - top.winfo_height()) // 2
        top.geometry(f"+{x}+{y}")
        
        entry.focus_set()


    # ── Helpers ────────────────────────────────────────────────────────────

    def _prompt_admin_login(self):
        import hashlib
        
        top = tk.Toplevel(self.root)
        top.title("Admin Authentication")
        top.geometry("360x220")
        top.configure(bg=SURFACE)
        top.grab_set()
        top.transient(self.root)
        
        # Center the modal
        top.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() - 360) // 2
        y = self.root.winfo_y() + (self.root.winfo_height() - 220) // 2
        top.geometry(f"+{x}+{y}")

        tk.Label(top, text="Admin Sign In", font=("Segoe UI", 16, "bold"),
                 bg=SURFACE, fg=TEXT).pack(pady=(20, 10))

        pwd_frame = tk.Frame(top, bg=SURFACE)
        pwd_frame.pack(fill=tk.X, padx=40)
        
        tk.Label(pwd_frame, text="Password:", font=("Segoe UI", 9, "bold"),
                 bg=SURFACE, fg=TEXT_MUTED).pack(anchor=tk.W)
                 
        pwd_var = tk.StringVar()
        pwd_entry = tk.Entry(pwd_frame, textvariable=pwd_var, show="●", font=("Segoe UI", 12),
                             bg=CARD, fg=TEXT, insertbackground=TEXT, relief=tk.FLAT)
        pwd_entry.pack(fill=tk.X, ipady=6, pady=(4, 8))
        
        err_lbl = tk.Label(top, text="", font=("Segoe UI", 9), bg=SURFACE, fg=DANGER)
        err_lbl.pack()

        def _verify():
            pwd = pwd_var.get()
            if not pwd:
                return
            hashed = hashlib.sha256(pwd.encode()).hexdigest()
            
            admin_user = None
            if self.ki.data_manager:
                admin_user = self.ki.data_manager.verify_user("admin", hashed)
                
            if admin_user and admin_user.get("role") == "admin":
                top.destroy()
                # Open admin panel in a new window instead of closing current
                AuraRetailOSApp(self.ki, self.registry, user=admin_user, parent_window=self.root)
            else:
                err_lbl.config(text="❌ Invalid password")
                pwd_var.set("")
                pwd_entry.focus_set()

        btn_frame = tk.Frame(top, bg=SURFACE)
        btn_frame.pack(pady=5)
        
        login_btn = tk.Button(btn_frame, text="  Unlock  ", font=FONT_BTN, bg=PRIMARY, fg=BG,
                              relief=tk.FLAT, cursor="hand2", padx=20, pady=5, command=_verify)
        login_btn.pack()
        self._bind_hover(login_btn, PRIMARY, PRIMARY_DK)
        
        top.bind("<Return>", lambda e: _verify())
        pwd_entry.focus_set()

    def _log(self, message: str, tag: str = None):
        self.log_text.configure(state=tk.NORMAL)
        # Auto-detect tag from first emoji char
        if tag is None:
            for icon in EVENT_TAG_COLORS:
                if icon in message:
                    tag = icon
                    break
        self.log_text.insert(tk.END, message + "\n", tag or "")
        self.log_text.see(tk.END)
        self.log_text.configure(state=tk.DISABLED)

    def _clear_log(self):
        self.log_text.configure(state=tk.NORMAL)
        self.log_text.delete("1.0", tk.END)
        self.log_text.configure(state=tk.DISABLED)

    def _update_stats(self):
        rev = self.registry.total_revenue
        sold = self.registry.total_items_sold
        self._txn_count = len(self.ki.kiosk.invoker.get_history())

        # Stat labels only exist in admin view — guard before updating
        if self.revenue_lbl:
            self.revenue_lbl.config(text=f"Revenue:  Rs.{rev:.2f}")
        if self.sold_lbl:
            self.sold_lbl.config(text=f"Items Sold:  {sold}")
        if self.txn_count_lbl:
            self.txn_count_lbl.config(text=f"Transactions:  {self._txn_count}")
        # Status bar exists for both roles
        self.status_rev_lbl.config(text=f"Revenue: Rs.{rev:.2f}")

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
        if hasattr(self, 'clock_lbl') and self.clock_lbl.winfo_exists():
            try:
                self.clock_lbl.config(text=now)
                self.root.after(1000, self._start_clock)
            except Exception:
                pass

    # ── Real-time sync for user sessions (polls config.json every 10s) ──────

    def _poll_mode_sync(self):
        try:
            from persistence.data_manager import DataManager
            config = DataManager.load_config()

            # ── Sync pricing ──────────────────────────────────────────────
            actual_pricing = self.ki.kiosk.pricing_strategy.get_strategy_name()
            actual_mult = self.ki.kiosk.pricing_strategy.get_multiplier()
            
            if not hasattr(self, "_last_pricing_name"):
                self._last_pricing_name = actual_pricing
                self._last_pricing_mult = actual_mult
                
            pricing_changed = (self._last_pricing_name != actual_pricing or 
                               self._last_pricing_mult != actual_mult)

            if pricing_changed:
                self._refresh_pricing_ui(actual_pricing)
                self._update_pricing_rb_labels()
                self._populate_products()
                if not self.is_admin:
                    self._log(f"💰 Notice: Pricing strategy updated to {actual_pricing} by Administrator")
                self._last_pricing_name = actual_pricing
                self._last_pricing_mult = actual_mult

            # ── Sync Inventory ──────────────────────────────────────────────
            current_inv_state = hash(tuple((p["id"], p.get("quantity", 0), p.get("base_price", 0.0)) 
                                     for p in self.ki.kiosk.inventory_manager.get_all_products()))
            
            if not hasattr(self, "_last_inv_state"):
                self._last_inv_state = current_inv_state
                
            # Repaint products if they updated in shared memory (by user or admin)
            if self._last_inv_state != current_inv_state:
                self._populate_products()
                self._last_inv_state = current_inv_state

        except Exception as e:
            print(f"[Sync] Poll error: {e}")
            
        # Update UI stats continuously to reflect shared singleton memory changes
        self._update_stats()

        # Schedule next poll in 2 seconds
        self.root.after(2000, self._poll_mode_sync)

    def _apply_synced_pricing(self, pricing_name: str):
        """Apply admin pricing change to user session."""
        from strategy.standard_pricing import StandardPricing
        from strategy.discounted_pricing import DiscountedPricing
        from strategy.emergency_pricing import EmergencyPricing

        config = self.ki.data_manager.load_config() if self.ki.data_manager else {}
        pricing_map = {
            "standard":   (StandardPricing(config.get("standard_multiplier", 1.0)),   "Standard"),
            "discounted": (DiscountedPricing(config.get("discount_rate", 0.20)), "Discounted"),
            "emergency":  (EmergencyPricing(config.get("emergency_rate", 0.50)),  "Emergency"),
        }

        key = pricing_name.lower()
        if key not in pricing_map:
            return

        strategy, display_name = pricing_map[key]
        self.ki.kiosk.set_pricing_strategy(strategy)  # swap strategy
        self._refresh_pricing_ui(display_name)         # update status bar
        self._update_pricing_rb_labels()               # sync radio button text
        self._populate_products()                      # reprice all cards
        self._log(f"💰 Admin set pricing: {display_name}")

    def run(self):
        if isinstance(self.root, tk.Tk):
            self.root.mainloop()
