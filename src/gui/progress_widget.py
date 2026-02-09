"""Progress Widget for displaying processing progress"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                              QProgressBar, QGroupBox)
from PyQt6.QtCore import Qt


class ProgressWidget(QWidget):
    """
    Custom widget for displaying batch processing progress.
    """
    
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        """Initialize UI components"""
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Group box
        group_box = QGroupBox("Processing Progress")
        group_layout = QVBoxLayout()
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        group_layout.addWidget(self.progress_bar)
        
        # Status label
        self.status_label = QLabel("Ready to process")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        group_layout.addWidget(self.status_label)
        
        # Statistics row
        stats_layout = QHBoxLayout()
        
        self.success_label = QLabel("✅ Success: 0")
        self.empty_label = QLabel("📭 Empty: 0")
        self.failed_label = QLabel("❌ Failed: 0")
        self.time_label = QLabel("⏱️ Time: 0s")
        
        stats_layout.addWidget(self.success_label)
        stats_layout.addWidget(self.empty_label)
        stats_layout.addWidget(self.failed_label)
        stats_layout.addWidget(self.time_label)
        stats_layout.addStretch()
        
        group_layout.addLayout(stats_layout)
        
        group_box.setLayout(group_layout)
        layout.addWidget(group_box)
        
        self.setLayout(layout)
    
    def update_progress(self, current: int, total: int):
        """Update progress bar"""
        if total > 0:
            percentage = int((current / total) * 100)
            self.progress_bar.setValue(percentage)
            self.progress_bar.setFormat(f"{current}/{total} files ({percentage}%)")
    
    def update_status(self, status: str):
        """Update status text"""
        self.status_label.setText(status)
    
    def update_stats(self, success: int, empty: int, failed: int, elapsed: float):
        """Update statistics"""
        self.success_label.setText(f"✅ Success: {success}")
        self.empty_label.setText(f"📭 Empty: {empty}")
        self.failed_label.setText(f"❌ Failed: {failed}")
        self.time_label.setText(f"⏱️ Time: {elapsed:.1f}s")
    
    def reset(self):
        """Reset all values"""
        self.progress_bar.setValue(0)
        self.progress_bar.setFormat("0%")
        self.status_label.setText("Ready to process")
        self.update_stats(0, 0, 0, 0.0)
