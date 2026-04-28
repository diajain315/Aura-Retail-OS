# ── Color Palette ──────────────────────────────────────────────────────────
BG          = "#0f1117"   # root background
SURFACE     = "#1a1d2e"   # panel / frame bg
CARD        = "#252840"   # product card bg
CARD_HOVER  = "#2e3357"   # card hover highlight
PRIMARY     = "#6C63FF"   # accent purple
PRIMARY_DK  = "#534BBF"   # darker accent
SUCCESS     = "#00D9A3"   # green / active
WARNING     = "#FFA502"   # orange / power-saving
DANGER      = "#FF4757"   # red / emergency
PURPLE      = "#747EE0"   # purple / maintenance
TEXT        = "#E8E9F3"   # main text
TEXT_MUTED  = "#8B8FA8"   # secondary text
BORDER      = "#2d3154"   # subtle border
LOG_BG      = "#12141f"   # event log background

# ── State colors map ───────────────────────────────────────────────────────
MODE_COLORS = {
    "Active":             SUCCESS,
    "Power Saving":       WARNING,
    "Maintenance":        PURPLE,
    "Emergency Lockdown": DANGER,
}

# ── Pricing colors map ─────────────────────────────────────────────────────
PRICING_COLORS = {
    "Standard":   TEXT,
    "Discounted": SUCCESS,
    "Emergency":  DANGER,
}

# ── Fonts ──────────────────────────────────────────────────────────────────
FONT_TITLE    = ("Segoe UI", 18, "bold")
FONT_HEADING  = ("Segoe UI", 13, "bold")
FONT_BODY     = ("Segoe UI", 11)
FONT_SMALL    = ("Segoe UI", 9)
FONT_MONO     = ("Consolas", 10)
FONT_PRICE    = ("Segoe UI", 14, "bold")
FONT_ICON     = ("Segoe UI Emoji", 22)
FONT_BTN      = ("Segoe UI", 10, "bold")
FONT_STATUS   = ("Segoe UI", 10)

# ── Padding / spacing ──────────────────────────────────────────────────────
PAD         = 12
PAD_SM      = 6
CARD_RADIUS = 10
