import tkinter as tk
from tkinter import ttk

PALETTE = {
    "bg": "#FFF5F8",
    "panel": "#FFD6E8",
    "accent": "#FF6FA0",
    "mint": "#B8E6E1",
    "text": "#5C4A4A",
}
FONT = ("Comic Sans MS", 10)
FONT_BOLD = ("Comic Sans MS", 10, "bold")
FONT_TITLE = ("Comic Sans MS", 13, "bold")


def apply_theme(root: tk.Tk) -> None:
    """Applies the kawaii medical-themed ttk style to the whole application."""
    root.configure(bg=PALETTE["bg"])

    style = ttk.Style(root)
    style.theme_use("clam")

    style.configure("TFrame", background=PALETTE["bg"])
    style.configure("TLabel", background=PALETTE["bg"], foreground=PALETTE["text"], font=FONT)
    style.configure(
        "TButton", font=FONT, foreground=PALETTE["text"],
        background=PALETTE["panel"], borderwidth=0, padding=8,
    )
    style.map("TButton", background=[("active", PALETTE["accent"])])
    style.configure("TEntry", fieldbackground="white", foreground=PALETTE["text"], padding=4)
    style.configure(
        "TProgressbar", troughcolor=PALETTE["panel"], background=PALETTE["mint"], thickness=14,
    )
