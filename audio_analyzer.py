"""
Module for analyzing audio to detect tempo, key, and other musical features.
"""
import numpy as np
import librosa
from typing import Dict, List, Tuple, Optional, Any
from PyQt6.QtCore import QObject, pyqtSignal, QThread


# Define key names
MAJOR_KEYS = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
MINOR_KEYS = ['Cm', 'C#m', 'Dm', 'D#m', 'Em', 'Fm', 'F#m', 'Gm', 'G#m', 'Am', 'A#m', 'Bm']


class AnalysisWorker(QThread):
    """Worker thread for audio analysis to prevent UI freezing."""
    
    # Define signals
    progress = pyqtSignal(int)  # Progress percentage
    finished = pyqtSignal(dict)  # Analysis results
    error = pyqtSignal(str)     # Error message
    
    def __init__(self, audio_data: np.ndarray, sample_rate: int):
        """
        Initialize the analysis worker.
        
        Args:
            audio_data: Audio data as numpy array
            sample_rate: Sample rate of the audio
        """
        super().__init__()
        self.audio_data = audio_data
        self.sample_rate = sample_rate
        self.results = {}
    
    def run(self):
        """Run the analysis process."""
        try:
            # Detect tempo
            self.progress.emit(10)
            tempo = self._detect_tempo()
            self.results['tempo'] = tempo
            
            # Detect key
            self.progress.emit(40)
            key = self._detect_key()
            self.results['key'] = key
            
            # Detect beats
            self.progress.emit(70)
            beats = self._detect_beats()
            self.results['beats'] = beats
            
            # Detect onsets
            self.progress.emit(85)
            onsets = self._detect_onsets()
            self.results['onsets'] = onsets
            
            self.progress.emit(100)
            self.finished.emit(self.results)
            
        except Exception as e:
            self.error.emit(str(e))
    
    def _detect_tempo(self) -> Dict[str, Any]:
        """
        Detect the tempo (BPM) of the audio.
        
        Returns:
            Dictionary with tempo information
        """
        # Compute onset envelope
        onset_env = librosa.onset.onset_strength(
            y=self.audio_data, 
            sr=self.sample_rate
        )
        
        # Estimate tempo
        tempo, _ = librosa.beat.beat_track(
            onset_envelope=onset_env, 
            sr=self.sample_rate
        )
        
        # Get tempo confidence
        # This is a simplified approach - in a real app, you might want
        # a more sophisticated confidence measure
        tempo_distribution = librosa.beat.tempo(
            onset_envelope=onset_env, 
            sr=self.sample_rate,
            aggregate=None
        )
        max_weight = np.max(tempo_distribution)
        total_weight = np.sum(tempo_distribution)
        confidence = max_weight / total_weight if total_weight > 0 else 0
        
        return {
            'bpm': float(tempo),
            'confidence': float(confidence)
        }
    
    def _detect_key(self) -> Dict[str, Any]:
        """
        Detect the musical key of the audio.
        
        Returns:
            Dictionary with key information
        """
        # Compute chromagram
        chroma = librosa.feature.chroma_cqt(
            y=self.audio_data, 
            sr=self.sample_rate
        )
        
        # Compute key profile correlation
        # Krumhansl-Schmuckler key-finding algorithm
        major_profile = np.array([6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88])
        minor_profile = np.array([6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17])
        
        # Normalize profiles
        major_profile = major_profile / major_profile.sum()
        minor_profile = minor_profile / minor_profile.sum()
        
        # Calculate the mean chroma vector
        chroma_mean = np.mean(chroma, axis=1)
        
        # Normalize the mean chroma vector
        if np.sum(chroma_mean) > 0:
            chroma_mean = chroma_mean / np.sum(chroma_mean)
        
        # Calculate correlation for all possible keys
        major_correlations = np.zeros(12)
        minor_correlations = np.zeros(12)
        
        for i in range(12):
            # Shift profiles to match each key
            shifted_major = np.roll(major_profile, i)
            shifted_minor = np.roll(minor_profile, i)
            
            # Calculate correlation
            major_correlations[i] = np.corrcoef(chroma_mean, shifted_major)[0, 1]
            minor_correlations[i] = np.corrcoef(chroma_mean, shifted_minor)[0, 1]
        
        # Find the key with the highest correlation
        max_major_idx = np.argmax(major_correlations)
        max_minor_idx = np.argmax(minor_correlations)
        
        # Determine if the key is major or minor
        if major_correlations[max_major_idx] > minor_correlations[max_minor_idx]:
            key_idx = max_major_idx
            key_name = MAJOR_KEYS[key_idx]
            is_major = True
            confidence = float(major_correlations[max_major_idx])
        else:
            key_idx = max_minor_idx
            key_name = MINOR_KEYS[key_idx]
            is_major = False
            confidence = float(minor_correlations[max_minor_idx])
        
        return {
            'key': key_name,
            'is_major': is_major,
            'confidence': confidence
        }
    
    def _detect_beats(self) -> Dict[str, Any]:
        """
        Detect the beats in the audio.
        
        Returns:
            Dictionary with beat information
        """
        # Compute onset envelope
        onset_env = librosa.onset.onset_strength(
            y=self.audio_data, 
            sr=self.sample_rate
        )
        
        # Detect beats
        tempo, beat_frames = librosa.beat.beat_track(
            onset_envelope=onset_env, 
            sr=self.sample_rate
        )
        
        # Convert beat frames to time
        beat_times = librosa.frames_to_time(beat_frames, sr=self.sample_rate)
        
        return {
            'beat_times': beat_times.tolist(),
            'beat_frames': beat_frames.tolist(),
            'tempo': float(tempo)
        }
    
    def _detect_onsets(self) -> Dict[str, Any]:
        """
        Detect note onsets in the audio.
        
        Returns:
            Dictionary with onset information
        """
        # Compute onset envelope
        onset_env = librosa.onset.onset_strength(
            y=self.audio_data, 
            sr=self.sample_rate
        )
        
        # Detect onsets
        onset_frames = librosa.onset.onset_detect(
            onset_envelope=onset_env, 
            sr=self.sample_rate
        )
        
        # Convert onset frames to time
        onset_times = librosa.frames_to_time(onset_frames, sr=self.sample_rate)
        
        # Compute onset strengths
        onset_strengths = onset_env[onset_frames] if len(onset_frames) > 0 else []
        
        return {
            'onset_times': onset_times.tolist(),
            'onset_frames': onset_frames.tolist(),
            'onset_strengths': onset_strengths.tolist() if isinstance(onset_strengths, np.ndarray) else onset_strengths
        }


