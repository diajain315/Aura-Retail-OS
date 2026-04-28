# Pattern: Implements Factory
import tkinter as tk
from tkinter import ttk
from gui.styles import *

class KioskSelectionScreen:

    
    def __init__(self, root):

        self.root = root
        self.kiosk_type = None
        self.result_window = None
        
        self._build_ui()
    
    def _build_ui(self):

        self.root.title("AURA Retail OS — Select Kiosk")
        self.root.geometry("720x520")
        self.root.configure(bg=BG)
        
        container = tk.Frame(self.root, bg=BG)
        container.pack(fill=tk.BOTH, expand=True)

        panel = tk.Frame(container, bg=SURFACE, padx=PAD, pady=PAD)
        panel.place(relx=0.5, rely=0.5, anchor=tk.CENTER, width=600, height=390)

        tk.Label(panel, text="AURA RETAIL OS", font=FONT_TITLE,
                 bg=SURFACE, fg=PRIMARY).pack(anchor=tk.W)
        tk.Label(panel, text="Choose kiosk type", font=FONT_HEADING,
                 bg=SURFACE, fg=TEXT).pack(anchor=tk.W, pady=(4, 6))
        tk.Label(panel, text="Select one option to launch the user page.", font=FONT_SMALL,
                 bg=SURFACE, fg=TEXT_MUTED).pack(anchor=tk.W, pady=(0, 14))

        options = [
            ("🍔 Food Kiosk", "food", "Quick retail sales"),
            ("💊 Pharmacy Kiosk", "pharmacy", "Medical and health products"),
            ("🚨 Emergency Relief", "emergency", "Critical supplies and limits"),
        ]

        for label, kiosk_type, description in options:
            btn = tk.Button(panel, text=f"{label}   ·   {description}", font=FONT_BTN,
                            bg=CARD, fg=TEXT, relief=tk.FLAT, cursor="hand2",
                            anchor="w", padx=14, pady=12,
                            command=lambda t=kiosk_type: self._select_kiosk(t))
            btn.pack(fill=tk.X, pady=8)
            btn.bind("<Enter>", lambda e, w=btn: w.config(bg=PRIMARY, fg=BG))
            btn.bind("<Leave>", lambda e, w=btn: w.config(bg=CARD, fg=TEXT))

        tk.Label(panel, text="Fast launch. Low friction. One click.", font=FONT_SMALL,
                 bg=SURFACE, fg=TEXT_MUTED).pack(anchor=tk.W, pady=(18, 0))
    
    def _select_kiosk(self, kiosk_type):

        self.kiosk_type = kiosk_type
        self.root.quit()
    
    def get_selected_kiosk(self):

        return self.kiosk_type
