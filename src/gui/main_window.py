"""Main Window for NovaOCR Desktop Application"""
import os
import sys
from pathlib import Path
from datetime import datetime
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                              QPushButton, QLabel, QLineEdit, QFileDialog,
                              QTextEdit, QMenuBar, QMenu, QMessageBox)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QAction, QDragEnterEvent, QDropEvent

from .progress_widget import ProgressWidget
from .settings_dialog import SettingsDialog
from ..core.config_manager import ConfigManager
from ..core.file_handler import FileHandler
from ..core.batch_processor import BatchProcessor, ProcessingStats
from ..providers.mistral_ocr import MistralOCRProvider
from ..providers.mistral_llm import MistralLLMProvider
from ..output.docx_generator import DOCXGenerator
from ..output.txt_generator import TXTGenerator


class ProcessingThread(QThread):
    """Background thread for OCR processing"""
    progress_update = pyqtSignal(int, int, str)  # current, total, status
    stats_update = pyqtSignal(int, int, int, float)  # success, empty, failed, elapsed
    finished = pyqtSignal(object)  # stats
    error = pyqtSignal(str)  # error message
    
    def __init__(self, processor: BatchProcessor, file_paths, output_path):
        super().__init__()
        self.processor = processor
        self.file_paths = file_paths
        self.output_path = output_path
    
    def run(self):
        """Run processing in background"""
        try:
            def progress_callback(current, total, status):
                self.progress_update.emit(current, total, status)
                # Also emit stats update
                stats = self.processor.stats
                self.stats_update.emit(
                    stats.successful_files,
                    stats.empty_files,
                    stats.failed_files,
                    stats.get_elapsed_time()
                )
            
            stats = self.processor.process_files(
                self.file_paths,
                self.output_path,
                progress_callback
            )
            
            self.finished.emit(stats)
            
        except Exception as e:
            self.error.emit(str(e))