class AudioAnalyzer(QObject):
    """Class for analyzing audio to detect musical features."""
    
    # Define signals
    analysisStarted = pyqtSignal()
    analysisProgress = pyqtSignal(int)
    analysisFinished = pyqtSignal(dict)
    analysisError = pyqtSignal(str)
    
    def __init__(self):
        """Initialize the audio analyzer."""
        super().__init__()
        self.worker = None
        self.results = {}
    
    def analyze(self, audio_data: np.ndarray, sample_rate: int) -> None:
        """
        Analyze audio data to detect musical features.
        
        Args:
            audio_data: Audio data as numpy array
            sample_rate: Sample rate of the audio
        """
        # Create and start worker thread
        self.worker = AnalysisWorker(audio_data, sample_rate)
        self.worker.progress.connect(self.analysisProgress.emit)
        self.worker.finished.connect(self._on_analysis_finished)
        self.worker.error.connect(self.analysisError.emit)
        
        # Start analysis
        self.analysisStarted.emit()
        self.worker.start()
    
    def _on_analysis_finished(self, results: Dict) -> None:
        """
        Handle analysis finished signal.
        
        Args:
            results: Dictionary of analysis results
        """
        self.results = results
        self.analysisFinished.emit(results)
    
    def get_results(self) -> Dict:
        """
        Get analysis results.
        
        Returns:
            Dictionary of analysis results
        """
        return self.results
    
    def get_tempo(self) -> Optional[float]:
        """
        Get the detected tempo.
        
        Returns:
            Tempo in BPM or None if not available
        """
        if 'tempo' in self.results:
            return self.results['tempo'].get('bpm')
        return None
    
    def get_key(self) -> Optional[str]:
        """
        Get the detected key.
        
        Returns:
            Key name or None if not available
        """
        if 'key' in self.results:
            return self.results['key'].get('key')
        return None

