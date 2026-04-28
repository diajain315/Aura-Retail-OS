import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from gui.styles import *
from pricing.standard_pricing import StandardPricing
from pricing.discounted_pricing import DiscountedPricing
from pricing.emergency_pricing import EmergencyPricing
from state.active_state import ActiveState
from state.power_saving_state import PowerSavingState
from state.maintenance_state import MaintenanceState
from state.emergency_state import EmergencyLockdownState

# Event color tags for admin log widget
EVENT_TAG_COLORS = {
    "✅": SUCCESS,
    "❌": DANGER,
    "⚠": WARNING,
    "🔧": WARNING,
    "🚨": DANGER,
    "🔄": PRIMARY,
    "💰": "#A9DFBF",
    "📦": SUCCESS,
    "🏙": TEXT_MUTED,
    "🔙": WARNING,
    "⚙": PRIMARY,
    "🚒": DANGER,
    "📧": TEXT_MUTED,
    "✨": SUCCESS,
}

class AdminLoginDialog:

    
    def __init__(self, parent, admin_auth, on_success=None):

        self.admin_auth = admin_auth
        self.on_success = on_success
        self.result = False
        
        # Create dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Admin Login")
        self.dialog.geometry("350x200")
        self.dialog.resizable(False, False)
        self.dialog.configure(bg=SURFACE)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self.dialog.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() // 2) - 175
        y = parent.winfo_y() + (parent.winfo_height() // 2) - 100
        self.dialog.geometry(f"+{x}+{y}")
        
        self._build_ui()
    
    def _build_ui(self):

        frame = tk.Frame(self.dialog, bg=SURFACE, padx=PAD, pady=PAD)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        tk.Label(frame, text="🔐 Admin Login", font=FONT_HEADING,
                 bg=SURFACE, fg=TEXT).pack(pady=(0, PAD))
        
        # Password
        tk.Label(frame, text="Password:", font=FONT_BODY, bg=SURFACE, fg=TEXT).pack(anchor=tk.W)
        self.password_entry = tk.Entry(frame, font=FONT_BODY, bg=CARD, fg=TEXT,
                         insertbackground=TEXT, relief=tk.FLAT,
                         show="•")
        self.password_entry.pack(fill=tk.X, pady=(0, PAD))
        self.password_entry.bind("<Return>", lambda e: self._login())
        self.password_entry.focus()
        
        # Buttons
        btn_frame = tk.Frame(frame, bg=SURFACE)
        btn_frame.pack(fill=tk.X, pady=(PAD, 0))
        
        login_btn = tk.Button(btn_frame, text="Login", font=FONT_BTN, bg=PRIMARY, fg=BG,
                              relief=tk.FLAT, cursor="hand2", command=self._login)
        login_btn.pack(side=tk.LEFT, expand=True, padx=(0, 4))
        self._bind_hover(login_btn, PRIMARY, PRIMARY_DK)
        
        cancel_btn = tk.Button(btn_frame, text="Cancel", font=FONT_BTN, bg=BORDER, fg=TEXT,
                               relief=tk.FLAT, cursor="hand2", command=self._cancel)
        cancel_btn.pack(side=tk.LEFT, expand=True, padx=(4, 0))
        self._bind_hover(cancel_btn, BORDER, TEXT_MUTED)
    
    def _bind_hover(self, btn, normal_color, hover_color):

        btn.bind("<Enter>", lambda e: btn.config(bg=hover_color))
        btn.bind("<Leave>", lambda e: btn.config(bg=normal_color))
    
    def _login(self):

        password = self.password_entry.get()
        
        if not password:
            messagebox.showwarning("Login Failed", "Please enter password")
            return
        
        if self.admin_auth.verify_credentials(password):
            self.admin_auth.create_session()
            self.result = True
            self.dialog.destroy()
            if self.on_success:
                self.on_success()
        else:
            messagebox.showerror("Login Failed", "Invalid password")
            self.password_entry.delete(0, tk.END)
            self.password_entry.focus()
    
    def _cancel(self):

        self.result = False
        self.dialog.destroy()

class EditPriceDialog:

    def __init__(self, parent, admin_manager, product, on_saved=None):
        self.admin_manager = admin_manager
        self.product = product
        self.on_saved = on_saved

        self.dialog = tk.Toplevel(parent)
        self.dialog.title(f"Edit Price - {product['name']}")
        self.dialog.geometry("360x220")
        self.dialog.resizable(False, False)
        self.dialog.configure(bg=SURFACE)
        self.dialog.transient(parent)
        self.dialog.grab_set()

        self._build_ui()

    def _build_ui(self):
        frame = tk.Frame(self.dialog, bg=SURFACE, padx=PAD, pady=PAD)
        frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(frame, text=f"✏️ Edit Price: {self.product['name']}",
                 font=FONT_HEADING, bg=SURFACE, fg=TEXT).pack(anchor=tk.W, pady=(0, PAD))

        tk.Label(frame, text=f"Current price: {self.product.get('base_price', 0):.2f}",
                 font=FONT_BODY, bg=SURFACE, fg=TEXT_MUTED).pack(anchor=tk.W)

        tk.Label(frame, text="New Price:", font=FONT_BODY, bg=SURFACE, fg=TEXT).pack(anchor=tk.W, pady=(PAD, 0))
        self.price_entry = tk.Entry(frame, font=FONT_BODY, bg=CARD, fg=TEXT,
                                    insertbackground=TEXT, relief=tk.FLAT)
        self.price_entry.insert(0, f"{self.product.get('base_price', 0):.2f}")
        self.price_entry.pack(fill=tk.X, pady=(0, PAD))
        self.price_entry.focus()

        btn_frame = tk.Frame(frame, bg=SURFACE)
        btn_frame.pack(fill=tk.X, pady=(PAD, 0))

        save_btn = tk.Button(btn_frame, text="Save", font=FONT_BTN, bg=PRIMARY, fg=BG,
                             relief=tk.FLAT, cursor="hand2", command=self._save)
        save_btn.pack(side=tk.LEFT, expand=True, padx=(0, 4))

        cancel_btn = tk.Button(btn_frame, text="Cancel", font=FONT_BTN, bg=BORDER, fg=TEXT,
                               relief=tk.FLAT, cursor="hand2", command=self.dialog.destroy)
        cancel_btn.pack(side=tk.LEFT, expand=True, padx=(4, 0))

    def _save(self):
        try:
            new_price = float(self.price_entry.get())
        except ValueError:
            messagebox.showerror("Invalid Price", "Please enter a valid number.")
            return

        if self.admin_manager.update_product_price(self.product["id"], new_price):
            if self.on_saved:
                self.on_saved(self.product["id"], new_price)
            self.dialog.destroy()
        else:
            messagebox.showerror("Error", "Unable to update the price.")

class AddProductDialog:

    def __init__(self, parent, admin_manager, on_saved=None):
        self.admin_manager = admin_manager
        self.on_saved = on_saved

        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Add New Product")
        self.dialog.geometry("460x560")
        self.dialog.resizable(False, False)
        self.dialog.configure(bg=SURFACE)
        self.dialog.transient(parent)
        self.dialog.grab_set()

        self._build_ui()

    def _build_ui(self):
        frame = tk.Frame(self.dialog, bg=SURFACE, padx=PAD, pady=PAD)
        frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(frame, text="➕ Add New Product", font=FONT_HEADING,
                 bg=SURFACE, fg=TEXT).pack(anchor=tk.W, pady=(0, PAD))

        self.fields = {}
        for label, key, default in [
            ("Product ID", "id", ""),
            ("Product Name", "name", ""),
            ("Description", "description", ""),
            ("Icon / Emoji", "icon", ""),
            ("Base Price", "base_price", "0.00"),
            ("Quantity", "quantity", "0"),
        ]:
            tk.Label(frame, text=label, font=FONT_BODY, bg=SURFACE, fg=TEXT).pack(anchor=tk.W)
            entry = tk.Entry(frame, font=FONT_BODY, bg=CARD, fg=TEXT,
                             insertbackground=TEXT, relief=tk.FLAT)
            entry.insert(0, default)
            entry.pack(fill=tk.X, pady=(0, PAD_SM))
            self.fields[key] = entry

        self.essential_var = tk.BooleanVar()
        tk.Checkbutton(frame, text="Essential Product", variable=self.essential_var,
                       font=FONT_BODY, bg=SURFACE, fg=TEXT, selectcolor=CARD,
                       activebackground=SURFACE).pack(anchor=tk.W, pady=(4, PAD))

        btn_frame = tk.Frame(frame, bg=SURFACE)
        btn_frame.pack(fill=tk.X, pady=(PAD, 0))

        add_btn = tk.Button(btn_frame, text="Add Product", font=FONT_BTN, bg=SUCCESS, fg=BG,
                            relief=tk.FLAT, cursor="hand2", command=self._save)
        add_btn.pack(side=tk.LEFT, expand=True, padx=(0, 4))

        cancel_btn = tk.Button(btn_frame, text="Cancel", font=FONT_BTN, bg=BORDER, fg=TEXT,
                               relief=tk.FLAT, cursor="hand2", command=self.dialog.destroy)
        cancel_btn.pack(side=tk.LEFT, expand=True, padx=(4, 0))

    def _save(self):
        product_data = {key: entry.get().strip() for key, entry in self.fields.items()}
        if not all(product_data[key] for key in ("id", "name", "icon", "base_price", "quantity")):
            messagebox.showwarning("Validation Error", "Please fill in all required fields.")
            return

        product_data["essential"] = self.essential_var.get()

        try:
            product_data["base_price"] = float(product_data["base_price"])
            product_data["quantity"] = int(product_data["quantity"])
        except ValueError:
            messagebox.showerror("Validation Error", "Base price must be a number and quantity must be an integer.")
            return

        if self.admin_manager.add_new_product(product_data):
            if self.on_saved:
                self.on_saved(product_data)
            self.dialog.destroy()
        else:
            messagebox.showerror("Error", "Unable to add the product.")

class AdminPanel:

    
    def __init__(self, parent, admin_manager, kiosk_interface, on_close=None):

        self.admin_manager = admin_manager
        self.ki = kiosk_interface
        self.on_close = on_close
        
        # Create admin window
        self.panel = tk.Toplevel(parent)
        self.panel.title("Admin Control Panel")
        self.panel.geometry("900x600")
        self.panel.state("zoomed")
        self.panel.resizable(True, True)
        self.panel.configure(bg=BG)
        self.panel.protocol("WM_DELETE_WINDOW", self._on_close)
        
        self._build_ui()
        
        # Subscribe to real-time updates
        admin_manager.subscribe_to_price_changes(self._on_price_changed)
        admin_manager.subscribe_to_inventory_changes(self._on_inventory_changed)
        
        from events.events import TransactionEvent, ModeChangedEvent, PricingChangedEvent, InventoryUpdateEvent
        bus = self.ki.kiosk.event_bus
        bus.subscribe(TransactionEvent, lambda e: self._update_stats())
        bus.subscribe(InventoryUpdateEvent, lambda e: self._update_stats())
        bus.subscribe(ModeChangedEvent, lambda e: self.mode_var.set(e.new_mode))
        bus.subscribe(PricingChangedEvent, lambda e: self.pricing_var.set(e.new_strategy) if e.new_strategy else None)
    
    def _build_ui(self):

        header = tk.Frame(self.panel, bg=SURFACE, height=50)
        header.pack(fill=tk.X, pady=(0, 4))
        header.pack_propagate(False)

        tk.Label(header, text="👨‍💼 Admin Control Panel", font=FONT_TITLE,
                 bg=SURFACE, fg=TEXT).pack(side=tk.LEFT, padx=PAD)

        container = tk.Frame(self.panel, bg=BG)
        container.pack(fill=tk.BOTH, expand=True, padx=PAD, pady=(0, PAD))
        container.columnconfigure(0, weight=4)
        container.columnconfigure(1, weight=1)
        container.columnconfigure(2, weight=4)
        container.rowconfigure(0, weight=1)

        self._build_inventory_panel(container)
        self._build_controls_panel(container)
        self._build_logs_panel(container)

        self.append_log("👨‍💼 Admin panel opened", "muted")

    def _build_inventory_panel(self, parent):
        frame = tk.Frame(parent, bg=SURFACE, padx=PAD, pady=PAD)
        frame.grid(row=0, column=0, sticky="nsew", padx=(0, PAD_SM))

        tk.Label(frame, text="➕ Inventory", font=FONT_HEADING, bg=SURFACE, fg=TEXT).pack(anchor=tk.W, pady=(0, PAD))
        tk.Label(frame, text="Add, edit, or remove products.", font=FONT_SMALL, bg=SURFACE, fg=TEXT_MUTED).pack(anchor=tk.W, pady=(0, PAD_SM))

        add_btn = tk.Button(frame, text="Add New Product", font=FONT_BTN, bg=SUCCESS, fg=BG,
                            relief=tk.FLAT, cursor="hand2", command=self._open_add_product_dialog)
        add_btn.pack(fill=tk.X, pady=(0, PAD))
        self._bind_hover(add_btn, SUCCESS, "#27AE60")

        self._build_edit_products_panel(frame)

    def _build_controls_panel(self, parent):
        outer_frame = tk.Frame(parent, bg=SURFACE, padx=PAD, pady=PAD)
        outer_frame.grid(row=0, column=1, sticky="nsew", padx=(PAD_SM, PAD_SM))

        tk.Label(outer_frame, text="⚙ Controls", font=FONT_HEADING, bg=SURFACE, fg=TEXT).pack(anchor=tk.W, pady=(0, PAD))

        canvas = tk.Canvas(outer_frame, bg=SURFACE, highlightthickness=0, width=200)
        scrollbar = ttk.Scrollbar(outer_frame, orient="vertical", command=canvas.yview)
        frame = tk.Frame(canvas, bg=SURFACE)

        frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas_window = canvas.create_window((0, 0), window=frame, anchor="nw")
        
        def _on_canvas_resize(e):
            if e.width > 0:
                canvas.itemconfig(canvas_window, width=e.width)
        canvas.bind("<Configure>", _on_canvas_resize)
        
        canvas.configure(yscrollcommand=scrollbar.set)
        
        def _on_mousewheel(e):
            canvas.yview_scroll(-1 * (e.delta // 120), "units")
        
        # Bind MouseWheel specifically when hovering the canvas/frame
        canvas.bind("<Enter>", lambda e: canvas.bind_all("<MouseWheel>", _on_mousewheel))
        canvas.bind("<Leave>", lambda e: canvas.unbind_all("<MouseWheel>"))

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Moved back to bottom

        self._section(frame, "Kiosk Mode")
        current_mode = self.ki.kiosk.state.get_mode_name()
        self.mode_var = tk.StringVar(value=current_mode)
        modes = [
            ("🟢 Active", "Active", ActiveState()),
            ("🟡 Power Saving", "Power Saving", PowerSavingState()),
            ("🟣 Maintenance", "Maintenance", MaintenanceState()),
            ("🔴 Emergency Lockdown", "Emergency Lockdown", EmergencyLockdownState()),
        ]
        for label, name, state_obj in modes:
            tk.Radiobutton(frame, text=label, variable=self.mode_var, value=name,
                           font=FONT_BODY, bg=SURFACE, fg=TEXT,
                           selectcolor=CARD, activebackground=SURFACE,
                           activeforeground=TEXT,
                           command=lambda n=name, s=state_obj: self._change_mode(n, s)).pack(anchor=tk.W, padx=PAD_SM)

        ttk.Separator(frame, orient="horizontal").pack(fill=tk.X, pady=PAD)

        self._section(frame, "Pricing Strategy")
        current_pricing = self.ki.kiosk.pricing_strategy.get_strategy_name()
        self.pricing_var = tk.StringVar(value=current_pricing)
        pricings = [
            ("💲 Standard", "Standard", StandardPricing()),
            ("🏷 Discounted", "Discounted", DiscountedPricing()),
            ("🚨 Emergency", "Emergency", EmergencyPricing()),
        ]
        for label, name, strat in pricings:
            tk.Radiobutton(frame, text=label, variable=self.pricing_var, value=name,
                           font=FONT_BODY, bg=SURFACE, fg=TEXT,
                           selectcolor=CARD, activebackground=SURFACE,
                           activeforeground=TEXT,
                           command=lambda n=name, s=strat: self._change_pricing(n, s)).pack(anchor=tk.W, padx=PAD_SM)

        ttk.Separator(frame, orient="horizontal").pack(fill=tk.X, pady=PAD)

        self._section(frame, "Simulation")
        for text, color, cmd in [
            ("🔧 Trigger Hardware Failure", DANGER, self._sim_failure),
            ("🚨 Activate Emergency Mode", DANGER, self._sim_emergency),
            ("📦 Restock All Products", SUCCESS, self._sim_restock),
            ("🩺 Run Diagnostics", PRIMARY, self._sim_diagnostics),
        ]:
            btn = tk.Button(frame, text=text, font=FONT_BTN, bg=color, fg=BG,
                            relief=tk.FLAT, cursor="hand2", pady=6, command=cmd)
            btn.pack(fill=tk.X, pady=3)

        self.control_status = tk.Label(frame, text="Admin controls are live.",
                                       font=FONT_SMALL, bg=SURFACE, fg=TEXT_MUTED,
                                       wraplength=320, justify=tk.LEFT)
        self.control_status.pack(anchor=tk.W, pady=(PAD, 0))

        ttk.Separator(frame, orient="horizontal").pack(fill=tk.X, pady=PAD)

        # ── Stats ─────────────────────────────────────────────
        self._section(frame, "Daily Statistics")
        stats_frame = tk.Frame(frame, bg=CARD, padx=PAD, pady=PAD_SM)
        stats_frame.pack(fill=tk.X, pady=(0, PAD))

        self.revenue_lbl = tk.Label(stats_frame, text="Revenue:  Rs.0.00",
                                    font=FONT_BODY, bg=CARD, fg=SUCCESS, anchor=tk.W)
        self.revenue_lbl.pack(fill=tk.X)
        self.sold_lbl = tk.Label(stats_frame, text="Items Sold:  0",
                                 font=FONT_BODY, bg=CARD, fg=TEXT, anchor=tk.W)
        self.sold_lbl.pack(fill=tk.X)
        self.txn_count_lbl = tk.Label(stats_frame, text="Transactions:  0",
                                      font=FONT_BODY, bg=CARD, fg=TEXT, anchor=tk.W)
        self.txn_count_lbl.pack(fill=tk.X)
        
        self._update_stats()

    def _build_logs_panel(self, parent):
        frame = tk.Frame(parent, bg=SURFACE, padx=PAD, pady=PAD)
        frame.grid(row=0, column=2, sticky="nsew", padx=(PAD_SM, 0))

        tk.Label(frame, text="📋 Admin Logs", font=FONT_HEADING, bg=SURFACE, fg=TEXT).pack(anchor=tk.W, pady=(0, PAD_SM))

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
              relief=tk.FLAT, cursor="hand2", command=self.clear_log).pack(fill=tk.X, pady=(PAD_SM, 0))
    
    def _build_edit_products_panel(self, parent):

        frame = tk.Frame(parent, bg=SURFACE)
        frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(frame, text="🛒 Products", font=FONT_HEADING,
                 bg=SURFACE, fg=TEXT).pack(anchor=tk.W, pady=(0, PAD))

        canvas = tk.Canvas(frame, bg=SURFACE, highlightthickness=0)
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        self.products_cards_frame = tk.Frame(canvas, bg=SURFACE)

        self.products_cards_frame.bind(
            "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=self.products_cards_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.bind("<MouseWheel>", lambda e: canvas.yview_scroll(-1 * (e.delta // 120), "units"))

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self._refresh_product_cards()

    def _refresh_product_cards(self):
        for widget in self.products_cards_frame.winfo_children():
            widget.destroy()

        products = self.admin_manager.get_all_products()
        cols = 2
        for i, product in enumerate(products):
            row, col = divmod(i, cols)
            self._make_admin_product_card(self.products_cards_frame, product, row, col)

    def _make_admin_product_card(self, parent, product, row, col):
        pid = product["id"]
        available = self.ki.kiosk.inventory_manager.get_available_stock(pid)
        essential = product.get("essential", False)

        card = tk.Frame(parent, bg=CARD, padx=PAD, pady=PAD, relief=tk.FLAT, bd=1)
        card.grid(row=row, column=col, sticky="nsew", padx=PAD_SM // 2, pady=PAD_SM // 2)
        parent.columnconfigure(col, weight=1)

        if essential:
            tk.Label(card, text="ESSENTIAL", font=("Segoe UI", 7, "bold"),
                     bg=SUCCESS, fg=BG, padx=4).pack(anchor=tk.E)

        tk.Label(card, text=product.get("icon", "📦"), font=FONT_ICON,
                 bg=CARD, fg=TEXT).pack()
        tk.Label(card, text=product["name"], font=FONT_HEADING,
                 bg=CARD, fg=TEXT).pack(pady=(0, 2))
        tk.Label(card, text=product.get("description", ""), font=FONT_SMALL,
                 bg=CARD, fg=TEXT_MUTED, wraplength=160, justify=tk.CENTER).pack()

        base_price = product.get('base_price', 0)
        actual_price = self.ki.kiosk.pricing_strategy.calculate_price(base_price)
        price_text = f"Rs.{actual_price:.2f}"

            
        tk.Label(card, text=price_text,
                 font=FONT_PRICE, bg=CARD, fg=PRIMARY).pack(pady=(6, 0))

        stock_color = DANGER if available <= 5 else WARNING if available <= 10 else SUCCESS
        tk.Label(card, text=f"In Stock: {available}", font=FONT_SMALL,
                 bg=CARD, fg=stock_color).pack(pady=(2, PAD_SM))

        btn_row = tk.Frame(card, bg=CARD)
        btn_row.pack(fill=tk.X)

        edit_btn = tk.Button(btn_row, text="EDIT PRICE", font=FONT_BTN,
                             bg=WARNING, fg=BG, relief=tk.FLAT, cursor="hand2",
                             command=lambda p=product: self._open_edit_price_dialog(p))
        edit_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 3))

        del_btn = tk.Button(btn_row, text="DELETE", font=FONT_BTN,
                            bg=DANGER, fg=BG, relief=tk.FLAT, cursor="hand2",
                            command=lambda p=product: self._delete_product_card(p))
        del_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(3, 0))

    def _open_edit_price_dialog(self, product):
        EditPriceDialog(self.panel, self.admin_manager, product,
                        on_saved=lambda pid, price: self._after_price_update(pid, price))

    def _after_price_update(self, product_id, new_price):
        self._refresh_product_cards()
        self.append_log(f"💰 Price updated: {product_id} → Rs.{new_price:.2f}", "💰")

    def _delete_product_card(self, product):
        product_id = product["id"]
        product_name = product["name"]
        if not messagebox.askyesno("Confirm Delete", f"Delete product '{product_name}'?"):
            return
        if self.admin_manager.delete_product(product_id):
            self._refresh_product_cards()
            self.append_log(f"🗑️ Deleted product: {product_name} ({product_id})")
        else:
            messagebox.showerror("Error", "Failed to delete product")
    
    def _open_add_product_dialog(self):

        AddProductDialog(self.panel, self.admin_manager, on_saved=lambda data: self._after_add_product(data))

    def _after_add_product(self, product_data):
        self._refresh_product_cards()
        self.append_log(f"✨ Added new product: {product_data['name']} ({product_data['id']})", "✨")
    
    def _on_price_changed(self, product_id, new_price):

        self._refresh_product_cards()
        if product_id != "ALL":
            self.append_log(f"💰 Price updated: {product_id} → Rs.{new_price:.2f}", "💰")
    
    def _on_inventory_changed(self, product_id, new_stock):

        self._refresh_product_cards()
        self.append_log(f"📦 Inventory updated: {product_id} stock={new_stock}", "📦")
    
    def _section(self, parent, title: str):
        tk.Label(parent, text=title.upper(), font=("Segoe UI", 9, "bold"),
                 bg=SURFACE, fg=TEXT_MUTED).pack(anchor=tk.W, pady=(0, 2))

    def _update_stats(self):
        try:
            rev = self.ki.registry.total_revenue
            sold = self.ki.registry.total_items_sold
            history = self.ki.kiosk.invoker.get_history()
            txn_count = len(history)

            self.revenue_lbl.config(text=f"Revenue:  Rs.{rev:.2f}")
            self.sold_lbl.config(text=f"Items Sold:  {sold}")
            self.txn_count_lbl.config(text=f"Transactions:  {txn_count}")
        except AttributeError:
            pass

    def _bind_hover(self, btn, normal_color, hover_color):

        btn.bind("<Enter>", lambda e: btn.config(bg=hover_color))
        btn.bind("<Leave>", lambda e: btn.config(bg=normal_color))

    def append_log(self, message: str, tag: str = None):
        self.log_text.configure(state=tk.NORMAL)
        if tag is None:
            for icon in EVENT_TAG_COLORS:
                if icon in message:
                    tag = icon
                    break
        self.log_text.insert(tk.END, message + "\n", tag or "")
        self.log_text.see(tk.END)
        self.log_text.configure(state=tk.DISABLED)

    def clear_log(self):
        self.log_text.configure(state=tk.NORMAL)
        self.log_text.delete("1.0", tk.END)
        self.log_text.configure(state=tk.DISABLED)

    def _change_mode(self, name, state_obj):
        self.ki.set_mode(state_obj, name)
        self.append_log(f"🔄 Mode changed to {name}", "🔄")

    def _change_pricing(self, name, strategy):
        self.ki.set_pricing(strategy, name)
        self.append_log(f"💰 Pricing switched to {name}", "💰")

    def _sim_failure(self):
        import random
        components = ["Dispenser Motor", "Payment Reader", "Touch Screen", "Refrigeration Unit"]
        severities = ["low", "medium", "high", "critical"]
        comp = random.choice(components)
        sev = random.choice(severities)
        self.append_log(f"🔧 Simulating failure: {comp} ({sev})", "🔧")
        self.ki.trigger_hardware_failure(comp, sev, log_cb=self.append_log)

    def _sim_emergency(self):
        self.mode_var.set("Emergency Lockdown")
        self.pricing_var.set("Emergency")
        self.ki.set_mode(EmergencyLockdownState(), "Emergency Lockdown")
        self.ki.set_pricing(EmergencyPricing(), "Emergency")
        self.append_log("🚨 Emergency mode activated", "🚨")

    def _sim_restock(self):
        self.append_log("📦 Restocking all products", "📦")
        self.ki.restock_all(50)

    def _sim_diagnostics(self):
        diag = self.ki.run_diagnostics()
        self.append_log("🩺 Diagnostics run", "⚙")
        for k, v in diag.items():
            self.append_log(f"  {k}: {v}", "muted")
    
    def _on_close(self):

        if self.on_close:
            self.on_close()
        self.panel.destroy()
