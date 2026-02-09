"""NovaOCR Desktop Application"""
import sys
from PyQt6.QtWidgets import QApplication

from .main_window import MainWindow


class NovaOCRApp:
    """
    Main application class for NovaOCR desktop app.
    
    Handles Qt application initialization and window management.
    """
    
    def __init__(self):
        """Initialize application"""
        self.app = QApplication(sys.argv)
        self.app.setApplicationName("NovaOCR")
        self.app.setOrganizationName("NovaOCR")
        
        self.main_window = MainWindow()
    
    def run(self):
        """Run the application"""
        self.main_window.show()
        sys.exit(self.app.exec())


def run_gui():
    """Convenience function to run the GUI"""
    app = NovaOCRApp()
    app.run()