class MainWindow(QMainWindow):
    """
    Main application window for NovaOCR.
    
    Features drag-and-drop, folder selection, real-time progress tracking,
    and settings configuration.
    """
    
    def __init__(self):
        super().__init__()
        self.config = ConfigManager()
        self.processing_thread = None
        self.current_processor = None
        
        self.setWindowTitle("NovaOCR - Professional OCR Desktop Application")
        self.setMinimumSize(800, 600)
        
        self.init_ui()
        self.setAcceptDrops(True)
    
    def init_ui(self):
        """Initialize UI components"""
        # Create menu bar
        self.create_menu_bar()
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Title
        title = QLabel("NovaOCR - OCR + AI Text Cleanup")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Folder selection
        folder_layout = QHBoxLayout()
        
        self.folder_input = QLineEdit()
        self.folder_input.setPlaceholderText("Select or drag-and-drop folder containing images/PDFs...")
        self.folder_input.setReadOnly(True)
        
        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self.browse_folder)
        
        folder_layout.addWidget(QLabel("Input Folder:"))
        folder_layout.addWidget(self.folder_input)
        folder_layout.addWidget(browse_btn)
        
        layout.addLayout(folder_layout)
        
        # Output filename
        output_layout = QHBoxLayout()
        
        self.output_input = QLineEdit()
        self.output_input.setPlaceholderText("OUTPUT.docx")
        self.output_input.setText(f"OUTPUT_{datetime.now().strftime('%Y%m%d_%H%M%S')}.docx")
        
        output_layout.addWidget(QLabel("Output File:"))
        output_layout.addWidget(self.output_input)
        
        layout.addLayout(output_layout)
        
        # Progress widget
        self.progress_widget = ProgressWidget()
        layout.addWidget(self.progress_widget)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.start_btn = QPushButton("▶ Start Processing")
        self.start_btn.clicked.connect(self.start_processing)
        self.start_btn.setStyleSheet(
            "QPushButton { background-color: #4CAF50; color: white; "
            "padding: 10px; font-size: 14px; font-weight: bold; }"
        )
        
        self.pause_btn = QPushButton("⏸ Pause")
        self.pause_btn.clicked.connect(self.pause_processing)
        self.pause_btn.setEnabled(False)
        
        self.stop_btn = QPushButton("⏹ Stop")
        self.stop_btn.clicked.connect(self.stop_processing)
        self.stop_btn.setEnabled(False)
        
        button_layout.addWidget(self.start_btn)
        button_layout.addWidget(self.pause_btn)
        button_layout.addWidget(self.stop_btn)
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        
        # Log viewer
        log_label = QLabel("Processing Log:")
        layout.addWidget(log_label)
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(200)
        layout.addWidget(self.log_text)
        
        central_widget.setLayout(layout)
    
    def create_menu_bar(self):
        """Create menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("File")
        
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Settings menu
        settings_menu = menubar.addMenu("Settings")
        
        config_action = QAction("Configuration...", self)
        config_action.triggered.connect(self.open_settings)
        settings_menu.addAction(config_action)
        
        # Help menu
        help_menu = menubar.addMenu("Help")
        
        about_action = QAction("About NovaOCR", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def browse_folder(self):
        """Open folder browser"""
        folder = QFileDialog.getExistingDirectory(
            self,
            "Select Folder with Images/PDFs",
            "",
            QFileDialog.Option.ShowDirsOnly
        )
        
        if folder:
            self.folder_input.setText(folder)
            self.validate_folder(folder)
    
    def validate_folder(self, folder_path: str):
        """Validate selected folder"""
        is_valid, message, count = FileHandler.validate_folder(folder_path)
        
        if is_valid:
            if "Warning" in message:
                QMessageBox.warning(self, "Duplicate Files Detected", message)
            self.log(f"✅ Folder validated: {count} files found")
        else:
            QMessageBox.critical(self, "Invalid Folder", message)
            self.log(f"❌ {message}")
    
    def dragEnterEvent(self, event: QDragEnterEvent):
        """Handle drag enter event"""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
    
    def dropEvent(self, event: QDropEvent):
        """Handle drop event"""
        urls = event.mimeData().urls()
        if urls:
            folder_path = urls[0].toLocalFile()
            if os.path.isdir(folder_path):
                self.folder_input.setText(folder_path)
                self.validate_folder(folder_path)
    
    def open_settings(self):
        """Open settings dialog"""
        dialog = SettingsDialog(self)
        if dialog.exec():
            # Reload config after settings change
            self.config.reload()
            self.log("⚙️ Settings reloaded")
    
    def show_about(self):
        """Show about dialog"""
        QMessageBox.about(
            self,
            "About NovaOCR",
            "<h3>NovaOCR v1.0.0</h3>"
            "<p>Professional OCR Desktop Application with AI-powered text cleanup.</p>"
            "<p><b>Features:</b></p>"
            "<ul>"
            "<li>Mistral OCR for document processing</li>"
            "<li>AI-powered text cleanup and formatting</li>"
            "<li>Batch processing with progress tracking</li>"
            "<li>Configurable settings and prompts</li>"
            "</ul>"
        )
    
    def start_processing(self):
        """Start OCR processing"""
        folder_path = self.folder_input.text()
        output_filename = self.output_input.text()
        
        # Validation
        if not folder_path:
            QMessageBox.warning(self, "No Folder Selected", "Please select an input folder")
            return
        
        if not output_filename:
            QMessageBox.warning(self, "No Output File", "Please specify an output filename")
            return
        
        # Get file list
        try:
            file_paths = FileHandler.find_valid_files(folder_path)
            
            if not file_paths:
                QMessageBox.warning(self, "No Files", "No valid files found in folder")
                return
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to read folder:\n{str(e)}")
            return
        
        # Check API key
        api_key = self.config.get("api.mistral.api_key")
        if not api_key:
            QMessageBox.critical(
                self,
                "API Key Missing",
                "Mistral API key not configured!\n\n"
                "Please set it in Settings or as MISTRAL_API_KEY environment variable."
            )
            return
        
        # Initialize providers
        try:
            ocr_provider = MistralOCRProvider(
                api_key=api_key,
                model=self.config.get("api.mistral.ocr_model", "mistral-ocr-latest")
            )
            
            llm_provider = MistralLLMProvider(
                api_key=api_key,
                model=self.config.get("api.mistral.llm_model", "mistral-large-latest"),
                max_retries=self.config.get("processing.max_retries", 3),
                backoff_base=self.config.get("processing.retry_backoff_base", 2)
            )
            
            # Select output generator
            output_format = self.config.get("output.format", "docx")
            if output_format == "docx":
                output_generator = DOCXGenerator()
            else:
                output_generator = TXTGenerator()
            
            # Create processor
            self.current_processor = BatchProcessor(
                ocr_provider=ocr_provider,
                llm_provider=llm_provider,
                output_generator=output_generator,
                batch_size=self.config.get("processing.batch_size", 7),
                system_prompt=self.config.get_prompt("text_cleanup", "system_prompt"),
                temperature=self.config.get_prompt("text_cleanup", "temperature")
            )
            
        except Exception as e:
            QMessageBox.critical(self, "Initialization Error", f"Failed to initialize:\n{str(e)}")
            return
        
        # Output path
        output_path = os.path.join(folder_path, output_filename)
        
        # Update UI
        self.start_btn.setEnabled(False)
        self.pause_btn.setEnabled(True)
        self.stop_btn.setEnabled(True)
        self.progress_widget.reset()
        
        self.log(f"🚀 Starting processing: {len(file_paths)} files")
        
        # Start processing thread
        self.processing_thread = ProcessingThread(
            self.current_processor,
            file_paths,
            output_path
        )
        
        self.processing_thread.progress_update.connect(self.on_progress_update)
        self.processing_thread.stats_update.connect(self.on_stats_update)
        self.processing_thread.finished.connect(self.on_processing_finished)
        self.processing_thread.error.connect(self.on_processing_error)
        
        # Show initial feedback
        self.progress_widget.update_status("🚀 Initializing OCR processing...")
        self.log(f"📄 Processing {len(file_paths)} files...")
        self.log(f"💾 Output: {output_path}")
        
        self.processing_thread.start()
        self.log("✅ Processing thread started")
    
    def pause_processing(self):
        """Pause processing"""
        if self.current_processor:
            if self.current_processor._is_paused:
                self.current_processor.resume()
                self.pause_btn.setText("⏸ Pause")
                self.log("▶ Processing resumed")
            else:
                self.current_processor.pause()
                self.pause_btn.setText("▶ Resume")
                self.log("⏸ Processing paused")
    
    def stop_processing(self):
        """Stop processing"""
        if self.current_processor:
            self.current_processor.stop()
            self.log("⏹ Stopping processing...")
    
    def on_progress_update(self, current: int, total: int, status: str):
        """Handle progress update"""
        self.progress_widget.update_progress(current, total)
        self.progress_widget.update_status(status)
        self.log(status)
    
    def on_stats_update(self, success: int, empty: int, failed: int, elapsed: float):
        """Handle stats update"""
        self.progress_widget.update_stats(success, empty, failed, elapsed)
    
    def on_processing_finished(self, stats: ProcessingStats):
        """Handle processing completion"""
        self.start_btn.setEnabled(True)
        self.pause_btn.setEnabled(False)
        self.stop_btn.setEnabled(False)
        
        self.log("\n" + stats.get_summary())
        self.log("✅ Processing complete!")
        
        QMessageBox.information(
            self,
            "Processing Complete",
            f"Processing finished!\n\n{stats.get_summary()}"
        )
    
    def on_processing_error(self, error_msg: str):
        """Handle processing error"""
        self.start_btn.setEnabled(True)
        self.pause_btn.setEnabled(False)
        self.stop_btn.setEnabled(False)
        
        self.log(f"❌ Error: {error_msg}")
        
        QMessageBox.critical(
            self,
            "Processing Error",
            f"An error occurred during processing:\n{error_msg}"
        )
    
    def log(self, message: str):
        """Add message to log"""
        self.log_text.append(message)
        # Auto-scroll to bottom
        self.log_text.verticalScrollBar().setValue(
            self.log_text.verticalScrollBar().maximum()
        )
