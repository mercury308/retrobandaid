import tkinter as tk
from tkinter import messagebox, ttk

from src.detection.metadata import RomMetadata


def show_error(parent: tk.Widget, title: str, message: str) -> None:
    messagebox.showerror(title, message, parent=parent)


def show_info(parent: tk.Widget, title: str, message: str) -> None:
    messagebox.showinfo(title, message, parent=parent)


def confirm(parent: tk.Widget, title: str, message: str) -> bool:
    return messagebox.askyesno(title, message, parent=parent)


def show_rom_info(parent: tk.Widget, metadata: RomMetadata) -> None:
    """Displays a modal dialog summarizing a RomMetadata result."""
    dialog = tk.Toplevel(parent)
    dialog.title("ROM Information")
    dialog.transient(parent)
    dialog.resizable(False, False)

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
        ttk.Label(dialog, text=f"{label}:", anchor="w", font=("TkDefaultFont", 9, "bold")).grid(
            row=i, column=0, sticky="w", padx=(10, 4), pady=2
        )
        ttk.Label(dialog, text=value, anchor="w", wraplength=360).grid(
            row=i, column=1, sticky="w", padx=(0, 10), pady=2
        )

    ttk.Button(dialog, text="Close", command=dialog.destroy).grid(
        row=len(rows), column=0, columnspan=2, pady=(8, 10)
    )

    dialog.grab_set()
