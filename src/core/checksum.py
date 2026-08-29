import hashlib
import zlib
from typing import Callable, Dict, Optional

def calculate_checksums(
    file_path: str,
    chunk_size: int = 64*1024,
    progress_callback: Optional[Callable[[float], None]] = None
) -> Dict[str, str]:
    """
    Calculates CRC32, MD5, and SHA256 checksums for a given file."""
    crc_val = 0
    md5_hash = hashlib.md5()
    sha256_hash = hashlib.sha256()

    total_size = 0
    try:
        import os
        total_size = os.path.getsize(file_path)
    except Exception as e:
        print(f"Error getting file size: {e}")

    with open(file_path, "rb") as f:
        while True:
            data = f.read(chunk_size)
            if not data:
                break
            crc_val = zlib.crc32(data, crc_val)
            md5_hash.update(data)
            sha256_hash.update(data)

            if progress_callback:
                progress_callback(f.tell() / total_size if total_size > 0 else 1.0)

    return {
        "crc32": format(crc_val & 0xffffffff, "08x"),
        "md5": md5_hash.hexdigest(),
        "sha256": sha256_hash.hexdigest()
    }
