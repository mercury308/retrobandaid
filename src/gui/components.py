import tkinter as tk
from tkinter import filedialog, ttk
from typing import Callable, Iterable, Optional, Tuple


class FilePicker(ttk.Frame):
    """A labeled entry + Browse button for picking an existing file or a save destination."""

    def __init__(
        self,
        parent: tk.Widget,
        label: str,
        filetypes: Iterable[Tuple[str, str]] = (("All files", "*.*"),),
        save_mode: bool = False,
        on_change: Optional[Callable[[str], None]] = None,
    ) -> None:
        super().__init__(parent)
        self._filetypes = list(filetypes)
        self._save_mode = save_mode
        self._on_change = on_change

        self.columnconfigure(1, weight=1)
        ttk.Label(self, text=label, width=14, anchor="w").grid(row=0, column=0, sticky="w")

        self.path_var = tk.StringVar()
        entry = ttk.Entry(self, textvariable=self.path_var)
        entry.grid(row=0, column=1, sticky="ew", padx=(4, 4))

        ttk.Button(self, text="Browse...", command=self._browse).grid(row=0, column=2)

    def _browse(self) -> None:
        if self._save_mode:
            path = filedialog.asksaveasfilename(filetypes=self._filetypes)
        else:
            path = filedialog.askopenfilename(filetypes=self._filetypes)

        if path:
            self.path_var.set(path)
            if self._on_change:
                self._on_change(path)

    def get(self) -> str:
        return self.path_var.get()

    def set(self, path: str) -> None:
        self.path_var.set(path)


class ProgressPanel(ttk.Frame):
    """A progress bar paired with a status label, driven by (percent, message) updates."""

    def __init__(self, parent: tk.Widget) -> None:
        super().__init__(parent)
        self.columnconfigure(0, weight=1)

        self.progress_var = tk.DoubleVar(value=0.0)
        self.progress_bar = ttk.Progressbar(
            self, orient="horizontal", mode="determinate", maximum=100.0, variable=self.progress_var
        )
        self.progress_bar.grid(row=0, column=0, sticky="ew")

        self.status_var = tk.StringVar(value="Ready")
        ttk.Label(self, textvariable=self.status_var, anchor="w").grid(row=1, column=0, sticky="ew", pady=(2, 0))

    def update_progress(self, percent: float, message: str = "") -> None:
        self.progress_var.set(max(0.0, min(100.0, percent)))
        if message:
            self.status_var.set(message)

    def reset(self) -> None:
        self.progress_var.set(0.0)
        self.status_var.set("Ready")
