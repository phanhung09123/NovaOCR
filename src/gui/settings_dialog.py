"""Settings Dialog for configuring application"""
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                              QLineEdit, QSpinBox, QDoubleSpinBox, QPushButton,
                              QTextEdit, QGroupBox, QComboBox, QFormLayout,
                              QMessageBox)
from PyQt6.QtCore import Qt

from ..core.config_manager import ConfigManager


class SettingsDialog(QDialog):
    """
    Settings configuration dialog.
    
    Allows editing API keys, models, and parameters.
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.config = ConfigManager()
        self.setWindowTitle("NovaOCR Settings")
        self.setMinimumWidth(600)
        self.setMinimumHeight(500)
        self.init_ui()
        self.load_settings()
    
    def init_ui(self):
        """Initialize UI components"""
        layout = QVBoxLayout()
        
        # API Settings
        api_group = QGroupBox("API Configuration")
        api_layout = QFormLayout()
        
        self.api_key_input = QLineEdit()
        self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.api_key_input.setPlaceholderText("Enter Mistral API key or leave empty for env variable")
        api_layout.addRow("Mistral API Key:", self.api_key_input)
        
        self.ocr_model_input = QLineEdit()
        self.ocr_model_input.setPlaceholderText("mistral-ocr-latest")
        api_layout.addRow("OCR Model:", self.ocr_model_input)
        
        self.llm_model_input = QLineEdit()
        self.llm_model_input.setPlaceholderText("mistral-large-latest")
        api_layout.addRow("LLM Model:", self.llm_model_input)
        
        api_group.setLayout(api_layout)
        layout.addWidget(api_group)
        
        # Processing Settings
        proc_group = QGroupBox("Processing Configuration")
        proc_layout = QFormLayout()
        
        self.batch_size_input = QSpinBox()
        self.batch_size_input.setMinimum(1)
        self.batch_size_input.setMaximum(20)
        self.batch_size_input.setValue(7)
        proc_layout.addRow("Batch Size:", self.batch_size_input)
        
        self.max_retries_input = QSpinBox()
        self.max_retries_input.setMinimum(1)
        self.max_retries_input.setMaximum(10)
        self.max_retries_input.setValue(3)
        proc_layout.addRow("Max Retries:", self.max_retries_input)
        
        self.backoff_input = QSpinBox()
        self.backoff_input.setMinimum(1)
        self.backoff_input.setMaximum(10)
        self.backoff_input.setValue(2)
        proc_layout.addRow("Retry Backoff (s):", self.backoff_input)
        
        proc_group.setLayout(proc_layout)
        layout.addWidget(proc_group)
        
        # Output Settings
        output_group = QGroupBox("Output Configuration")
        output_layout = QFormLayout()
        
        self.format_combo = QComboBox()
        self.format_combo.addItems(["docx", "txt"])
        output_layout.addRow("Output Format:", self.format_combo)
        
        output_group.setLayout(output_layout)
        layout.addWidget(output_group)
        
        # Prompt Editor
        prompt_group = QGroupBox("System Prompt (Editable)")
        prompt_layout = QVBoxLayout()
        
        self.prompt_editor = QTextEdit()
        self.prompt_editor.setMinimumHeight(150)
        prompt_layout.addWidget(self.prompt_editor)
        
        prompt_group.setLayout(prompt_layout)
        layout.addWidget(prompt_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        save_btn = QPushButton("Save Settings")
        save_btn.clicked.connect(self.save_settings)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        button_layout.addStretch()
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def load_settings(self):
        """Load settings from config"""
        # API settings
        api_key = self.config.get("api.mistral.api_key", "")
        self.api_key_input.setText(api_key if api_key else "")
        
        self.ocr_model_input.setText(
            self.config.get("api.mistral.ocr_model", "mistral-ocr-latest")
        )
        
        self.llm_model_input.setText(
            self.config.get("api.mistral.llm_model", "mistral-large-latest")
        )
        
        # Processing settings
        self.batch_size_input.setValue(
            self.config.get("processing.batch_size", 7)
        )
        
        self.max_retries_input.setValue(
            self.config.get("processing.max_retries", 3)
        )
        
        self.backoff_input.setValue(
            self.config.get("processing.retry_backoff_base", 2)
        )
        
        # Output settings
        output_format = self.config.get("output.format", "docx")
        index = self.format_combo.findText(output_format)
        if index >= 0:
            self.format_combo.setCurrentIndex(index)
        
        # Prompt
        prompt = self.config.get_prompt("text_cleanup", "system_prompt")
        self.prompt_editor.setPlainText(prompt)
    
    def save_settings(self):
        """Save settings to config"""
        try:
            # Save API settings
            api_key = self.api_key_input.text().strip()
            if api_key:
                self.config.set("api.mistral.api_key", api_key)
            
            self.config.set("api.mistral.ocr_model", self.ocr_model_input.text())
            self.config.set("api.mistral.llm_model", self.llm_model_input.text())
            
            # Save processing settings
            self.config.set("processing.batch_size", self.batch_size_input.value())
            self.config.set("processing.max_retries", self.max_retries_input.value())
            self.config.set("processing.retry_backoff_base", self.backoff_input.value())
            
            # Save output settings
            self.config.set("output.format", self.format_combo.currentText())
            
            # Save to file
            self.config.save_config()
            
            QMessageBox.information(
                self,
                "Settings Saved",
                "Settings have been saved successfully!\n\n"
                "Note: Restart the application for all changes to take effect."
            )
            
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error Saving Settings",
                f"Failed to save settings:\n{str(e)}"
            )
