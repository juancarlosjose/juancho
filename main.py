"""
Main entry point for the MP3 to MIDI converter application.
"""
import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QDir
from main_window import MainWindow


def main():
    """Main entry point."""
    # Create application
    app = QApplication(sys.argv)
    app.setApplicationName("MP3 to MIDI Converter")
    app.setOrganizationName("MP3toMIDI")
    
    # Set style sheet
    app.setStyle("Fusion")
    
    # Create main window
    window = MainWindow()
    window.show()
    
    # Run application
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

