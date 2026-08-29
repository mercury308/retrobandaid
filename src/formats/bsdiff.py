import subprocess
from src.core.patcher import Patcher
from typing import Callable, Optional

class BSDiffPatcher(Patcher):
    """
    Patcher class for BSDiff patch files.
    """
    def validate_patch(self) -> bool:
        try:
            with open(self.patch_path, "rb") as f:
                header = f.read(8)
                return header in [b"BSDIFF40", b"ENDSLEY/"]
        except Exception:
            return False

    def apply_patch(self, progress_callback: Optional[Callable[[float, str], None]] = None) -> bool:
        cmd = [
            "bspatch",
            self.source_path,
            self.output_path,
            self.patch_path
        ]

        if progress_callback:
            progress_callback(10.0, "Launching BSDiff engine...")

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            raise RuntimeError(f"BSDiff patching failed: {result.stderr}")

        if progress_callback:
            progress_callback(100.0, "BSDiff patch applied successfully!")

        return True