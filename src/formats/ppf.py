from src.core.patcher import Patcher
from typing import Callable, Optional

class PPFPatcher(Patcher):
    """
    Patcher class for PPF patch files.
    """
    def validate_patch(self) -> bool:
        try:
            with open(self.patch_path, "rb") as f:
                header = f.read(3)
                return header == b"PPF"
        except Exception:
            return False

    def apply_patch(self, progress_callback: Optional[Callable[[float, str], None]] = None) -> bool:
        if not self.validate_patch():
            raise ValueError("Invalid PPF header. Expected 'PPF'.")

        with open(self.patch_path, "rb") as f_patch:
            f_patch.seek(3)
            version = f_patch.read(1)

            if version == b"1":
                f_patch.seek(56) 
            elif version in [b"2", b"3"]:
                f_patch.seek(60)

            with open(self.source_path, "rb") as f_src:
                rom_data = bytearray(f_src.read())

            patch_size = f_patch.seek(0, 2)
            f_patch.seek(60 if version != b"1" else 56)

            while f_patch.tell() < patch_size:
                offset_bytes = f_patch.read(8 if version == b"3" else 4)
                if not offset_bytes or len(offset_bytes) < (8 if version == b"3" else 4):
                    break

                offset = int.from_bytes(offset_bytes, byteorder="little")
                length = int.from_bytes(f_patch.read(1), byteorder="little")
                payload = f_patch.read(length)

                if offset + length > len(rom_data):
                    rom_data.extend(b"\x00" * (offset + length - len(rom_data)))

                rom_data[offset : offset + length] = payload

        with open(self.output_path, "wb") as f_out:
            f_out.write(rom_data)

        if progress_callback:
            progress_callback(100.0, "PPF disc patch applied successfully!")

        return True