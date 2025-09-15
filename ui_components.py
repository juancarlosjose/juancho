"""
UI components for the MP3 to MIDI converter application.
"""
from PyQt6.QtWidgets import (
    QWidget, QLabel, QPushButton, QSlider, QComboBox, QProgressBar,
    QHBoxLayout, QVBoxLayout, QFileDialog, QGroupBox, QTabWidget,
    QCheckBox, QSpinBox, QDoubleSpinBox, QMessageBox, QSplitter,
    QFrame, QScrollArea, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QIcon, QDragEnterEvent, QDropEvent


class FileDropWidget(QWidget):
    """Widget that accepts file drops."""
    
    # Define signals
    fileDropped = pyqtSignal(str)  # File path
    
    def __init__(self, parent=None):
        """
        Initialize the file drop widget.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        
        # Enable drag and drop
        self.setAcceptDrops(True)
        
        # Create layout
        layout = QVBoxLayout()
        
        # Create label
        self.label = QLabel("Drop MP3 file here")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setStyleSheet("""
            QLabel {
                border: 2px dashed #aaa;
                border-radius: 5px;
                padding: 20px;
                background-color: #f8f8f8;
                font-size: 16px;
            }
        """)
        
        # Add label to layout
        layout.addWidget(self.label)
        
        # Set layout
        self.setLayout(layout)
    
    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        """
        Handle drag enter event.
        
        Args:
            event: Drag enter event
        """
        # Check if the event has URLs
        if event.mimeData().hasUrls():
            # Get the first URL
            url = event.mimeData().urls()[0]
            
            # Check if it's a local file
            if url.isLocalFile():
                # Get the file path
                file_path = url.toLocalFile()
                
                # Check if it's an MP3 file
                if file_path.lower().endswith('.mp3'):
                    # Accept the event
                    event.acceptProposedAction()
                    
                    # Change label style
                    self.label.setStyleSheet("""
                        QLabel {
                            border: 2px dashed #3498db;
                            border-radius: 5px;
                            padding: 20px;
                            background-color: #e8f4fc;
                            font-size: 16px;
                        }
                    """)
    
    def dragLeaveEvent(self, event) -> None:
        """
        Handle drag leave event.
        
        Args:
            event: Drag leave event
        """
        # Reset label style
        self.label.setStyleSheet("""
            QLabel {
                border: 2px dashed #aaa;
                border-radius: 5px;
                padding: 20px;
                background-color: #f8f8f8;
                font-size: 16px;
            }
        """)
    
    def dropEvent(self, event: QDropEvent) -> None:
        """
        Handle drop event.
        
        Args:
            event: Drop event
        """
        # Check if the event has URLs
        if event.mimeData().hasUrls():
            # Get the first URL
            url = event.mimeData().urls()[0]
            
            # Check if it's a local file
            if url.isLocalFile():
                # Get the file path
                file_path = url.toLocalFile()
                
                # Check if it's an MP3 file
                if file_path.lower().endswith('.mp3'):
                    # Accept the event
                    event.acceptProposedAction()
                    
                    # Reset label style
                    self.label.setStyleSheet("""
                        QLabel {
                            border: 2px dashed #aaa;
                            border-radius: 5px;
                            padding: 20px;
                            background-color: #f8f8f8;
                            font-size: 16px;
                        }
                    """)
                    
                    # Emit file dropped signal
                    self.fileDropped.emit(file_path)


class AudioPlayerControls(QWidget):
    """Widget for audio player controls."""
    
    # Define signals
    playClicked = pyqtSignal()
    pauseClicked = pyqtSignal()
    stopClicked = pyqtSignal()
    positionChanged = pyqtSignal(int)  # Position in milliseconds
    volumeChanged = pyqtSignal(float)  # Volume (0.0 to 1.0)
    
    def __init__(self, parent=None):
        """
        Initialize the audio player controls.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        
        # Create layout
        layout = QVBoxLayout()
        
        # Create transport controls
        transport_layout = QHBoxLayout()
        
        # Create play button
        self.play_button = QPushButton("Play")
        self.play_button.clicked.connect(self.playClicked.emit)
        transport_layout.addWidget(self.play_button)
        
        # Create pause button
        self.pause_button = QPushButton("Pause")
        self.pause_button.clicked.connect(self.pauseClicked.emit)
        transport_layout.addWidget(self.pause_button)
        
        # Create stop button
        self.stop_button = QPushButton("Stop")
        self.stop_button.clicked.connect(self.stopClicked.emit)
        transport_layout.addWidget(self.stop_button)
        
        # Add transport controls to layout
        layout.addLayout(transport_layout)
        
        # Create position slider
        position_layout = QHBoxLayout()
        
        # Create position label
        self.position_label = QLabel("0:00")
        position_layout.addWidget(self.position_label)
        
        # Create position slider
        self.position_slider = QSlider(Qt.Orientation.Horizontal)
        self.position_slider.setRange(0, 1000)
        self.position_slider.sliderMoved.connect(self._on_position_slider_moved)
        position_layout.addWidget(self.position_slider)
        
        # Create duration label
        self.duration_label = QLabel("0:00")
        position_layout.addWidget(self.duration_label)
        
        # Add position controls to layout
        layout.addLayout(position_layout)
        
        # Create volume controls
        volume_layout = QHBoxLayout()
        
        # Create volume label
        volume_layout.addWidget(QLabel("Volume:"))
        
        # Create volume slider
        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(70)
        self.volume_slider.valueChanged.connect(self._on_volume_slider_changed)
        volume_layout.addWidget(self.volume_slider)
        
        # Add volume controls to layout
        layout.addLayout(volume_layout)
        
        # Set layout
        self.setLayout(layout)
    
    def _on_position_slider_moved(self, position: int) -> None:
        """
        Handle position slider moved event.
        
        Args:
            position: Position value
        """
        self.positionChanged.emit(position)
    
    def _on_volume_slider_changed(self, volume: int) -> None:
        """
        Handle volume slider changed event.
        
        Args:
            volume: Volume value (0 to 100)
        """
        # Convert to float (0.0 to 1.0)
        volume_float = volume / 100.0
        self.volumeChanged.emit(volume_float)
    
    def set_position(self, position: int, duration: int) -> None:
        """
        Set the position display.
        
        Args:
            position: Position in milliseconds
            duration: Duration in milliseconds
        """
        # Update position slider
        self.position_slider.setValue(position)
        
        # Update position label
        position_str = self._format_time(position)
        self.position_label.setText(position_str)
        
        # Update duration label
        duration_str = self._format_time(duration)
        self.duration_label.setText(duration_str)
    
    def set_duration(self, duration: int) -> None:
        """
        Set the duration display.
        
        Args:
            duration: Duration in milliseconds
        """
        # Update position slider range
        self.position_slider.setRange(0, duration)
        
        # Update duration label
        duration_str = self._format_time(duration)
        self.duration_label.setText(duration_str)
    
    def _format_time(self, time_ms: int) -> str:
        """
        Format time in milliseconds as MM:SS.
        
        Args:
            time_ms: Time in milliseconds
            
        Returns:
            Formatted time string
        """
        # Convert to seconds
        time_s = time_ms / 1000
        
        # Calculate minutes and seconds
        minutes = int(time_s // 60)
        seconds = int(time_s % 60)
        
        # Format as MM:SS
        return f"{minutes}:{seconds:02d}"


class AnalysisResultsWidget(QWidget):
    """Widget for displaying analysis results."""
    
    def __init__(self, parent=None):
        """
        Initialize the analysis results widget.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        
        # Create layout
        layout = QVBoxLayout()
        
        # Create group box
        group_box = QGroupBox("Analysis Results")
        group_layout = QVBoxLayout()
        
        # Create tempo label
        tempo_layout = QHBoxLayout()
        tempo_layout.addWidget(QLabel("Tempo:"))
        self.tempo_label = QLabel("-- BPM")
        tempo_layout.addWidget(self.tempo_label)
        tempo_layout.addStretch()
        group_layout.addLayout(tempo_layout)
        
        # Create key label
        key_layout = QHBoxLayout()
        key_layout.addWidget(QLabel("Key:"))
        self.key_label = QLabel("--")
        key_layout.addWidget(self.key_label)
        key_layout.addStretch()
        group_layout.addLayout(key_layout)
        
        # Set group box layout
        group_box.setLayout(group_layout)
        
        # Add group box to layout
        layout.addWidget(group_box)
        
        # Add stretch
        layout.addStretch()
        
        # Set layout
        self.setLayout(layout)
    
    def set_results(self, results: dict) -> None:
        """
        Set the analysis results.
        
        Args:
            results: Dictionary of analysis results
        """
        # Update tempo label
        if 'tempo' in results:
            tempo = results['tempo'].get('bpm', 0)
            confidence = results['tempo'].get('confidence', 0)
            self.tempo_label.setText(f"{tempo:.1f} BPM (confidence: {confidence:.2f})")
        
        # Update key label
        if 'key' in results:
            key = results['key'].get('key', '--')
            confidence = results['key'].get('confidence', 0)
            self.key_label.setText(f"{key} (confidence: {confidence:.2f})")


class SeparationControlsWidget(QWidget):
    """Widget for separation controls."""
    
    # Define signals
    separateClicked = pyqtSignal(str)  # Separation method
    
    def __init__(self, parent=None):
        """
        Initialize the separation controls widget.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        
        # Create layout
        layout = QVBoxLayout()
        
        # Create group box
        group_box = QGroupBox("Separation Controls")
        group_layout = QVBoxLayout()
        
        # Create method selection
        method_layout = QHBoxLayout()
        method_layout.addWidget(QLabel("Method:"))
        self.method_combo = QComboBox()
        self.method_combo.addItem("Demucs", "demucs")
        self.method_combo.addItem("Spleeter", "spleeter")
        method_layout.addWidget(self.method_combo)
        group_layout.addLayout(method_layout)
        
        # Create separate button
        self.separate_button = QPushButton("Separate Audio")
        self.separate_button.clicked.connect(self._on_separate_clicked)
        group_layout.addWidget(self.separate_button)
        
        # Create progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFormat("%p%")
        group_layout.addWidget(self.progress_bar)
        
        # Set group box layout
        group_box.setLayout(group_layout)
        
        # Add group box to layout
        layout.addWidget(group_box)
        
        # Add stretch
        layout.addStretch()
        
        # Set layout
        self.setLayout(layout)
    
    def _on_separate_clicked(self) -> None:
        """Handle separate button clicked event."""
        # Get selected method
        method = self.method_combo.currentData()
        
        # Emit separate clicked signal
        self.separateClicked.emit(method)
    
    def set_progress(self, progress: int) -> None:
        """
        Set the progress bar value.
        
        Args:
            progress: Progress value (0 to 100)
        """
        self.progress_bar.setValue(progress)
    
    def set_enabled(self, enabled: bool) -> None:
        """
        Set whether the controls are enabled.
        
        Args:
            enabled: Whether the controls are enabled
        """
        self.method_combo.setEnabled(enabled)
        self.separate_button.setEnabled(enabled)


class ConversionControlsWidget(QWidget):
    """Widget for conversion controls."""
    
    # Define signals
    convertClicked = pyqtSignal(bool)  # Quantize flag
    
    def __init__(self, parent=None):
        """
        Initialize the conversion controls widget.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        
        # Create layout
        layout = QVBoxLayout()
        
        # Create group box
        group_box = QGroupBox("Conversion Controls")
        group_layout = QVBoxLayout()
        
        # Create quantize checkbox
        self.quantize_check = QCheckBox("Quantize to beats")
        self.quantize_check.setChecked(True)
        group_layout.addWidget(self.quantize_check)
        
        # Create convert button
        self.convert_button = QPushButton("Convert to MIDI")
        self.convert_button.clicked.connect(self._on_convert_clicked)
        group_layout.addWidget(self.convert_button)
        
        # Create progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFormat("%p%")
        group_layout.addWidget(self.progress_bar)
        
        # Set group box layout
        group_box.setLayout(group_layout)
        
        # Add group box to layout
        layout.addWidget(group_box)
        
        # Add stretch
        layout.addStretch()
        
        # Set layout
        self.setLayout(layout)
    
    def _on_convert_clicked(self) -> None:
        """Handle convert button clicked event."""
        # Get quantize flag
        quantize = self.quantize_check.isChecked()
        
        # Emit convert clicked signal
        self.convertClicked.emit(quantize)
    
    def set_progress(self, progress: int) -> None:
        """
        Set the progress bar value.
        
        Args:
            progress: Progress value (0 to 100)
        """
        self.progress_bar.setValue(progress)
    
    def set_enabled(self, enabled: bool) -> None:
        """
        Set whether the controls are enabled.
        
        Args:
            enabled: Whether the controls are enabled
        """
        self.quantize_check.setEnabled(enabled)
        self.convert_button.setEnabled(enabled)


class MIDIPlayerWidget(QWidget):
    """Widget for MIDI player."""
    
    # Define signals
    stemSelected = pyqtSignal(str)  # Stem name
    playClicked = pyqtSignal()
    pauseClicked = pyqtSignal()
    stopClicked = pyqtSignal()
    exportClicked = pyqtSignal(str)  # Stem name
    exportAllClicked = pyqtSignal()
    
    def __init__(self, parent=None):
        """
        Initialize the MIDI player widget.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        
        # Create layout
        layout = QVBoxLayout()
        
        # Create stem selection
        stem_layout = QHBoxLayout()
        stem_layout.addWidget(QLabel("Stem:"))
        self.stem_combo = QComboBox()
        self.stem_combo.addItem("Combined", "combined")
        self.stem_combo.addItem("Vocals", "vocals")
        self.stem_combo.addItem("Drums", "drums")
        self.stem_combo.addItem("Bass", "bass")
        self.stem_combo.addItem("Other", "other")
        self.stem_combo.currentIndexChanged.connect(self._on_stem_selected)
        stem_layout.addWidget(self.stem_combo)
        layout.addLayout(stem_layout)
        
        # Create player controls
        self.player_controls = AudioPlayerControls()
        self.player_controls.playClicked.connect(self.playClicked.emit)
        self.player_controls.pauseClicked.connect(self.pauseClicked.emit)
        self.player_controls.stopClicked.connect(self.stopClicked.emit)
        layout.addWidget(self.player_controls)
        
        # Create export controls
        export_layout = QHBoxLayout()
        
        # Create export button
        self.export_button = QPushButton("Export Selected")
        self.export_button.clicked.connect(self._on_export_clicked)
        export_layout.addWidget(self.export_button)
        
        # Create export all button
        self.export_all_button = QPushButton("Export All")
        self.export_all_button.clicked.connect(self.exportAllClicked.emit)
        export_layout.addWidget(self.export_all_button)
        
        # Add export controls to layout
        layout.addLayout(export_layout)
        
        # Set layout
        self.setLayout(layout)
    
    def _on_stem_selected(self, index: int) -> None:
        """
        Handle stem selected event.
        
        Args:
            index: Selected index
        """
        # Get selected stem
        stem = self.stem_combo.currentData()
        
        # Emit stem selected signal
        self.stemSelected.emit(stem)
    
    def _on_export_clicked(self) -> None:
        """Handle export button clicked event."""
        # Get selected stem
        stem = self.stem_combo.currentData()
        
        # Emit export clicked signal
        self.exportClicked.emit(stem)
    
    def set_position(self, position: int, duration: int) -> None:
        """
        Set the position display.
        
        Args:
            position: Position in milliseconds
            duration: Duration in milliseconds
        """
        self.player_controls.set_position(position, duration)
    
    def set_duration(self, duration: int) -> None:
        """
        Set the duration display.
        
        Args:
            duration: Duration in milliseconds
        """
        self.player_controls.set_duration(duration)
    
    def set_enabled(self, enabled: bool) -> None:
        """
        Set whether the controls are enabled.
        
        Args:
            enabled: Whether the controls are enabled
        """
        self.stem_combo.setEnabled(enabled)
        self.player_controls.setEnabled(enabled)
        self.export_button.setEnabled(enabled)
        self.export_all_button.setEnabled(enabled)

