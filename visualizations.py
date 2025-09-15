"""
Module for visualizing audio and MIDI data.
"""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
import librosa
import pretty_midi
from typing import Dict, List, Tuple, Optional, Any
from PyQt6.QtWidgets import QWidget, QVBoxLayout


class WaveformCanvas(FigureCanvasQTAgg):
    """Canvas for displaying audio waveforms."""
    
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        """
        Initialize the waveform canvas.
        
        Args:
            parent: Parent widget
            width: Figure width in inches
            height: Figure height in inches
            dpi: Figure resolution
        """
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        super().__init__(self.fig)
    
    def plot_waveform(self, audio_data: np.ndarray, sample_rate: int, title: str = "Waveform") -> None:
        """
        Plot an audio waveform.
        
        Args:
            audio_data: Audio data as numpy array
            sample_rate: Sample rate of the audio
            title: Plot title
        """
        # Clear the axes
        self.axes.clear()
        
        # Create time axis
        time = np.arange(len(audio_data)) / sample_rate
        
        # Plot waveform
        self.axes.plot(time, audio_data, color='#3498db')
        
        # Set labels and title
        self.axes.set_xlabel('Time (s)')
        self.axes.set_ylabel('Amplitude')
        self.axes.set_title(title)
        
        # Set y-axis limits
        self.axes.set_ylim([-1.1, 1.1])
        
        # Add grid
        self.axes.grid(True, alpha=0.3)
        
        # Adjust layout
        self.fig.tight_layout()
        
        # Draw the canvas
        self.draw()


class SpectrogramCanvas(FigureCanvasQTAgg):
    """Canvas for displaying spectrograms."""
    
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        """
        Initialize the spectrogram canvas.
        
        Args:
            parent: Parent widget
            width: Figure width in inches
            height: Figure height in inches
            dpi: Figure resolution
        """
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        super().__init__(self.fig)
    
    def plot_spectrogram(self, audio_data: np.ndarray, sample_rate: int, 
                         title: str = "Spectrogram", n_fft: int = 2048, 
                         hop_length: int = 512) -> None:
        """
        Plot a spectrogram.
        
        Args:
            audio_data: Audio data as numpy array
            sample_rate: Sample rate of the audio
            title: Plot title
            n_fft: FFT window size
            hop_length: Number of samples between successive frames
        """
        # Clear the axes
        self.axes.clear()
        
        # Compute spectrogram
        S = librosa.stft(audio_data, n_fft=n_fft, hop_length=hop_length)
        
        # Convert to dB scale
        S_db = librosa.amplitude_to_db(np.abs(S), ref=np.max)
        
        # Plot spectrogram
        img = librosa.display.specshow(
            S_db, 
            x_axis='time', 
            y_axis='log', 
            sr=sample_rate, 
            hop_length=hop_length,
            ax=self.axes
        )
        
        # Add colorbar
        self.fig.colorbar(img, ax=self.axes, format='%+2.0f dB')
        
        # Set title
        self.axes.set_title(title)
        
        # Adjust layout
        self.fig.tight_layout()
        
        # Draw the canvas
        self.draw()


class ChromagramCanvas(FigureCanvasQTAgg):
    """Canvas for displaying chromagrams."""
    
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        """
        Initialize the chromagram canvas.
        
        Args:
            parent: Parent widget
            width: Figure width in inches
            height: Figure height in inches
            dpi: Figure resolution
        """
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        super().__init__(self.fig)
    
    def plot_chromagram(self, audio_data: np.ndarray, sample_rate: int, 
                        title: str = "Chromagram") -> None:
        """
        Plot a chromagram.
        
        Args:
            audio_data: Audio data as numpy array
            sample_rate: Sample rate of the audio
            title: Plot title
        """
        # Clear the axes
        self.axes.clear()
        
        # Compute chromagram
        chroma = librosa.feature.chroma_cqt(y=audio_data, sr=sample_rate)
        
        # Plot chromagram
        img = librosa.display.specshow(
            chroma, 
            x_axis='time', 
            y_axis='chroma', 
            sr=sample_rate, 
            ax=self.axes
        )
        
        # Add colorbar
        self.fig.colorbar(img, ax=self.axes)
        
        # Set title
        self.axes.set_title(title)
        
        # Adjust layout
        self.fig.tight_layout()
        
        # Draw the canvas
        self.draw()


