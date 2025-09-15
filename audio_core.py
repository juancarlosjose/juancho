"""
Core audio functionality for loading and processing MP3 files.
"""
import os
import librosa
import numpy as np
from pydub import AudioSegment
from typing import Tuple, Dict, Any, Optional


class AudioFile:
    """Class representing an audio file with processing capabilities."""
    
    def __init__(self, file_path: str):
        """
        Initialize an AudioFile object.
        
        Args:
            file_path: Path to the audio file
        """
        self.file_path = file_path
        self.file_name = os.path.basename(file_path)
        self.audio_data = None
        self.sample_rate = None
        self.duration = None
        self.channels = None
        self.metadata = {}
        
        # Load the audio file
        self._load_audio()
    
    def _load_audio(self) -> None:
        """Load the audio file and extract basic information."""
        try:
            # Load audio file with librosa
            self.audio_data, self.sample_rate = librosa.load(
                self.file_path, sr=None, mono=False
            )
            
            # Convert to mono if needed for processing
            if self.audio_data.ndim > 1:
                self.channels = self.audio_data.shape[0]
                self.mono_audio = librosa.to_mono(self.audio_data)
            else:
                self.channels = 1
                self.mono_audio = self.audio_data
            
            # Calculate duration
            self.duration = librosa.get_duration(y=self.mono_audio, sr=self.sample_rate)
            
            # Extract basic metadata
            self._extract_metadata()
            
        except Exception as e:
            raise RuntimeError(f"Error loading audio file: {str(e)}")
    
    def _extract_metadata(self) -> None:
        """Extract basic metadata from the audio file."""
        # Get basic audio properties
        self.metadata = {
            "file_name": self.file_name,
            "duration": self.duration,
            "sample_rate": self.sample_rate,
            "channels": self.channels,
            "file_size": os.path.getsize(self.file_path),
        }
    
    def get_waveform_data(self, max_points: int = 1000) -> np.ndarray:
        """
        Get waveform data for visualization.
        
        Args:
            max_points: Maximum number of points to return
            
        Returns:
            Numpy array of waveform data
        """
        # If we have more samples than max_points, downsample
        if len(self.mono_audio) > max_points:
            # Simple downsampling by taking every nth sample
            n = len(self.mono_audio) // max_points
            return self.mono_audio[::n][:max_points]
        return self.mono_audio
    
    def get_spectrogram(self, n_fft: int = 2048, hop_length: int = 512) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Compute the spectrogram of the audio.
        
        Args:
            n_fft: FFT window size
            hop_length: Number of samples between successive frames
            
        Returns:
            Tuple of (spectrogram, frequencies, times)
        """
        # Compute spectrogram
        S = librosa.stft(self.mono_audio, n_fft=n_fft, hop_length=hop_length)
        
        # Convert to dB scale
        S_db = librosa.amplitude_to_db(np.abs(S), ref=np.max)
        
        # Get frequency and time axes
        freqs = librosa.fft_frequencies(sr=self.sample_rate, n_fft=n_fft)
        times = librosa.times_like(S, sr=self.sample_rate, hop_length=hop_length)
        
        return S_db, freqs, times
    
    def get_audio_segment(self, start_time: float = 0, end_time: Optional[float] = None) -> np.ndarray:
        """
        Get a segment of the audio data.
        
        Args:
            start_time: Start time in seconds
            end_time: End time in seconds (None for end of file)
            
        Returns:
            Audio segment as numpy array
        """
        if end_time is None:
            end_time = self.duration
            
        start_sample = int(start_time * self.sample_rate)
        end_sample = int(end_time * self.sample_rate)
        
        return self.mono_audio[start_sample:end_sample]
    
    def export_as_wav(self, output_path: str) -> str:
        """
        Export the audio file as WAV.
        
        Args:
            output_path: Path to save the WAV file
            
        Returns:
            Path to the exported WAV file
        """
        # Load with pydub for easy export
        audio = AudioSegment.from_file(self.file_path)
        wav_path = output_path
        audio.export(wav_path, format="wav")
        return wav_path


def load_audio_file(file_path: str) -> AudioFile:
    """
    Load an audio file and return an AudioFile object.
    
    Args:
        file_path: Path to the audio file
        
    Returns:
        AudioFile object
    """
    return AudioFile(file_path)

