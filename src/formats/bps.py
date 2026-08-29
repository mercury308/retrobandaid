from src.core.patcher import Patcher
from typing import Callable, Optional
import zlib

class BPSPatcher(Patcher):
    """
    Patcher class for BPS patch files.
    """
    def validate_patch(self) -> bool:
        try:
            with open(self.patch_path, "rb") as f:
                header = f.read(4)
                return header == b"BPS1"
        except Exception:
            return False

    def _read_vint(self, f) -> int:
        """Decodes variable-length integer used in BPS."""
        value = 0
        shift = 1
        while True:
            b = f.read(1)
            if not b:
                raise EOFError("Unexpected end of BPS file")
            byte = b[0]
            value += (byte & 0x7F) * shift
            if byte & 0x80:
                break
            shift <<= 7
            value += shift
        return value

    def apply_patch(self, progress_callback: Optional[Callable[[float, str], None]] = None) -> bool:
        if not self.validate_patch():
            raise ValueError("Invalid BPS header. Expected 'BPS1'.")

        with open(self.patch_path, "rb") as f_patch:
            f_patch.seek(4) 
            
            with open(self.source_path, "rb") as f_src:
                source_data = f_src.read()

            source_size = self._read_vint(f_patch)
            target_size = self._read_vint(f_patch)
            metadata_size = self._read_vint(f_patch)
            
            f_patch.seek(metadata_size, 1)

            target_data = bytearray(target_size)
            source_relative_offset = 0
            target_relative_offset = 0
            output_offset = 0

            while output_offset < target_size:
                data = self._read_vint(f_patch)
                mode = data & 3
                length = (data >> 2) + 1

                if mode == 0:  
                    target_data[output_offset : output_offset + length] = source_data[output_offset : output_offset + length]
                    output_offset += length
                elif mode == 1: 
                    for _ in range(length):
                        target_data[output_offset] = f_patch.read(1)[0]
                        output_offset += 1
                elif mode == 2:  
                    offset_data = self._read_vint(f_patch)
                    source_relative_offset += -((offset_data >> 1)) if (offset_data & 1) else (offset_data >> 1)
                    target_data[output_offset : output_offset + length] = source_data[source_relative_offset : source_relative_offset + length]
                    source_relative_offset += length
                    output_offset += length
                elif mode == 3:  
                    offset_data = self._read_vint(f_patch)
                    target_relative_offset += -((offset_data >> 1)) if (offset_data & 1) else (offset_data >> 1)
                    for _ in range(length):
                        target_data[output_offset] = target_data[target_relative_offset]
                        output_offset += 1
                        target_relative_offset += 1

        with open(self.output_path, "wb") as f_out:
            f_out.write(target_data)

        if progress_callback:
            progress_callback(100.0, "BPS patch applied successfully!")

        return True