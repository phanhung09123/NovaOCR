"""Mistral OCR Provider Implementation using REST API"""
import base64
import os
import json
import requests
from pathlib import Path
from typing import List

from ..interfaces.ocr_provider import OCRProvider
from ..utils.logger import get_logger


class MistralOCRProvider(OCRProvider):
    """
    Mistral OCR provider implementation using REST API.
    
    Supports PDF and image formats using Mistral OCR REST endpoint.
    """
    
    SUPPORTED_EXTENSIONS = ('.pdf', '.png', '.jpg', '.jpeg', '.webp')
    MIME_TYPES = {
        '.pdf': 'application/pdf',
        '.png': 'image/png',
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.webp': 'image/webp'
    }
    
    API_ENDPOINT = "https://api.mistral.ai/v1/chat/completions"
    
    def __init__(self, api_key: str, model: str = "pixtral-12b-2409"):
        """
        Initialize Mistral OCR provider.
        
        Args:
            api_key: Mistral API key
            model: Vision model name (pixtral-12b-2409 supports vision)
        """
        if not api_key:
            raise ValueError("Mistral API key is required")
        
        self.api_key = api_key
        self.model = model
        self.logger = get_logger()
        self.logger.info(f"✅ Initialized Mistral OCR with model: {model}")
    
    def extract_text(self, file_path: str) -> str:
        """
        Extract text from a single file using Mistral Vision API.
        
        Args:
            file_path: Path to file
            
        Returns:
            Extracted text
        """
        if not self.supports_file_type(file_path):
            raise ValueError(f"Unsupported file type: {file_path}")
        
        try:
            # Encode file to base64
            base64_data = self._encode_file(file_path)
            
            # Determine file type
            ext = Path(file_path).suffix.lower()
            mime = self.MIME_TYPES.get(ext, "image/jpeg")
            
            self.logger.info(f"🔄 Calling Mistral Vision API for {Path(file_path).name}...")
            
            import time
            start_time = time.time()
            
            # Call Mistral Chat API with vision
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            payload = {
                "model": self.model,
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "Extract all text from this image. Return only the extracted text, nothing else. Preserve the original formatting and structure as much as possible."
                            },
                            {
                                "type": "image_url",
                                "image_url": f"data:{mime};base64,{base64_data}"
                            }
                        ]
                    }
                ]
            }
            
            response = requests.post(
                self.API_ENDPOINT,
                headers=headers,
                json=payload,
                timeout=60
            )
            
            elapsed = time.time() - start_time
            
            if response.status_code != 200:
                self.logger.error(f"❌ API Error {response.status_code}: {response.text}")
                return ""
            
            result = response.json()
            extracted_text = result.get("choices", [{}])[0].get("message", {}).get("content", "")
            
            if not extracted_text:
                self.logger.warning(f"OCR extracted empty text for {Path(file_path).name}")
            else:
                self.logger.info(f"⏱️  OCR completed in {elapsed:.1f}s - {len(extracted_text)} chars from {Path(file_path).name}")
            
            return extracted_text.strip()
            
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

import base64
import os
from pathlib import Path
from typing import List
from mistralai import Mistral

from ..interfaces.ocr_provider import OCRProvider
from ..utils.logger import get_logger


class MistralOCRProvider(OCRProvider):
    """
    Mistral OCR provider implementation.
    
    Supports PDF and image formats using Mistral OCR API.
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
            model: OCR model name
        """
        if not api_key:
            raise ValueError("Mistral API key is required")
        
        self.api_key = api_key
        self.model = model
        self.logger = get_logger()
        self.logger.debug(f"Initialized Mistral OCR with model: {model}")
    
    def extract_text(self, file_path: str) -> str:
        """
        Extract text from a single file using Mistral OCR.
        
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
            
            # Create payload based on file type
            if ext == '.pdf':
                doc_payload = {
                    "type": "document_url",
                    "document_url": f"data:application/pdf;base64,{base64_data}"
                }
            else:
                mime = self.MIME_TYPES.get(ext, "image/jpeg")
                doc_payload = {
                    "type": "image_url",
                    "image_url": f"data:{mime};base64,{base64_data}"
                }
            
            # Call Mistral OCR API
            self.logger.info(f"🔄 Calling Mistral OCR API for {Path(file_path).name}...")
            
            import time
            start_time = time.time()
            
            # Create client and call OCR
            client = Mistral(api_key=self.api_key)
            response = client.ocr.process(
                model=self.model,
                document=doc_payload
            )
            
            elapsed = time.time() - start_time
            self.logger.info(f"⏱️  OCR completed in {elapsed:.1f}s for {Path(file_path).name}")
            
            # Extract markdown from all pages
            if not response or not hasattr(response, 'pages'):
                self.logger.warning(f"OCR returned no response for {Path(file_path).name}")
                return ""
            
            if not response.pages:
                self.logger.warning(f"OCR returned empty pages for {Path(file_path).name}")
                return ""
            
            raw_markdown = "\n".join([page.markdown for page in response.pages])
            result = raw_markdown.strip()
            
            if not result:
                self.logger.warning(f"OCR extracted text is empty for {Path(file_path).name}")
            else:
                self.logger.debug(f"OCR extracted {len(result)} characters from {Path(file_path).name}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ OCR API ERROR for {Path(file_path).name}: {str(e)}")
            self.logger.error(f"   Exception type: {type(e).__name__}")
            # Print full traceback for debugging
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
