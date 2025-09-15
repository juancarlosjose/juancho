"""
Module for exporting MIDI files.
"""
import os
import shutil
from typing import Dict, List, Optional
from PyQt6.QtCore import QObject, pyqtSignal


class MIDIExporter(QObject):
    """Class for exporting MIDI files."""
    
    # Define signals
    exportStarted = pyqtSignal(str)  # MIDI file name
    exportFinished = pyqtSignal(str, str)  # MIDI file name, destination path
    exportError = pyqtSignal(str, str)  # MIDI file name, error message
    
    def __init__(self):
        """Initialize the MIDI exporter."""
        super().__init__()
    
    def export_midi(self, midi_path: str, destination_path: str) -> bool:
        """
        Export a MIDI file to a destination path.
        
        Args:
            midi_path: Path to the MIDI file
            destination_path: Destination path
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Emit export started signal
            midi_name = os.path.basename(midi_path)
            self.exportStarted.emit(midi_name)
            
            # Create destination directory if it doesn't exist
            os.makedirs(os.path.dirname(destination_path), exist_ok=True)
            
            # Copy the MIDI file
            shutil.copy2(midi_path, destination_path)
            
            # Emit export finished signal
            self.exportFinished.emit(midi_name, destination_path)
            
            return True
            
        except Exception as e:
            # Emit export error signal
            self.exportError.emit(midi_name, str(e))
            return False
    
    def export_all_midis(self, midi_files: Dict[str, str], destination_dir: str) -> Dict[str, bool]:
        """
        Export all MIDI files to a destination directory.
        
        Args:
            midi_files: Dictionary of MIDI file names and paths
            destination_dir: Destination directory
            
        Returns:
            Dictionary of MIDI file names and export status
        """
        # Create destination directory if it doesn't exist
        os.makedirs(destination_dir, exist_ok=True)
        
        # Export each MIDI file
        results = {}
        for name, path in midi_files.items():
            destination_path = os.path.join(destination_dir, f"{name}.mid")
            results[name] = self.export_midi(path, destination_path)
        
        return results

