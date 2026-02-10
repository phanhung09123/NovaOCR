"""Mistral OCR Provider using Official SDK"""
import base64
import os
from pathlib import Path
from typing import List
from mistralai import Mistral

from ..interfaces.ocr_provider import OCRProvider
from ..utils.logger import get_logger


class MistralOCRProvider(OCRProvider):
    """
    Mistral OCR provider implementation using official SDK.
    
    Uses mistral-ocr-latest model via client.ocr.process() method.
    Compatible with Colab code using mistralai SDK v1.12.0+
    """
    
    SUPPORTED_EXTENSIONS = ('.pdf', '.png', '.jpg', '.jpeg', '.webp')
    MIME_TYPES = {
        '.pdf': 'application/pdf',
        '.png': 'image/png',
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.webp': 'image/webp'
    }
    
    def __init__(self, api_key: str, model: str = "mistral-ocr-latest"):
        """
        Initialize Mistral OCR provider.
        
        Args:
            api_key: Mistral API key
            model: OCR model name (mistral-ocr-latest or mistral-ocr-2512)
        """
        if not api_key:
            raise ValueError("Mistral API key is required")
        
        self.api_key = api_key
        self.model = model
        self.client = Mistral(api_key=api_key)
        self.logger = get_logger()
        self.logger.info(f"✅ Initialized Mistral OCR with model: {model}")
    
    def extract_text(self, file_path: str) -> str:
        """
        Extract text from a single file using Mistral OCR SDK.
        
        Args:
            file_path: Path to file
            
        Returns:
            Extracted text as markdown
        """
        if not self.supports_file_type(file_path):
            raise ValueError(f"Unsupported file type: {file_path}")
        
        try:
            # Encode file to base64
            base64_data = self._encode_file(file_path)
            
            # Determine file type
            ext = Path(file_path).suffix.lower()
            mime = self.MIME_TYPES.get(ext, "image/jpeg")
            
            self.logger.info(f"🔄 Calling Mistral OCR SDK for {Path(file_path).name}...")
            
            import time
            start_time = time.time()
            
            # Create document payload exactly like Colab
            if ext == '.pdf':
                doc_payload = {
                    "type": "document_url",
                    "document_url": f"data:application/pdf;base64,{base64_data}"
                }
            else:
                doc_payload = {
                    "type": "image_url",
                    "image_url": f"data:{mime};base64,{base64_data}"
                }
            
            # Call OCR API using SDK - exactly like Colab
            ocr_response = self.client.ocr.process(
                model=self.model,
                document=doc_payload,
                include_image_base64=False
            )
            
            elapsed = time.time() - start_time
            
            # Extract markdown from pages - exactly like Colab
            raw_markdown = "\n".join([page.markdown for page in ocr_response.pages])
            extracted_text = raw_markdown.strip()
            
            if not extracted_text:
                self.logger.warning(f"OCR extracted empty text for {Path(file_path).name}")
            else:
                self.logger.info(f"⏱️  OCR completed in {elapsed:.1f}s - {len(extracted_text)} chars from {Path(file_path).name}")
            
            return extracted_text
            
        except Exception as e:
            self.logger.error(f"❌ OCR ERROR for {Path(file_path).name}: {str(e)}")
            import traceback
            self.logger.debug(f"   Traceback: {traceback.format_exc()}")
            return ""
    
    def extract_text_batch(self, file_paths: List[str]) -> List[str]:
        """
        Extract text from multiple files.
        
        Args:
            file_paths: List of file paths
            
        Returns:
            List of extracted texts
        """
        results = []
        for file_path in file_paths:
            text = self.extract_text(file_path)
            results.append(text)
        return results
    
    def supports_file_type(self, file_path: str) -> bool:
        """Check if file type is supported"""
        ext = Path(file_path).suffix.lower()
        return ext in self.SUPPORTED_EXTENSIONS
    
    def _encode_file(self, file_path: str) -> str:
        """Encode file to base64"""
        with open(file_path, "rb") as file:
            return base64.b64encode(file.read()).decode('utf-8')
