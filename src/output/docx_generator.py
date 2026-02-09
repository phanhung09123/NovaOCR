"""DOCX Output Generator Implementation"""
import pypandoc
from pathlib import Path

from ..interfaces.output_generator import OutputGenerator
from ..utils.logger import get_logger


class DOCXGenerator(OutputGenerator):
    """
    DOCX output generator using pypandoc.
    
    Converts markdown to DOCX format with fallback to TXT.
    """
    
    def __init__(self):
        """Initialize DOCX generator"""
        self.logger = get_logger()
    
    def generate(self, content: str, output_path: str) -> bool:
        """
        Generate DOCX file from markdown content.
        
        Args:
            content: Markdown content
            output_path: Output file path
            
        Returns:
            True if successful
        """
        try:
            # Ensure parent directory exists
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Convert markdown to DOCX
            pypandoc.convert_text(
                content,
                'docx',
                format='markdown',
                outputfile=str(output_file)
            )
            
            self.logger.info(f"✅ Successfully created: {output_file.name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error creating DOCX: {str(e)}")
            
            # Fallback to TXT
            try:
                txt_path = str(output_path).replace('.docx', '.txt')
                with open(txt_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.logger.info(f"📝 Saved as TXT fallback: {Path(txt_path).name}")
                return True
            except Exception as txt_error:
                self.logger.error(f"TXT fallback also failed: {str(txt_error)}")
                return False
    
    def get_format_name(self) -> str:
        """Get format name"""
        return "DOCX"
