"""Abstract interfaces for NovaOCR providers"""
from .ocr_provider import OCRProvider
from .llm_provider import LLMProvider
from .output_generator import OutputGenerator

__all__ = ['OCRProvider', 'LLMProvider', 'OutputGenerator']
