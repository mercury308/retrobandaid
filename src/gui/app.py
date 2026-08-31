import os
import tkinter as tk
from tkinter import ttk

from src.core.rom_manager import RomManager
from src.gui.components import FilePicker, ProgressPanel
from src.gui.dialogs import show_error, show_info, show_rom_info
from src.gui.theme import PALETTE, apply_theme
from src.utils.async_worker import AsyncWorker
from src.utils.config_manager import ConfigManager
from src.utils.logger import get_logger

logger = get_logger("gui")

PATCH_FILETYPES = [
    ("Patch files", "*.ips *.bps *.ups *.xdelta *.vcdiff *.ppf *.aps *.bsdiff *.bdf"),
    ("All files", "*.*"),
]
ROM_FILETYPES = [("All files", "*.*")]

POLL_INTERVAL_MS = 100
ICON_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "medicon.png")


class RetroBandaidApp(tk.Tk):
    """Main application window: pick a source ROM + patch, apply it, and show the result."""

    def __init__(self) -> None:
        super().__init__()
        self.title("\U0001fa79 RetroBandaid")
        self.resizable(False, False)
        self._set_window_icon()
        apply_theme(self)

        self.config_manager = ConfigManager()
        self.rom_manager = RomManager()
        self.worker = AsyncWorker()

        self._build_widgets()

    def _set_window_icon(self) -> None:
        """Overrides Tk's default feather icon with medicon.png, falling back to a blank icon."""
        try:
            icon = tk.PhotoImage(file=ICON_PATH)
        except tk.TclError:
            icon = tk.PhotoImage(width=1, height=1)
            icon.put(PALETTE["bg"], to=(0, 0))
        self.iconphoto(True, icon)
        self._icon_ref = icon  # keep a reference so Tk doesn't garbage-collect it

    def _build_widgets(self) -> None:
        pad = {"padx": 10, "pady": 6}

        self.source_picker = FilePicker(self, "Source ROM", filetypes=ROM_FILETYPES)
        self.source_picker.grid(row=0, column=0, sticky="ew", **pad)

        self.patch_picker = FilePicker(self, "Patch File", filetypes=PATCH_FILETYPES)
        self.patch_picker.grid(row=1, column=0, sticky="ew", **pad)

        self.output_picker = FilePicker(self, "Output ROM", filetypes=ROM_FILETYPES, save_mode=True)
        self.output_picker.grid(row=2, column=0, sticky="ew", **pad)

        button_row = ttk.Frame(self)
        button_row.grid(row=3, column=0, sticky="ew", **pad)
        button_row.columnconfigure((0, 1), weight=1)

        self.info_button = ttk.Button(button_row, text="\U0001fa79 Check ROM", command=self._on_rom_info)
        self.info_button.grid(row=0, column=0, sticky="ew", padx=(0, 4))

        self.apply_button = ttk.Button(button_row, text="\U0001f48a Patch it up!", command=self._on_apply)
        self.apply_button.grid(row=0, column=1, sticky="ew", padx=(4, 0))

        self.progress_panel = ProgressPanel(self)
        self.progress_panel.grid(row=4, column=0, sticky="ew", **pad)

        self.columnconfigure(0, weight=1, minsize=440)

    def _on_rom_info(self) -> None:
        source_path = self.source_picker.get()
        if not source_path:
            show_error(self, "Missing File", "Please choose a source ROM first.")
            return

        try:
            metadata = self.rom_manager.identify(source_path)
        except OSError as exc:
            show_error(self, "Error", f"Could not read ROM: {exc}")
            return

        show_rom_info(self, metadata)

    def _on_apply(self) -> None:
        source_path = self.source_picker.get()
        patch_path = self.patch_picker.get()
        output_path = self.output_picker.get()

        if not (source_path and patch_path and output_path):
            show_error(self, "Missing Fields", "Please select a source ROM, a patch file, and an output path.")
            return

        self.apply_button.state(["disabled"])
        self.progress_panel.reset()
        self.config_manager.set("last_source_dir", os.path.dirname(source_path))
        self.config_manager.set("last_patch_dir", os.path.dirname(patch_path))
        self.config_manager.set("last_output_dir", os.path.dirname(output_path))
        self.config_manager.save()

        self.worker.run(self.rom_manager.apply_patch, source_path, patch_path, output_path)
        self.after(POLL_INTERVAL_MS, self._poll_worker)

    def _poll_worker(self) -> None:
        event = self.worker.poll()
        if event is None:
            self.after(POLL_INTERVAL_MS, self._poll_worker)
            return

        kind, payload, error = event
        if kind == "progress":
            self.progress_panel.update_progress(payload, error or "")
            self.after(POLL_INTERVAL_MS, self._poll_worker)
        elif kind == "done":
            self.progress_panel.update_progress(100.0, "All better! \U0001f380")
            self.apply_button.state(["!disabled"])
            show_info(self, "Success", "Patch applied successfully.")
        elif kind == "error":
            self.progress_panel.reset()
            self.apply_button.state(["!disabled"])
            logger.exception("Patch failed", exc_info=error)
            show_error(self, "Patch Failed", str(error))


def main() -> None:
    app = RetroBandaidApp()
    app.mainloop()


if __name__ == "__main__":
    main()
