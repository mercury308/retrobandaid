from abc import ABC, abstractmethod
from typing import Callable, Optional, Type  

class Patcher(ABC):
    """
    Abstract base class for patchers.
    """
    def __init__(self, source_path: str, patch_patch: str, output_path: str):
        self.source_path = source_path
        self.patch_patch = patch_patch
        self.output_path = output_path

    @abstractmethod
    def verify_patch(self) -> bool:
        """
        Verify patch against the source file.
        Returns True if the patch is valid, False otherwise.
        """
        pass

    @abstractmethod
    def apply_patch(self, progress_callback: Optional[Callable[[float, str], None]] = None) -> bool:
        """
        Apply patch to the source file and write the result to the output path.
        Returns True if the patch was applied successfully, False otherwise.
        """
        pass