class PianoRollCanvas(FigureCanvasQTAgg):
    """Canvas for displaying MIDI piano rolls."""
    
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        """
        Initialize the piano roll canvas.
        
        Args:
            parent: Parent widget
            width: Figure width in inches
            height: Figure height in inches
            dpi: Figure resolution
        """
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        super().__init__(self.fig)
    
    def plot_piano_roll(self, midi_data: pretty_midi.PrettyMIDI, 
                        title: str = "Piano Roll", instrument_idx: int = 0) -> None:
        """
        Plot a MIDI piano roll.
        
        Args:
            midi_data: PrettyMIDI object
            title: Plot title
            instrument_idx: Index of the instrument to plot
        """
        # Clear the axes
        self.axes.clear()
        
        # Check if there are instruments
        if not midi_data.instruments:
            self.axes.text(0.5, 0.5, "No MIDI data", ha='center', va='center')
            self.axes.set_title(title)
            self.fig.tight_layout()
            self.draw()
            return
        
        # Ensure valid instrument index
        if instrument_idx >= len(midi_data.instruments):
            instrument_idx = 0
        
        # Get the instrument
        instrument = midi_data.instruments[instrument_idx]
        
        # Get the piano roll
        piano_roll = instrument.get_piano_roll(fs=100)
        
        # Plot piano roll
        img = self.axes.imshow(
            piano_roll,
            aspect='auto',
            origin='lower',
            interpolation='nearest',
            cmap='Blues'
        )
        
        # Set y-axis ticks to show note names
        yticks = np.arange(0, 128, 12)
        note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        ytick_labels = [f"{note_names[i % 12]}{i // 12}" for i in yticks]
        self.axes.set_yticks(yticks)
        self.axes.set_yticklabels(ytick_labels)
        
        # Set x-axis to show time in seconds
        max_time = piano_roll.shape[1] / 100  # fs=100
        xticks = np.arange(0, piano_roll.shape[1], 100)  # Every second
        xtick_labels = [f"{i/100:.1f}" for i in xticks]
        self.axes.set_xticks(xticks)
        self.axes.set_xticklabels(xtick_labels)
        
        # Set labels and title
        self.axes.set_xlabel('Time (s)')
        self.axes.set_ylabel('Pitch')
        self.axes.set_title(f"{title} - {instrument.name}")
        
        # Add colorbar
        self.fig.colorbar(img, ax=self.axes, label='Velocity')
        
        # Adjust layout
        self.fig.tight_layout()
        
        # Draw the canvas
        self.draw()


class WaveformWidget(QWidget):
    """Widget for displaying audio waveforms."""
    
    def __init__(self, parent=None):
        """
        Initialize the waveform widget.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        
        # Create layout
        layout = QVBoxLayout()
        
        # Create canvas
        self.canvas = WaveformCanvas(self, width=5, height=3)
        
        # Add canvas to layout
        layout.addWidget(self.canvas)
        
        # Set layout
        self.setLayout(layout)
    
    def plot_waveform(self, audio_data: np.ndarray, sample_rate: int, title: str = "Waveform") -> None:
        """
        Plot an audio waveform.
        
        Args:
            audio_data: Audio data as numpy array
            sample_rate: Sample rate of the audio
            title: Plot title
        """
        self.canvas.plot_waveform(audio_data, sample_rate, title)


class SpectrogramWidget(QWidget):
    """Widget for displaying spectrograms."""
    
    def __init__(self, parent=None):
        """
        Initialize the spectrogram widget.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        
        # Create layout
        layout = QVBoxLayout()
        
        # Create canvas
        self.canvas = SpectrogramCanvas(self, width=5, height=3)
        
        # Add canvas to layout
        layout.addWidget(self.canvas)
        
        # Set layout
        self.setLayout(layout)
    
    def plot_spectrogram(self, audio_data: np.ndarray, sample_rate: int, 
                         title: str = "Spectrogram", n_fft: int = 2048, 
                         hop_length: int = 512) -> None:
        """
        Plot a spectrogram.
        
        Args:
            audio_data: Audio data as numpy array
            sample_rate: Sample rate of the audio
            title: Plot title
            n_fft: FFT window size
            hop_length: Number of samples between successive frames
        """
        self.canvas.plot_spectrogram(audio_data, sample_rate, title, n_fft, hop_length)


class ChromagramWidget(QWidget):
    """Widget for displaying chromagrams."""
    
    def __init__(self, parent=None):
        """
        Initialize the chromagram widget.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        
        # Create layout
        layout = QVBoxLayout()
        
        # Create canvas
        self.canvas = ChromagramCanvas(self, width=5, height=3)
        
        # Add canvas to layout
        layout.addWidget(self.canvas)
        
        # Set layout
        self.setLayout(layout)
    
    def plot_chromagram(self, audio_data: np.ndarray, sample_rate: int, 
                        title: str = "Chromagram") -> None:
        """
        Plot a chromagram.
        
        Args:
            audio_data: Audio data as numpy array
            sample_rate: Sample rate of the audio
            title: Plot title
        """
        self.canvas.plot_chromagram(audio_data, sample_rate, title)


class PianoRollWidget(QWidget):
    """Widget for displaying MIDI piano rolls."""
    
    def __init__(self, parent=None):
        """
        Initialize the piano roll widget.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        
        # Create layout
        layout = QVBoxLayout()
        
        # Create canvas
        self.canvas = PianoRollCanvas(self, width=5, height=3)
        
        # Add canvas to layout
        layout.addWidget(self.canvas)
        
        # Set layout
        self.setLayout(layout)
    
    def plot_piano_roll(self, midi_data: pretty_midi.PrettyMIDI, 
                        title: str = "Piano Roll", instrument_idx: int = 0) -> None:
        """
        Plot a MIDI piano roll.
        
        Args:
            midi_data: PrettyMIDI object
            title: Plot title
            instrument_idx: Index of the instrument to plot
        """
        self.canvas.plot_piano_roll(midi_data, title, instrument_idx)

