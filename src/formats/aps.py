from src.core.patcher import Patcher
from typing import Callable, Optional

class APSPatcher(Patcher):
    """
    Patcher class for APS patch files.
    """
    def validate_patch(self) -> bool:
        try:
            with open(self.patch_path, "rb") as f:
                header = f.read(4)
                return header == b"APS1"
        except Exception:
            return False

    def apply_patch(self, progress_callback: Optional[Callable[[float, str], None]] = None) -> bool:
        if not self.validate_patch():
            raise ValueError("Invalid APS header. Expected 'APS1'.")

        with open(self.patch_path, "rb") as f_patch:
            f_patch.seek(4)
            patch_mode = f_patch.read(1)

            with open(self.source_path, "rb") as f_src:
                rom_data = bytearray(f_src.read())

            while True:
                offset_bytes = f_patch.read(4)
                if not offset_bytes or len(offset_bytes) < 4:
                    break

                offset = int.from_bytes(offset_bytes, byteorder="little")
                length = int.from_bytes(f_patch.read(2), byteorder="little")
                payload = f_patch.read(length)

                if offset + length > len(rom_data):
                    rom_data.extend(b"\x00" * (offset + length - len(rom_data)))

                rom_data[offset : offset + length] = payload

        with open(self.output_path, "wb") as f_out:
            f_out.write(rom_data)

        if progress_callback:
            progress_callback(100.0, "APS patch applied successfully!")

        return True