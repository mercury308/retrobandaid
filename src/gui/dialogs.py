import tkinter as tk
from tkinter import messagebox, ttk

from src.detection.metadata import RomMetadata
from src.gui.theme import FONT, FONT_BOLD, PALETTE


def show_error(parent: tk.Widget, title: str, message: str) -> None:
    messagebox.showerror(title, message, parent=parent)


def show_info(parent: tk.Widget, title: str, message: str) -> None:
    messagebox.showinfo(title, message, parent=parent)


def confirm(parent: tk.Widget, title: str, message: str) -> bool:
    return messagebox.askyesno(title, message, parent=parent)


def show_rom_info(parent: tk.Widget, metadata: RomMetadata) -> None:
    """Displays a modal dialog summarizing a RomMetadata result."""
    dialog = tk.Toplevel(parent)
    dialog.title("\U0001fa79 ROM Checkup")
    dialog.transient(parent)
    dialog.resizable(False, False)
    dialog.configure(bg=PALETTE["bg"])

    rows = [
        ("File", metadata.path),
        ("System", metadata.system or "Unknown"),
        ("Size", f"{metadata.size:,} bytes"),
        ("Header detected", "Yes" if metadata.has_header else "No"),
        ("CRC32", metadata.checksums.get("crc32", "-")),
        ("MD5", metadata.checksums.get("md5", "-")),
        ("SHA256", metadata.checksums.get("sha256", "-")),
        ("Known title", metadata.known_name or "-"),
    ]

    for i, (label, value) in enumerate(rows):
        ttk.Label(dialog, text=f"{label}:", anchor="w", font=FONT_BOLD).grid(
            row=i, column=0, sticky="w", padx=(10, 4), pady=2
        )
        ttk.Label(dialog, text=value, anchor="w", wraplength=360, font=FONT).grid(
            row=i, column=1, sticky="w", padx=(0, 10), pady=2
        )

    ttk.Button(dialog, text="Close \U0001f48a", command=dialog.destroy).grid(
        row=len(rows), column=0, columnspan=2, pady=(8, 10)
    )

    dialog.grab_set()
