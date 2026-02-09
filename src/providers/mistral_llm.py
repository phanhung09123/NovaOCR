"""Mistral LLM Provider Implementation"""
import time
from mistralai import Mistral

from ..interfaces.llm_provider import LLMProvider
from ..utils.logger import get_logger


class MistralLLMProvider(LLMProvider):
    """
    Mistral LLM provider for text cleaning.
    
    Includes retry logic with exponential backoff.
    """
    
    def __init__(self, api_key: str, model: str = "mistral-large-latest", 
                 max_retries: int = 3, backoff_base: int = 2):
        """
        Initialize Mistral LLM provider.
        
        Args:
            api_key: Mistral API key
            model: LLM model name
            max_retries: Maximum number of retry attempts
            backoff_base: Base for exponential backoff (seconds)
        """
        if not api_key:
            raise ValueError("Mistral API key is required")
        
        self.api_key = api_key
        self.model = model
        self.max_retries = max_retries
        self.backoff_base = backoff_base
        self.client = Mistral(api_key=api_key)
        self.logger = get_logger()
    
    def clean_text(self, raw_text: str, system_prompt: str, temperature: float = 0) -> str:
        """
        Clean text using Mistral LLM with retry logic.
        
        Args:
            raw_text: Raw OCR text
            system_prompt: System prompt for cleaning instructions
            temperature: Model temperature (0 = deterministic)
            
        Returns:
            Cleaned text
        """
        for attempt in range(self.max_retries):
            try:
                response = self.client.chat.complete(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": f"Raw text to clean:\n\n{raw_text}"}
                    ],
                    temperature=temperature
                )
                
                cleaned_text = response.choices[0].message.content
                return cleaned_text
                
            except Exception as e:
                if attempt < self.max_retries - 1:
                    wait_time = self.backoff_base ** attempt
                    self.logger.warning(
                        f"LLM API error (attempt {attempt + 1}/{self.max_retries}), "
                        f"retrying in {wait_time}s: {str(e)}"
                    )
                    time.sleep(wait_time)
                else:
                    self.logger.error(
                        f"LLM cleaning failed after {self.max_retries} attempts: {str(e)}"
                    )
                    # Return original text as fallback
                    return raw_text
        
        return raw_text
    
    def get_model_name(self) -> str:
        """Get model name"""
        return self.model
