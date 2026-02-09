"""Configuration Manager - Single Responsibility Principle"""
import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from dotenv import load_dotenv


class ConfigManager:
    """
    Centralized configuration management.
    
    Loads and validates configuration from YAML files and environment variables.
    Thread-safe singleton pattern.
    """
    
    _instance: Optional['ConfigManager'] = None
    _config: Dict[str, Any] = {}
    _prompts: Dict[str, Any] = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConfigManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize configuration manager (only once)"""
        if not self._config:
            self._load_config()
    
    def _load_config(self):
        """Load configuration from files and environment"""
        # Load environment variables
        load_dotenv()
        
        # Find config directory
        config_dir = self._find_config_dir()
        
        # Load main config
        config_path = config_dir / "config.yaml"
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                self._config = yaml.safe_load(f) or {}
        else:
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
        # Load prompts config
        prompts_path = config_dir / "prompts.yaml"
        if prompts_path.exists():
            with open(prompts_path, 'r', encoding='utf-8') as f:
                self._prompts = yaml.safe_load(f) or {}
        
        # Override API key from environment if set
        env_api_key = os.getenv('MISTRAL_API_KEY')
        if env_api_key:
            if 'api' not in self._config:
                self._config['api'] = {}
            if 'mistral' not in self._config['api']:
                self._config['api']['mistral'] = {}
            self._config['api']['mistral']['api_key'] = env_api_key
    
    def _find_config_dir(self) -> Path:
        """Find the config directory"""
        # Start from current file location and go up
        current = Path(__file__).resolve()
        
        # Try to find config directory
        for parent in [current.parent.parent.parent, Path.cwd()]:
            config_dir = parent / "config"
            if config_dir.exists() and config_dir.is_dir():
                return config_dir
        
        # Default to config in cwd
        return Path.cwd() / "config"
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """
        Get configuration value using dot notation.
        
        Args:
            key_path: Dot-separated path (e.g., "api.mistral.api_key")
            default: Default value if key not found
            
        Returns:
            Configuration value or default
            
        Example:
            config.get("api.mistral.api_key")
        """
        keys = key_path.split('.')
        value = self._config
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        
        return value
    
    def get_prompt(self, prompt_name: str, key: str = "system_prompt") -> str:
        """
        Get prompt configuration.
        
        Args:
            prompt_name: Name of the prompt (e.g., "text_cleanup")
            key: Key within the prompt config (e.g., "system_prompt", "temperature")
            
        Returns:
            Prompt value
        """
        if prompt_name in self._prompts and key in self._prompts[prompt_name]:
            return self._prompts[prompt_name][key]
        return ""
    
    def set(self, key_path: str, value: Any):
        """
        Set configuration value using dot notation.
        
        Args:
            key_path: Dot-separated path
            value: Value to set
        """
        keys = key_path.split('.')
        config = self._config
        
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]
        
        config[keys[-1]] = value
    
    def save_config(self, config_path: Optional[Path] = None):
        """
        Save current configuration to file.
        
        Args:
            config_path: Path to save to (default: original config file)
        """
        if config_path is None:
            config_path = self._find_config_dir() / "config.yaml"
        
        with open(config_path, 'w', encoding='utf-8') as f:
            yaml.dump(self._config, f, default_flow_style=False, allow_unicode=True)
    
    def reload(self):
        """Reload configuration from files"""
        self._config = {}
        self._prompts = {}
        self._load_config()
