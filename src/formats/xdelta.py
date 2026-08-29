import subprocess
import os
from src.core.patcher import Patcher
from typing import Callable, Optional

class XDeltaPatcher(Patcher):
    """
    Patcher class for XDelta patch files.
    """
    def validate_patch(self) -> bool:
        try:
            with open(self.patch_path, "rb") as f:
                header = f.read(4)
                return header in [b"\xd6\xc3\xc4\x00", b"VCD\x00"]
        except Exception:
            return False

    def apply_patch(self, progress_callback: Optional[Callable[[float, str], None]] = None) -> bool:
        cmd = [
            "xdelta3",
            "-d",
            "-s", self.source_path,
            self.patch_path,
            self.output_path
        ]

        if progress_callback:
            progress_callback(10.0, "Launching xDelta3 engine...")

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            raise RuntimeError(f"xDelta3 patching failed: {result.stderr}")

        if progress_callback:
            progress_callback(100.0, "xDelta patch applied successfully!")

        return True