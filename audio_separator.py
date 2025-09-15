"""
Module for separating audio into different stems (vocals, drums, bass, other).
"""
import os
import tempfile
import shutil
import numpy as np
from typing import Dict, List, Optional, Tuple
from PyQt6.QtCore import QObject, pyqtSignal, QThread
import librosa


class SeparationWorker(QThread):
    """Worker thread for audio separation to prevent UI freezing."""
    
    # Define signals
    progress = pyqtSignal(int)  # Progress percentage
    finished = pyqtSignal(dict)  # Separated stems
    error = pyqtSignal(str)     # Error message
    
    def __init__(self, file_path: str, method: str = "demucs", output_dir: Optional[str] = None):
        """
        Initialize the separation worker.
        
        Args:
            file_path: Path to the audio file
            method: Separation method ('demucs' or 'spleeter')
            output_dir: Directory to save separated stems (optional)
        """
        super().__init__()
        self.file_path = file_path
        self.method = method
        self.output_dir = output_dir or tempfile.mkdtemp()
        self.stems = {}
    
    def run(self):
        """Run the separation process."""
        try:
            if self.method == "demucs":
                self._separate_with_demucs()
            elif self.method == "spleeter":
                self._separate_with_spleeter()
            else:
                raise ValueError(f"Unknown separation method: {self.method}")
                
            self.finished.emit(self.stems)
        except Exception as e:
            self.error.emit(str(e))
    
    def _separate_with_demucs(self):
        """Separate audio using Demucs."""
        try:
            # Import here to avoid loading the model until needed
            from demucs.pretrained import get_model
            from demucs.apply import apply_model
            import torch
            
            # Load model
            self.progress.emit(10)
            model = get_model("htdemucs")
            model.cpu()
            model.eval()
            
            # Load audio
            self.progress.emit(20)
            audio, sr = librosa.load(self.file_path, sr=44100, mono=False)
            if audio.ndim == 1:
                audio = audio[None]  # Add channel dimension
            if audio.ndim == 1:
                audio = np.stack([audio, audio])  # Convert mono to stereo
            
            # Convert to torch tensor
            audio = torch.tensor(audio, dtype=torch.float32)
            
            # Apply model
            self.progress.emit(30)
            with torch.no_grad():
                sources = apply_model(model, audio[None], device="cpu")[0]
            
            # Process and save each stem
            stem_names = ["drums", "bass", "other", "vocals"]
            for i, name in enumerate(stem_names):
                self.progress.emit(40 + (i * 15))
                source = sources[i].numpy()
                
                # Save to file
                stem_path = os.path.join(self.output_dir, f"{name}.wav")
                librosa.output.write_wav(stem_path, source, sr)
                
                # Store in stems dictionary
                self.stems[name] = {
                    "path": stem_path,
                    "data": source,
                    "sr": sr
                }
            
            self.progress.emit(100)
            
        except ImportError:
            self.error.emit("Demucs is not installed. Please install it with 'pip install demucs'.")
        except Exception as e:
            self.error.emit(f"Error in Demucs separation: {str(e)}")
    
    def _separate_with_spleeter(self):
        """Separate audio using Spleeter."""
        try:
            # Import here to avoid loading the model until needed
            from spleeter.separator import Separator
            
            # Create separator
            self.progress.emit(10)
            separator = Separator('spleeter:4stems')
            
            # Separate
            self.progress.emit(30)
            separator.separate_to_file(
                self.file_path, 
                self.output_dir,
                codec='wav'
            )
            
            # Process each stem
            stem_names = ["drums", "bass", "other", "vocals"]
            base_name = os.path.splitext(os.path.basename(self.file_path))[0]
            
            for i, name in enumerate(stem_names):
                self.progress.emit(50 + (i * 12))
                
                # Get stem path
                stem_path = os.path.join(self.output_dir, base_name, f"{name}.wav")
                
                # Load stem
                stem_data, sr = librosa.load(stem_path, sr=None)
                
                # Store in stems dictionary
                self.stems[name] = {
                    "path": stem_path,
                    "data": stem_data,
                    "sr": sr
                }
            
            self.progress.emit(100)
            
        except ImportError:
            self.error.emit("Spleeter is not installed. Please install it with 'pip install spleeter'.")
        except Exception as e:
            self.error.emit(f"Error in Spleeter separation: {str(e)}")


class AudioSeparator(QObject):
    """Class for separating audio into different stems."""
    
    # Define signals
    separationStarted = pyqtSignal()
    separationProgress = pyqtSignal(int)
    separationFinished = pyqtSignal(dict)
    separationError = pyqtSignal(str)
    
    def __init__(self):
        """Initialize the audio separator."""
        super().__init__()
        self.worker = None
        self.output_dir = None
        self.stems = {}
    
    def separate(self, file_path: str, method: str = "demucs", output_dir: Optional[str] = None) -> None:
        """
        Separate audio into stems.
        
        Args:
            file_path: Path to the audio file
            method: Separation method ('demucs' or 'spleeter')
            output_dir: Directory to save separated stems (optional)
        """
        # Create output directory if needed
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        
        # Store output directory
        self.output_dir = output_dir or tempfile.mkdtemp()
        
        # Create and start worker thread
        self.worker = SeparationWorker(file_path, method, self.output_dir)
        self.worker.progress.connect(self.separationProgress.emit)
        self.worker.finished.connect(self._on_separation_finished)
        self.worker.error.connect(self.separationError.emit)
        
        # Start separation
        self.separationStarted.emit()
        self.worker.start()
    
    def _on_separation_finished(self, stems: Dict) -> None:
        """
        Handle separation finished signal.
        
        Args:
            stems: Dictionary of separated stems
        """
        self.stems = stems
        self.separationFinished.emit(stems)
    
    def get_stem(self, name: str) -> Optional[Dict]:
        """
        Get a specific stem.
        
        Args:
            name: Stem name ('vocals', 'drums', 'bass', 'other')
            
        Returns:
            Stem data or None if not found
        """
        return self.stems.get(name)
    
    def get_all_stems(self) -> Dict:
        """
        Get all stems.
        
        Returns:
            Dictionary of all stems
        """
        return self.stems
    
    def cleanup(self) -> None:
        """Clean up temporary files."""
        if self.output_dir and os.path.exists(self.output_dir):
            try:
                shutil.rmtree(self.output_dir)
            except Exception:
                pass

