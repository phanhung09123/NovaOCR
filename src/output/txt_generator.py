"""TXT Output Generator Implementation"""
from pathlib import Path

from ..interfaces.output_generator import OutputGenerator
from ..utils.logger import get_logger


class TXTGenerator(OutputGenerator):
    """
    Plain text output generator.
    
    Simple UTF-8 text file output.
    """
    
    def __init__(self):
        """Initialize TXT generator"""
        self.logger = get_logger()
    
    def generate(self, content: str, output_path: str) -> bool:
        """
        Generate TXT file.
        
        Args:
            content: Text content
            output_path: Output file path
            
        Returns:
            True if successful
        """
        try:
            # Ensure parent directory exists
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Write text file
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.logger.info(f"✅ Successfully created: {output_file.name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error creating TXT: {str(e)}")
            return False
    
    def get_format_name(self) -> str:
        """Get format name"""
        return "TXT"
