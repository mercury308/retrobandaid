from src.core.patcher import Patcher
from typing import Callable, Optional

class IPSPatcher(Patcher):
    """
    Patcher class for IPS patch files.
    """
    def verify_patch(self) -> bool:
        try:
            with open(self.patch_patch, "rb") as f:
                header = f.read(5)
                return header == b"PATCH"
        except Exception:
            return False

    def apply_patch(self, progress_callback: Optional[Callable[[float, str], None]] = None) -> bool:
        if not self.verify_patch():
            raise ValueError("Invalid IPS patch file. The patch file does not start with the 'PATCH' header.")

        with open(self.source_path, "rb") as f_in:
            rom_data = bytearray(f_in.read())

        with open(self.patch_patch, "rb") as f_patch:
            f_patch.seek(5)

            while True:
                offset_bytes = f_patch.read(3)
                if not offset_bytes or offset_bytes == b"EOF":
                    break

                offset = int.from_bytes(offset_bytes, byteorder='big')
                size = int.from_bytes(f_patch.read(2), byteorder='big')

                if size == 0:
                    # RLE patch block
                    rle_size = int.from_bytes(f_patch.read(2), byteorder='big')
                    rle_value = f_patch.read(1)

                    if offset+rle_size > len(rom_data):
                        rom_data.extend(b'\x00' * (offset + rle_size - len(rom_data)))
                    rom_data[offset:offset+rle_size] = rle_value * rle_size
                else:
                    payload = f_patch.read(size)

                    if offset+size > len(rom_data):
                        rom_data.extend(b'\x00' * (offset + size - len(rom_data)))
                    rom_data[offset:offset+size] = payload
        with open(self.output_path, "wb") as f_out:
            f_out.write(rom_data)

        if progress_callback:
            progress_callback(1.0, "IPS patch applied successfully!")

        return True
                    