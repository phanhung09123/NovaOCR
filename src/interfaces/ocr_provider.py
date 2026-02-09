"""Abstract OCR Provider Interface - Open/Closed Principle"""
from abc import ABC, abstractmethod
from typing import List


class OCRProvider(ABC):
    """
    Abstract base class for OCR providers.
    
    This interface allows easy extension with new OCR providers
    (Google Vision, Azure OCR, etc.) without modifying existing code.
    """
    
    @abstractmethod
    def extract_text(self, file_path: str) -> str:
        """
        Extract text from a single file.
        
        Args:
            file_path: Absolute path to the file (PDF, image, etc.)
            
        Returns:
            Extracted text as string
            
        Raises:
            Exception: If OCR processing fails
        """
        pass
    
    @abstractmethod
    def extract_text_batch(self, file_paths: List[str]) -> List[str]:
        """
        Extract text from multiple files.
        
        Args:
            file_paths: List of absolute paths to files
            
        Returns:
            List of extracted text strings (same order as input)
        """
        pass
    
    @abstractmethod
    def supports_file_type(self, file_path: str) -> bool:
        """
        Check if this provider supports the given file type.
        
        Args:
            file_path: Path to check
            
        Returns:
            True if supported, False otherwise
        """
        pass
