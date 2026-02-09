"""Abstract Output Generator Interface - Open/Closed Principle"""
from abc import ABC, abstractmethod


class OutputGenerator(ABC):
    """
    Abstract base class for output format generators.
    
    This interface allows easy extension with new output formats
    (PDF, EPUB, HTML, etc.) without modifying existing code.
    """
    
    @abstractmethod
    def generate(self, content: str, output_path: str) -> bool:
        """
        Generate output file from content.
        
        Args:
            content: The content to write (usually markdown format)
            output_path: Absolute path for the output file
            
        Returns:
            True if successful, False otherwise
            
        Raises:
            Exception: If generation fails
        """
        pass
    
    @abstractmethod
    def get_format_name(self) -> str:
        """
        Get the name of the output format.
        
        Returns:
            Format name (e.g., "DOCX", "TXT")
        """
        pass
