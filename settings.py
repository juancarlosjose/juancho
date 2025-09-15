"""
Settings module for the MP3 to MIDI converter application.
"""
from PyQt6.QtCore import QSettings, QObject, pyqtSignal


class Settings(QObject):
    """Class for managing application settings."""
    
    # Define signals
    settingsChanged = pyqtSignal()
    
    def __init__(self):
        """Initialize the settings."""
        super().__init__()
        
        # Create settings object
        self.settings = QSettings("MP3toMIDI", "MP3toMIDI")
        
        # Default settings
        self.default_settings = {
            # General settings
            "general/recent_files": [],
            "general/max_recent_files": 10,
            
            # Audio settings
            "audio/default_volume": 0.7,
            
            # Separation settings
            "separation/default_method": "demucs",
            
            # Conversion settings
            "conversion/quantize": True,
            
            # Export settings
            "export/default_directory": "",
            
            # UI settings
            "ui/theme": "fusion",
            "ui/show_waveform": True,
            "ui/show_spectrogram": True,
            "ui/show_chromagram": True,
            "ui/show_piano_roll": True,
        }
        
        # Initialize settings
        self._initialize_settings()
    
    def _initialize_settings(self):
        """Initialize settings with default values if not set."""
        for key, value in self.default_settings.items():
            if not self.settings.contains(key):
                self.settings.setValue(key, value)
    
    def get(self, key: str, default=None):
        """
        Get a setting value.
        
        Args:
            key: Setting key
            default: Default value if not found
            
        Returns:
            Setting value
        """
        if default is None and key in self.default_settings:
            default = self.default_settings[key]
        
        return self.settings.value(key, default)
    
    def set(self, key: str, value):
        """
        Set a setting value.
        
        Args:
            key: Setting key
            value: Setting value
        """
        self.settings.setValue(key, value)
        self.settingsChanged.emit()
    
    def add_recent_file(self, file_path: str):
        """
        Add a file to the recent files list.
        
        Args:
            file_path: Path to the file
        """
        # Get current recent files
        recent_files = self.get("general/recent_files", [])
        
        # Remove if already in list
        if file_path in recent_files:
            recent_files.remove(file_path)
        
        # Add to beginning of list
        recent_files.insert(0, file_path)
        
        # Limit to max recent files
        max_recent = self.get("general/max_recent_files", 10)
        recent_files = recent_files[:max_recent]
        
        # Save updated list
        self.set("general/recent_files", recent_files)
    
    def get_recent_files(self):
        """
        Get the list of recent files.
        
        Returns:
            List of recent file paths
        """
        return self.get("general/recent_files", [])
    
    def clear_recent_files(self):
        """Clear the list of recent files."""
        self.set("general/recent_files", [])
    
    def reset_to_defaults(self):
        """Reset all settings to default values."""
        for key, value in self.default_settings.items():
            self.set(key, value)


# Create a global settings instance
settings = Settings()

