"""
Controller for the MP3 to MIDI converter application.
"""
import os
import tempfile
from typing import Dict, Optional, Any
import pretty_midi
from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot

from audio_core import AudioFile, load_audio_file
from audio_player import AudioPlayer, MIDIPlayer
from audio_separator import AudioSeparator
from audio_analyzer import AudioAnalyzer
from midi_converter import MIDIConverter
from midi_exporter import MIDIExporter


class AppController(QObject):
    """Controller for the MP3 to MIDI converter application."""
    
    # Define signals
    fileLoaded = pyqtSignal(AudioFile)
    fileLoadError = pyqtSignal(str)
    
    analysisStarted = pyqtSignal()
    analysisProgress = pyqtSignal(int)
    analysisFinished = pyqtSignal(dict)
    analysisError = pyqtSignal(str)
    
    separationStarted = pyqtSignal()
    separationProgress = pyqtSignal(int)
    separationFinished = pyqtSignal(dict)
    separationError = pyqtSignal(str)
    
    conversionStarted = pyqtSignal()
    conversionProgress = pyqtSignal(int)
    conversionFinished = pyqtSignal(dict)
    conversionError = pyqtSignal(str)
    
    exportStarted = pyqtSignal(str)
    exportFinished = pyqtSignal(str, str)
    exportError = pyqtSignal(str, str)
    
    def __init__(self):
        """Initialize the controller."""
        super().__init__()
        
        # Initialize state
        self.audio_file = None
        self.temp_dir = tempfile.mkdtemp()
        self.stems = {}
        self.midi_files = {}
        self.analysis_results = {}
        
        # Create components
        self.audio_player = AudioPlayer()
        self.midi_player = MIDIPlayer()
        self.audio_separator = AudioSeparator()
        self.audio_analyzer = AudioAnalyzer()
        self.midi_converter = MIDIConverter()
        self.midi_exporter = MIDIExporter()
        
        # Connect signals
        self._connect_signals()
    
    def _connect_signals(self):
        """Connect signals to slots."""
        # Audio separator
        self.audio_separator.separationStarted.connect(self.separationStarted.emit)
        self.audio_separator.separationProgress.connect(self.separationProgress.emit)
        self.audio_separator.separationFinished.connect(self._on_separation_finished)
        self.audio_separator.separationError.connect(self.separationError.emit)
        
        # Audio analyzer
        self.audio_analyzer.analysisStarted.connect(self.analysisStarted.emit)
        self.audio_analyzer.analysisProgress.connect(self.analysisProgress.emit)
        self.audio_analyzer.analysisFinished.connect(self._on_analysis_finished)
        self.audio_analyzer.analysisError.connect(self.analysisError.emit)
        
        # MIDI converter
        self.midi_converter.conversionStarted.connect(self.conversionStarted.emit)
        self.midi_converter.conversionProgress.connect(self.conversionProgress.emit)
        self.midi_converter.conversionFinished.connect(self._on_conversion_finished)
        self.midi_converter.conversionError.connect(self.conversionError.emit)
        
        # MIDI exporter
        self.midi_exporter.exportStarted.connect(self.exportStarted.emit)
        self.midi_exporter.exportFinished.connect(self.exportFinished.emit)
        self.midi_exporter.exportError.connect(self.exportError.emit)
    
    def load_audio_file(self, file_path: str) -> None:
        """
        Load an audio file.
        
        Args:
            file_path: Path to the audio file
        """
        try:
            # Load the audio file
            self.audio_file = load_audio_file(file_path)
            
            # Load the file in the audio player
            self.audio_player.load_file(file_path)
            
            # Emit file loaded signal
            self.fileLoaded.emit(self.audio_file)
            
            # Analyze the audio
            self.analyze_audio()
            
        except Exception as e:
            # Emit file load error signal
            self.fileLoadError.emit(str(e))
    
    def analyze_audio(self) -> None:
        """Analyze the audio file."""
        if self.audio_file:
            # Start analysis
            self.audio_analyzer.analyze(
                self.audio_file.mono_audio,
                self.audio_file.sample_rate
            )
    
    def separate_audio(self, method: str) -> None:
        """
        Separate audio into stems.
        
        Args:
            method: Separation method
        """
        if self.audio_file:
            # Create output directory
            output_dir = os.path.join(self.temp_dir, "stems")
            os.makedirs(output_dir, exist_ok=True)
            
            # Start separation
            self.audio_separator.separate(
                self.audio_file.file_path,
                method,
                output_dir
            )
    
    def convert_to_midi(self, quantize: bool) -> None:
        """
        Convert audio stems to MIDI.
        
        Args:
            quantize: Whether to quantize notes to the beat grid
        """
        if self.stems:
            # Create output directory
            output_dir = os.path.join(self.temp_dir, "midi")
            os.makedirs(output_dir, exist_ok=True)
            
            # Start conversion
            self.midi_converter.convert(
                self.stems,
                self.analysis_results,
                output_dir,
                quantize
            )
    
    def export_midi(self, stem: str, destination_path: str) -> None:
        """
        Export a MIDI file.
        
        Args:
            stem: Stem name
            destination_path: Destination path
        """
        if stem in self.midi_files:
            # Get the MIDI file path
            midi_path = self.midi_files[stem]['path']
            
            # Export the MIDI file
            self.midi_exporter.export_midi(midi_path, destination_path)
    
    def export_all_midi(self, destination_dir: str) -> None:
        """
        Export all MIDI files.
        
        Args:
            destination_dir: Destination directory
        """
        if self.midi_files:
            # Create a dictionary of MIDI file paths
            midi_paths = {}
            for name, data in self.midi_files.items():
                midi_paths[name] = data['path']
            
            # Export all MIDI files
            self.midi_exporter.export_all_midis(midi_paths, destination_dir)
    
    def load_midi_file(self, stem: str) -> None:
        """
        Load a MIDI file in the MIDI player.
        
        Args:
            stem: Stem name
        """
        if stem in self.midi_files:
            # Load the MIDI file
            midi_path = self.midi_files[stem]['path']
            self.midi_player.load_file(midi_path)
    
    def get_midi_data(self, stem: str) -> Optional[pretty_midi.PrettyMIDI]:
        """
        Get MIDI data for a stem.
        
        Args:
            stem: Stem name
            
        Returns:
            PrettyMIDI object or None if not found
        """
        if stem in self.midi_files:
            try:
                return pretty_midi.PrettyMIDI(self.midi_files[stem]['path'])
            except Exception:
                return None
        return None
    
    def cleanup(self) -> None:
        """Clean up temporary files."""
        # Clean up audio separator
        self.audio_separator.cleanup()
        
        # Remove temporary directory
        if self.temp_dir and os.path.exists(self.temp_dir):
            try:
                import shutil
                shutil.rmtree(self.temp_dir)
            except Exception:
                pass
    
    @pyqtSlot(dict)
    def _on_separation_finished(self, stems: Dict) -> None:
        """
        Handle separation finished event.
        
        Args:
            stems: Dictionary of separated stems
        """
        # Store stems
        self.stems = stems
        
        # Emit separation finished signal
        self.separationFinished.emit(stems)
    
    @pyqtSlot(dict)
    def _on_analysis_finished(self, results: Dict) -> None:
        """
        Handle analysis finished event.
        
        Args:
            results: Dictionary of analysis results
        """
        # Store results
        self.analysis_results = results
        
        # Emit analysis finished signal
        self.analysisFinished.emit(results)
    
    @pyqtSlot(dict)
    def _on_conversion_finished(self, results: Dict) -> None:
        """
        Handle conversion finished event.
        
        Args:
            results: Dictionary of conversion results
        """
        # Store results
        self.midi_files = results
        
        # Emit conversion finished signal
        self.conversionFinished.emit(results)

