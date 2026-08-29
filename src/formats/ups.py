import zlib
from src.core.patcher import Patcher
from typing import Callable, Optional

class UPSPatcher(Patcher):
    """
    Patcher class for UPS patch files.
    """
    def validate_patch(self) -> bool:
        try:
            with open(self.patch_path, "rb") as f:
                header = f.read(4)
                return header == b"UPS1"
        except Exception:
            return False

    def _read_vint(self, f) -> int:
        value = 0
        shift = 1
        while True:
            b = f.read(1)
            if not b:
                raise EOFError("Unexpected end of UPS patch")
            byte = b[0]
            value += (byte & 0x7F) * shift
            if byte & 0x80:
                break
            shift <<= 7
            value += shift
        return value

    def apply_patch(self, progress_callback: Optional[Callable[[float, str], None]] = None) -> bool:
        if not self.validate_patch():
            raise ValueError("Invalid UPS header. Expected 'UPS1'.")

        with open(self.patch_path, "rb") as f_patch:
            f_patch.seek(4)
            with open(self.source_path, "rb") as f_src:
                src_data = bytearray(f_src.read())

            src_size = self._read_vint(f_patch)
            dst_size = self._read_vint(f_patch)

            dst_data = bytearray(dst_size)
            copy_len = min(len(src_data), dst_size)
            dst_data[:copy_len] = src_data[:copy_len]

            offset = 0
            while f_patch.tell() < (f_patch.seek(0, 2) - 12):
                f_patch.seek(f_patch.tell()) 
                offset += self._read_vint(f_patch)

                while True:
                    b = f_patch.read(1)
                    if not b or b[0] == 0:
                        break
                    if offset < dst_size:
                        dst_data[offset] ^= b[0]
                    offset += 1
                offset += 1

        with open(self.output_path, "wb") as f_out:
            f_out.write(dst_data)

        if progress_callback:
            progress_callback(100.0, "UPS patch applied successfully!")

        return True