import hashlib
import tkinter as tk
from tkinter import messagebox
from gui.styles import (BG, SURFACE, CARD, PRIMARY, PRIMARY_DK, SUCCESS,
                        DANGER, TEXT, TEXT_MUTED, BORDER, LOG_BG,
                        FONT_TITLE, FONT_HEADING, FONT_BODY, FONT_BTN,
                        FONT_SMALL, FONT_PRICE, PAD, PAD_SM)


def _hash(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


class LoginWindow:
    
    def __init__(self, data_manager):
        self.data_manager = data_manager
        self.result = None
        self._build()

    def _build(self):
        self.root = tk.Tk()
        self.root.title("Aura Retail OS — Login")
        self.root.configure(bg=BG)

        # ── Maximise the window ──────────────────────────────────────────
        try:
            self.root.state("zoomed")          # Windows maximize
        except Exception:
            self.root.attributes("-zoomed", True)   # Linux fallback

        self.root.protocol("WM_DELETE_WINDOW", self._on_cancel)
        self.root.resizable(True, True)

        # Build after window is ready
        self.root.after(10, self._build_content)

    def _build_content(self):
        # ── Full-screen canvas split: left branding | right form ──────────
        main = tk.Frame(self.root, bg=BG)
        main.pack(fill=tk.BOTH, expand=True)
        main.columnconfigure(0, weight=1)
        main.columnconfigure(1, weight=1)
        main.rowconfigure(0, weight=1)

        self._build_left_brand(main)
        self._build_right_form(main)

    # ── Left panel — branding ─────────────────────────────────────────────

    def _build_left_brand(self, parent):
        left = tk.Frame(parent, bg=PRIMARY_DK)
        left.grid(row=0, column=0, sticky="nsew")

        inner = tk.Frame(left, bg=PRIMARY_DK)
        inner.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(inner, text="⬡", font=("Segoe UI Emoji", 80),
                 bg=PRIMARY_DK, fg=TEXT).pack()
        tk.Label(inner, text="AURA\nRETAIL OS", font=("Segoe UI", 36, "bold"),
                 bg=PRIMARY_DK, fg=TEXT, justify=tk.CENTER).pack(pady=(10, 0))
        tk.Label(inner, text="Smart City Kiosk Platform",
                 font=("Segoe UI", 13), bg=PRIMARY_DK, fg="#C5C2FF").pack(pady=(8, 0))

        # Separator line
        tk.Frame(inner, bg="#C5C2FF", height=1, width=200).pack(pady=24)

        tk.Label(inner, text="City of Zephyrus", font=FONT_SMALL,
                 bg=PRIMARY_DK, fg="#C5C2FF").pack()
        tk.Label(inner, text="v2.0 — Path A: Adaptive Autonomous System",
                 font=FONT_SMALL, bg=PRIMARY_DK, fg="#9996CC").pack(pady=(4, 0))

        # Pattern labels at bottom
        patterns = ["Strategy", "Observer", "State", "Command", "Chain of Responsibility"]
        chips_frame = tk.Frame(inner, bg=PRIMARY_DK)
        chips_frame.pack(pady=(30, 0))
        tk.Label(chips_frame, text="Design Patterns:", font=FONT_SMALL,
                 bg=PRIMARY_DK, fg="#C5C2FF").pack()
        for p in patterns:
            tk.Label(chips_frame, text=f"  ◆ {p}", font=FONT_SMALL,
                     bg=PRIMARY_DK, fg="#9996CC").pack(anchor=tk.W)

    # ── Right panel — login form ───────────────────────────────────────────

    def _build_right_form(self, parent):
        right = tk.Frame(parent, bg=BG)
        right.grid(row=0, column=1, sticky="nsew")

        # Centre the card vertically and horizontally
        card = tk.Frame(right, bg=SURFACE, padx=50, pady=50)
        card.place(relx=0.5, rely=0.5, anchor="center", width=460)

        # ── Title ─────────────────────────────────────────────────────────
        tk.Label(card, text="Welcome Back", font=("Segoe UI", 22, "bold"),
                 bg=SURFACE, fg=TEXT).pack(anchor=tk.W)
        tk.Label(card, text="Sign in to access the kiosk system",
                 font=FONT_BODY, bg=SURFACE, fg=TEXT_MUTED).pack(anchor=tk.W, pady=(4, 24))

        # ── Username ──────────────────────────────────────────────────────
        tk.Label(card, text="USERNAME", font=("Segoe UI", 8, "bold"),
                 bg=SURFACE, fg=TEXT_MUTED).pack(anchor=tk.W)
        self.username_var = tk.StringVar()
        self.user_entry = tk.Entry(card, textvariable=self.username_var,
                                   font=("Segoe UI", 13), bg=CARD, fg=TEXT,
                                   insertbackground=TEXT, relief=tk.FLAT, bd=0)
        self.user_entry.pack(fill=tk.X, ipady=10, pady=(4, 0))
        tk.Frame(card, bg=BORDER, height=2).pack(fill=tk.X, pady=(0, 18))

        # ── Password ──────────────────────────────────────────────────────
        tk.Label(card, text="PASSWORD", font=("Segoe UI", 8, "bold"),
                 bg=SURFACE, fg=TEXT_MUTED).pack(anchor=tk.W)
        self.password_var = tk.StringVar()
        self.pass_entry = tk.Entry(card, textvariable=self.password_var,
                                   font=("Segoe UI", 13), bg=CARD, fg=TEXT,
                                   insertbackground=TEXT, show="●",
                                   relief=tk.FLAT, bd=0)
        self.pass_entry.pack(fill=tk.X, ipady=10, pady=(4, 0))
        tk.Frame(card, bg=BORDER, height=2).pack(fill=tk.X, pady=(0, 8))

        # ── Show password toggle ───────────────────────────────────────────
        self.show_pw = tk.BooleanVar(value=False)
        tk.Checkbutton(card, text="Show password", variable=self.show_pw,
                       font=FONT_SMALL, bg=SURFACE, fg=TEXT_MUTED,
                       selectcolor=CARD, activebackground=SURFACE,
                       activeforeground=TEXT_MUTED,
                       command=self._toggle_pw).pack(anchor=tk.W, pady=(0, 16))

        # ── Error label ───────────────────────────────────────────────────
        self.error_var = tk.StringVar(value="")
        self.error_lbl = tk.Label(card, textvariable=self.error_var,
                                  font=("Segoe UI", 10, "bold"),
                                  bg=SURFACE, fg=DANGER)
        self.error_lbl.pack(anchor=tk.W, pady=(0, 10))

        # ── LOGIN BUTTON ──────────────────────────────────────────────────
        self.login_btn = tk.Button(
            card,
            text="     LOGIN   ",
            font=("Segoe UI", 14, "bold"),
            bg=PRIMARY,
            fg=TEXT,
            relief=tk.FLAT,
            cursor="hand2",
            pady=14,
            activebackground=PRIMARY_DK,
            activeforeground=TEXT,
            command=self._attempt_login
        )
        self.login_btn.pack(fill=tk.X, pady=(4, 0))
        self.login_btn.bind("<Enter>", lambda e: self.login_btn.config(bg=PRIMARY_DK))
        self.login_btn.bind("<Leave>", lambda e: self.login_btn.config(bg=PRIMARY))

        # ── Credentials hint card ─────────────────────────────────────────
        hint = tk.Frame(card, bg=CARD, padx=16, pady=12)
        hint.pack(fill=tk.X, pady=(24, 0))

        tk.Label(hint, text="Default Credentials", font=("Segoe UI", 9, "bold"),
                 bg=CARD, fg=TEXT_MUTED).pack(anchor=tk.W, pady=(0, 6))

        for uname, pwd, role, color in [
            ("admin", "admin123", "Administrator", SUCCESS),
            ("user",  "user123",  "Customer",       PRIMARY),
        ]:
            row = tk.Frame(hint, bg=CARD)
            row.pack(fill=tk.X, pady=2)
            tk.Label(row, text=f"{uname} / {pwd}",
                     font=("Consolas", 10), bg=CARD, fg=color).pack(side=tk.LEFT)
            tk.Label(row, text=f"  [{role}]",
                     font=("Segoe UI", 9), bg=CARD, fg=TEXT_MUTED).pack(side=tk.LEFT)

        # ── Key bindings ──────────────────────────────────────────────────
        self.root.bind("<Return>", lambda e: self._attempt_login())
        self.user_entry.focus_set()

    # ── Actions ───────────────────────────────────────────────────────────

    def _toggle_pw(self):
        self.pass_entry.config(show="" if self.show_pw.get() else "●")

    def _attempt_login(self):
        username = self.username_var.get().strip()
        password = self.password_var.get()

        if not username:
            self._show_error("Please enter your username.")
            self.user_entry.focus_set()
            return
        if not password:
            self._show_error("Please enter your password.")
            self.pass_entry.focus_set()
            return

        hashed = _hash(password)
        user = self.data_manager.verify_user(username, hashed)

        if user:
            self.error_var.set("")
            self.result = user
            self.root.destroy()
        else:
            self._show_error("Invalid username or password. Please try again.")
            self.password_var.set("")
            self.pass_entry.focus_set()

    def _show_error(self, msg: str):
        self.error_var.set(msg)
        # Flash the error label briefly
        self.error_lbl.config(fg=DANGER)

    def _on_cancel(self):
        self.result = None
        self.root.destroy()

    def show(self) -> dict:
        """Run the login window and return authenticated user dict or None."""
        self.root.mainloop()
        return self.result
