"""
Main window for the MP3 to MIDI converter application.
"""
import os
import tempfile
from typing import Dict, Optional, Any
import pretty_midi
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QFileDialog,
    QMessageBox, QTabWidget, QSplitter, QLabel, QStatusBar
)
from PyQt6.QtCore import Qt, pyqtSlot, QSettings

from audio_core import AudioFile, load_audio_file
from audio_player import AudioPlayer, MIDIPlayer
from audio_separator import AudioSeparator
from audio_analyzer import AudioAnalyzer
from midi_converter import MIDIConverter
from midi_exporter import MIDIExporter
from visualizations import (
    WaveformWidget, SpectrogramWidget, ChromagramWidget, PianoRollWidget
)
from ui_components import (
    FileDropWidget, AudioPlayerControls, AnalysisResultsWidget,
    SeparationControlsWidget, ConversionControlsWidget, MIDIPlayerWidget
)


class MainWindow(QMainWindow):
    """Main window for the MP3 to MIDI converter application."""
    
    def __init__(self):
        """Initialize the main window."""
        super().__init__()
        
        # Set window properties
        self.setWindowTitle("MP3 to MIDI Converter")
        self.setMinimumSize(800, 600)
        
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
        
        # Create UI
        self._create_ui()
        
        # Connect signals
        self._connect_signals()
        
        # Load settings
        self._load_settings()
    
    def _create_ui(self):
        """Create the user interface."""
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create main layout
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)
        
        # Create top section (file loading and audio player)
        top_layout = QHBoxLayout()
        
        # Create file drop widget
        self.file_drop_widget = FileDropWidget()
        top_layout.addWidget(self.file_drop_widget)
        
        # Create audio player controls
        self.audio_player_controls = AudioPlayerControls()
        top_layout.addWidget(self.audio_player_controls)
        
        # Add top section to main layout
        main_layout.addLayout(top_layout)
        
        # Create middle section (visualizations and controls)
        middle_layout = QHBoxLayout()
        
        # Create tab widget for visualizations
        self.viz_tabs = QTabWidget()
        
        # Create waveform widget
        self.waveform_widget = WaveformWidget()
        self.viz_tabs.addTab(self.waveform_widget, "Waveform")
        
        # Create spectrogram widget
        self.spectrogram_widget = SpectrogramWidget()
        self.viz_tabs.addTab(self.spectrogram_widget, "Spectrogram")
        
        # Create chromagram widget
        self.chromagram_widget = ChromagramWidget()
        self.viz_tabs.addTab(self.chromagram_widget, "Chromagram")
        
        # Create piano roll widget
        self.piano_roll_widget = PianoRollWidget()
        self.viz_tabs.addTab(self.piano_roll_widget, "Piano Roll")
        
        # Add visualization tabs to middle layout
        middle_layout.addWidget(self.viz_tabs, 2)
        
        # Create controls layout
        controls_layout = QVBoxLayout()
        
        # Create analysis results widget
        self.analysis_results_widget = AnalysisResultsWidget()
        controls_layout.addWidget(self.analysis_results_widget)
        
        # Create separation controls widget
        self.separation_controls_widget = SeparationControlsWidget()
        controls_layout.addWidget(self.separation_controls_widget)
        
        # Create conversion controls widget
        self.conversion_controls_widget = ConversionControlsWidget()
        controls_layout.addWidget(self.conversion_controls_widget)
        
        # Add controls to middle layout
        middle_layout.addLayout(controls_layout, 1)
        
        # Add middle section to main layout
        main_layout.addLayout(middle_layout, 1)
        
        # Create bottom section (MIDI player)
        bottom_layout = QVBoxLayout()
        
        # Create MIDI player widget
        self.midi_player_widget = MIDIPlayerWidget()
        bottom_layout.addWidget(self.midi_player_widget)
        
        # Add bottom section to main layout
        main_layout.addLayout(bottom_layout)
        
        # Create status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
    
    def _connect_signals(self):
        """Connect signals to slots."""
        # File drop widget
        self.file_drop_widget.fileDropped.connect(self._on_file_dropped)
        
        # Audio player
        self.audio_player.positionChanged.connect(self._on_audio_position_changed)
        self.audio_player.durationChanged.connect(self._on_audio_duration_changed)
        self.audio_player.stateChanged.connect(self._on_audio_state_changed)
        
        # Audio player controls
        self.audio_player_controls.playClicked.connect(self.audio_player.play)
        self.audio_player_controls.pauseClicked.connect(self.audio_player.pause)
        self.audio_player_controls.stopClicked.connect(self.audio_player.stop)
        self.audio_player_controls.positionChanged.connect(self._on_position_slider_moved)
        self.audio_player_controls.volumeChanged.connect(self.audio_player.set_volume)
        
        # Audio separator
        self.audio_separator.separationStarted.connect(self._on_separation_started)
        self.audio_separator.separationProgress.connect(self._on_separation_progress)
        self.audio_separator.separationFinished.connect(self._on_separation_finished)
        self.audio_separator.separationError.connect(self._on_separation_error)
        
        # Separation controls
        self.separation_controls_widget.separateClicked.connect(self._on_separate_clicked)
        
        # Audio analyzer
        self.audio_analyzer.analysisStarted.connect(self._on_analysis_started)
        self.audio_analyzer.analysisProgress.connect(self._on_analysis_progress)
        self.audio_analyzer.analysisFinished.connect(self._on_analysis_finished)
        self.audio_analyzer.analysisError.connect(self._on_analysis_error)
        
        # MIDI converter
        self.midi_converter.conversionStarted.connect(self._on_conversion_started)
        self.midi_converter.conversionProgress.connect(self._on_conversion_progress)
        self.midi_converter.conversionFinished.connect(self._on_conversion_finished)
        self.midi_converter.conversionError.connect(self._on_conversion_error)
        
        # Conversion controls
        self.conversion_controls_widget.convertClicked.connect(self._on_convert_clicked)
        
        # MIDI player
        self.midi_player.positionChanged.connect(self._on_midi_position_changed)
        self.midi_player.durationChanged.connect(self._on_midi_duration_changed)
        self.midi_player.stateChanged.connect(self._on_midi_state_changed)
        
        # MIDI player widget
        self.midi_player_widget.stemSelected.connect(self._on_midi_stem_selected)
        self.midi_player_widget.playClicked.connect(self.midi_player.play)
        self.midi_player_widget.pauseClicked.connect(self.midi_player.pause)
        self.midi_player_widget.stopClicked.connect(self.midi_player.stop)
        self.midi_player_widget.exportClicked.connect(self._on_export_midi_clicked)
        self.midi_player_widget.exportAllClicked.connect(self._on_export_all_midi_clicked)
        
        # MIDI exporter
        self.midi_exporter.exportStarted.connect(self._on_export_started)
        self.midi_exporter.exportFinished.connect(self._on_export_finished)
        self.midi_exporter.exportError.connect(self._on_export_error)
    
    def _load_settings(self):
        """Load application settings."""
        settings = QSettings("MP3toMIDI", "MP3toMIDI")
        
        # Load window geometry
        geometry = settings.value("geometry")
        if geometry:
            self.restoreGeometry(geometry)
        
        # Load window state
        state = settings.value("windowState")
        if state:
            self.restoreState(state)
    
    def _save_settings(self):
        """Save application settings."""
        settings = QSettings("MP3toMIDI", "MP3toMIDI")
        
        # Save window geometry
        settings.setValue("geometry", self.saveGeometry())
        
        # Save window state
        settings.setValue("windowState", self.saveState())
    
    def closeEvent(self, event):
        """
        Handle close event.
        
        Args:
            event: Close event
        """
        # Save settings
        self._save_settings()
        
        # Clean up
        self._cleanup()
        
        # Accept the event
        event.accept()
    
    def _cleanup(self):
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
    
    @pyqtSlot(str)
    def _on_file_dropped(self, file_path: str):
        """
        Handle file dropped event.
        
        Args:
            file_path: Path to the dropped file
        """
        self._load_audio_file(file_path)
    
    def _load_audio_file(self, file_path: str):
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
            
            # Update UI
            self._update_ui_for_loaded_file()
            
            # Update status
            self.status_bar.showMessage(f"Loaded: {os.path.basename(file_path)}")
            
            # Analyze the audio
            self._analyze_audio()
            
        except Exception as e:
            # Show error message
            QMessageBox.critical(
                self,
                "Error Loading File",
                f"Error loading audio file: {str(e)}"
            )
    
    def _update_ui_for_loaded_file(self):
        """Update UI for loaded file."""
        # Update waveform
        self.waveform_widget.plot_waveform(
            self.audio_file.mono_audio,
            self.audio_file.sample_rate,
            f"Waveform: {self.audio_file.file_name}"
        )
        
        # Update spectrogram
        self.spectrogram_widget.plot_spectrogram(
            self.audio_file.mono_audio,
            self.audio_file.sample_rate,
            f"Spectrogram: {self.audio_file.file_name}"
        )
        
        # Update chromagram
        self.chromagram_widget.plot_chromagram(
            self.audio_file.mono_audio,
            self.audio_file.sample_rate,
            f"Chromagram: {self.audio_file.file_name}"
        )
        
        # Enable controls
        self.separation_controls_widget.set_enabled(True)
    
    def _analyze_audio(self):
        """Analyze the audio file."""
        if self.audio_file:
            # Start analysis
            self.audio_analyzer.analyze(
                self.audio_file.mono_audio,
                self.audio_file.sample_rate
            )
    
    @pyqtSlot(int)
    def _on_audio_position_changed(self, position: int):
        """
        Handle audio position changed event.
        
        Args:
            position: Position in milliseconds
        """
        # Update position display
        self.audio_player_controls.set_position(position, self.audio_player.get_duration())
    
    @pyqtSlot(int)
    def _on_audio_duration_changed(self, duration: int):
        """
        Handle audio duration changed event.
        
        Args:
            duration: Duration in milliseconds
        """
        # Update duration display
        self.audio_player_controls.set_duration(duration)
    
    @pyqtSlot(str)
    def _on_audio_state_changed(self, state: str):
        """
        Handle audio state changed event.
        
        Args:
            state: Player state
        """
        # Update status
        self.status_bar.showMessage(f"Audio: {state}")
    
    @pyqtSlot(int)
    def _on_position_slider_moved(self, position: int):
        """
        Handle position slider moved event.
        
        Args:
            position: Position value
        """
        # Set player position
        self.audio_player.set_position(position)
    
    @pyqtSlot(str)
    def _on_separate_clicked(self, method: str):
        """
        Handle separate clicked event.
        
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
    
    @pyqtSlot()
    def _on_separation_started(self):
        """Handle separation started event."""
        # Update status
        self.status_bar.showMessage("Separation started...")
        
        # Disable controls
        self.separation_controls_widget.set_enabled(False)
    
    @pyqtSlot(int)
    def _on_separation_progress(self, progress: int):
        """
        Handle separation progress event.
        
        Args:
            progress: Progress value
        """
        # Update progress bar
        self.separation_controls_widget.set_progress(progress)
        
        # Update status
        self.status_bar.showMessage(f"Separation progress: {progress}%")
    
    @pyqtSlot(dict)
    def _on_separation_finished(self, stems: Dict):
        """
        Handle separation finished event.
        
        Args:
            stems: Dictionary of separated stems
        """
        # Store stems
        self.stems = stems
        
        # Update status
        self.status_bar.showMessage("Separation finished")
        
        # Enable controls
        self.separation_controls_widget.set_enabled(True)
        self.conversion_controls_widget.set_enabled(True)
    
    @pyqtSlot(str)
    def _on_separation_error(self, error: str):
        """
        Handle separation error event.
        
        Args:
            error: Error message
        """
        # Show error message
        QMessageBox.critical(
            self,
            "Separation Error",
            f"Error during separation: {error}"
        )
        
        # Update status
        self.status_bar.showMessage("Separation failed")
        
        # Enable controls
        self.separation_controls_widget.set_enabled(True)
    
    @pyqtSlot()
    def _on_analysis_started(self):
        """Handle analysis started event."""
        # Update status
        self.status_bar.showMessage("Analysis started...")
    
    @pyqtSlot(int)
    def _on_analysis_progress(self, progress: int):
        """
        Handle analysis progress event.
        
        Args:
            progress: Progress value
        """
        # Update status
        self.status_bar.showMessage(f"Analysis progress: {progress}%")
    
    @pyqtSlot(dict)
    def _on_analysis_finished(self, results: Dict):
        """
        Handle analysis finished event.
        
        Args:
            results: Dictionary of analysis results
        """
        # Store results
        self.analysis_results = results
        
        # Update UI
        self.analysis_results_widget.set_results(results)
        
        # Update status
        self.status_bar.showMessage("Analysis finished")
    
    @pyqtSlot(str)
    def _on_analysis_error(self, error: str):
        """
        Handle analysis error event.
        
        Args:
            error: Error message
        """
        # Show error message
        QMessageBox.critical(
            self,
            "Analysis Error",
            f"Error during analysis: {error}"
        )
        
        # Update status
        self.status_bar.showMessage("Analysis failed")
    
    @pyqtSlot(bool)
    def _on_convert_clicked(self, quantize: bool):
        """
        Handle convert clicked event.
        
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
    
    @pyqtSlot()
    def _on_conversion_started(self):
        """Handle conversion started event."""
        # Update status
        self.status_bar.showMessage("Conversion started...")
        
        # Disable controls
        self.conversion_controls_widget.set_enabled(False)
    
    @pyqtSlot(int)
    def _on_conversion_progress(self, progress: int):
        """
        Handle conversion progress event.
        
        Args:
            progress: Progress value
        """
        # Update progress bar
        self.conversion_controls_widget.set_progress(progress)
        
        # Update status
        self.status_bar.showMessage(f"Conversion progress: {progress}%")
    
    @pyqtSlot(dict)
    def _on_conversion_finished(self, results: Dict):
        """
        Handle conversion finished event.
        
        Args:
            results: Dictionary of conversion results
        """
        # Store results
        self.midi_files = results
        
        # Update status
        self.status_bar.showMessage("Conversion finished")
        
        # Enable controls
        self.conversion_controls_widget.set_enabled(True)
        self.midi_player_widget.set_enabled(True)
        
        # Load the combined MIDI file
        if 'combined' in results:
            midi_path = results['combined']['path']
            self.midi_player.load_file(midi_path)
            
            # Load MIDI data for visualization
            try:
                midi_data = pretty_midi.PrettyMIDI(midi_path)
                self.piano_roll_widget.plot_piano_roll(
                    midi_data,
                    "Combined MIDI"
                )
            except Exception as e:
                print(f"Error loading MIDI for visualization: {str(e)}")
    
    @pyqtSlot(str)
    def _on_conversion_error(self, error: str):
        """
        Handle conversion error event.
        
        Args:
            error: Error message
        """
        # Show error message
        QMessageBox.critical(
            self,
            "Conversion Error",
            f"Error during conversion: {error}"
        )
        
        # Update status
        self.status_bar.showMessage("Conversion failed")
        
        # Enable controls
        self.conversion_controls_widget.set_enabled(True)
    
    @pyqtSlot(int)
    def _on_midi_position_changed(self, position: int):
        """
        Handle MIDI position changed event.
        
        Args:
            position: Position in milliseconds
        """
        # Update position display
        self.midi_player_widget.set_position(position, self.midi_player.get_duration())
    
    @pyqtSlot(int)
    def _on_midi_duration_changed(self, duration: int):
        """
        Handle MIDI duration changed event.
        
        Args:
            duration: Duration in milliseconds
        """
        # Update duration display
        self.midi_player_widget.set_duration(duration)
    
    @pyqtSlot(str)
    def _on_midi_state_changed(self, state: str):
        """
        Handle MIDI state changed event.
        
        Args:
            state: Player state
        """
        # Update status
        self.status_bar.showMessage(f"MIDI: {state}")
    
    @pyqtSlot(str)
    def _on_midi_stem_selected(self, stem: str):
        """
        Handle MIDI stem selected event.
        
        Args:
            stem: Stem name
        """
        if stem in self.midi_files:
            # Load the MIDI file
            midi_path = self.midi_files[stem]['path']
            self.midi_player.load_file(midi_path)
            
            # Load MIDI data for visualization
            try:
                midi_data = pretty_midi.PrettyMIDI(midi_path)
                self.piano_roll_widget.plot_piano_roll(
                    midi_data,
                    f"{stem.capitalize()} MIDI"
                )
            except Exception as e:
                print(f"Error loading MIDI for visualization: {str(e)}")
    
    @pyqtSlot(str)
    def _on_export_midi_clicked(self, stem: str):
        """
        Handle export MIDI clicked event.
        
        Args:
            stem: Stem name
        """
        if stem in self.midi_files:
            # Get the MIDI file path
            midi_path = self.midi_files[stem]['path']
            
            # Show save dialog
            file_dialog = QFileDialog()
            file_dialog.setAcceptMode(QFileDialog.AcceptMode.AcceptSave)
            file_dialog.setNameFilter("MIDI Files (*.mid)")
            file_dialog.setDefaultSuffix("mid")
            file_dialog.selectFile(f"{stem}.mid")
            
            if file_dialog.exec():
                # Get the selected file path
                destination_path = file_dialog.selectedFiles()[0]
                
                # Export the MIDI file
                self.midi_exporter.export_midi(midi_path, destination_path)
    
    @pyqtSlot()
    def _on_export_all_midi_clicked(self):
        """Handle export all MIDI clicked event."""
        if self.midi_files:
            # Show directory dialog
            directory = QFileDialog.getExistingDirectory(
                self,
                "Select Directory for MIDI Files"
            )
            
            if directory:
                # Create a dictionary of MIDI file paths
                midi_paths = {}
                for name, data in self.midi_files.items():
                    midi_paths[name] = data['path']
                
                # Export all MIDI files
                self.midi_exporter.export_all_midis(midi_paths, directory)
    
    @pyqtSlot(str)
    def _on_export_started(self, midi_name: str):
        """
        Handle export started event.
        
        Args:
            midi_name: MIDI file name
        """
        # Update status
        self.status_bar.showMessage(f"Exporting {midi_name}...")
    
    @pyqtSlot(str, str)
    def _on_export_finished(self, midi_name: str, destination_path: str):
        """
        Handle export finished event.
        
        Args:
            midi_name: MIDI file name
            destination_path: Destination path
        """
        # Update status
        self.status_bar.showMessage(f"Exported {midi_name} to {destination_path}")
        
        # Show success message
        QMessageBox.information(
            self,
            "Export Successful",
            f"MIDI file exported to:\n{destination_path}"
        )
    
    @pyqtSlot(str, str)
    def _on_export_error(self, midi_name: str, error: str):
        """
        Handle export error event.
        
        Args:
            midi_name: MIDI file name
            error: Error message
        """
        # Show error message
        QMessageBox.critical(
            self,
            "Export Error",
            f"Error exporting {midi_name}: {error}"
        )
        
        # Update status
        self.status_bar.showMessage(f"Export failed: {midi_name}")

