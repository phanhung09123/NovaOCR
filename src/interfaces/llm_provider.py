"""Abstract LLM Provider Interface - Open/Closed Principle"""
from abc import ABC, abstractmethod


class LLMProvider(ABC):
    """
    Abstract base class for LLM text cleaning providers.
    
    This interface allows easy extension with new LLM providers
    (OpenAI, Anthropic, Gemini, etc.) without modifying existing code.
    """
    
    @abstractmethod
    def clean_text(self, raw_text: str, system_prompt: str, temperature: float = 0) -> str:
        """
        Clean and process raw OCR text using AI.
        
        Args:
            raw_text: The raw OCR output to clean
            system_prompt: System prompt defining cleaning behavior
            temperature: Model temperature (0 = deterministic, higher = more creative)
            
        Returns:
            Cleaned text
            
        Raises:
            Exception: If LLM processing fails after all retries
        """
        pass
    
    @abstractmethod
    def get_model_name(self) -> str:
        """
        Get the name of the model being used.
        
        Returns:
            Model name string
        """
        pass
