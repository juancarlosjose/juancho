"""
Module for converting audio to MIDI.
"""
import os
import numpy as np
import librosa
import mido
import pretty_midi
from typing import Dict, List, Tuple, Optional, Any
from PyQt6.QtCore import QObject, pyqtSignal, QThread


# MIDI instrument mappings (General MIDI)
MIDI_INSTRUMENTS = {
    'vocals': 54,  # Voice Oohs
    'drums': 0,    # Standard Drum Kit (channel 10)
    'bass': 33,    # Electric Bass
    'other': 0     # Acoustic Grand Piano
}

# MIDI drum mappings
DRUM_MAPPINGS = {
    'kick': 36,
    'snare': 38,
    'hi-hat': 42,
    'tom': 45,
    'cymbal': 49
}


class ConversionWorker(QThread):
    """Worker thread for audio to MIDI conversion to prevent UI freezing."""
    
    # Define signals
    progress = pyqtSignal(int)  # Progress percentage
    finished = pyqtSignal(dict)  # Conversion results
    error = pyqtSignal(str)     # Error message
    
    def __init__(self, stems: Dict[str, Dict], analysis_results: Dict[str, Any], 
                 output_dir: str, quantize: bool = True):
        """
        Initialize the conversion worker.
        
        Args:
            stems: Dictionary of audio stems
            analysis_results: Dictionary of analysis results
            output_dir: Directory to save MIDI files
            quantize: Whether to quantize notes to the beat grid
        """
        super().__init__()
        self.stems = stems
        self.analysis_results = analysis_results
        self.output_dir = output_dir
        self.quantize = quantize
        self.results = {}
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
    
    def run(self):
        """Run the conversion process."""
        try:
            # Create a combined MIDI file with all stems
            self.progress.emit(10)
            combined_midi = self._create_combined_midi()
            
            # Process each stem
            stem_count = len(self.stems)
            for i, (stem_name, stem_data) in enumerate(self.stems.items()):
                progress = 20 + int((i / stem_count) * 70)
                self.progress.emit(progress)
                
                # Convert stem to MIDI
                midi_data = self._convert_stem_to_midi(stem_name, stem_data)
                
                # Save MIDI file
                midi_path = os.path.join(self.output_dir, f"{stem_name}.mid")
                midi_data.write(midi_path)
                
                # Store in results
                self.results[stem_name] = {
                    'path': midi_path,
                    'midi': midi_data
                }
            
            # Save combined MIDI
            combined_path = os.path.join(self.output_dir, "combined.mid")
            combined_midi.write(combined_path)
            self.results['combined'] = {
                'path': combined_path,
                'midi': combined_midi
            }
            
            self.progress.emit(100)
            self.finished.emit(self.results)
            
        except Exception as e:
            self.error.emit(str(e))
    
    def _create_combined_midi(self) -> pretty_midi.PrettyMIDI:
        """
        Create a combined MIDI file with all stems.
        
        Returns:
            PrettyMIDI object with all stems
        """
        # Create a new MIDI file
        midi = pretty_midi.PrettyMIDI()
        
        # Set tempo if available
        if 'tempo' in self.analysis_results:
            tempo = self.analysis_results['tempo'].get('bpm', 120.0)
            midi.initial_tempo = tempo
        
        return midi
    
    def _convert_stem_to_midi(self, stem_name: str, stem_data: Dict) -> pretty_midi.PrettyMIDI:
        """
        Convert an audio stem to MIDI.
        
        Args:
            stem_name: Name of the stem
            stem_data: Stem data dictionary
            
        Returns:
            PrettyMIDI object
        """
        # Create a new MIDI file
        midi = pretty_midi.PrettyMIDI()
        
        # Set tempo if available
        if 'tempo' in self.analysis_results:
            tempo = self.analysis_results['tempo'].get('bpm', 120.0)
            midi.initial_tempo = tempo
        
        # Get audio data and sample rate
        audio = stem_data['data']
        sr = stem_data['sr']
        
        # Handle different stem types
        if stem_name == 'drums':
            self._convert_drums_to_midi(midi, audio, sr)
        elif stem_name == 'bass':
            self._convert_bass_to_midi(midi, audio, sr)
        elif stem_name == 'vocals':
            self._convert_vocals_to_midi(midi, audio, sr)
        else:  # 'other'
            self._convert_other_to_midi(midi, audio, sr)
        
        return midi
    
    def _convert_drums_to_midi(self, midi: pretty_midi.PrettyMIDI, audio: np.ndarray, sr: int) -> None:
        """
        Convert drum audio to MIDI.
        
        Args:
            midi: PrettyMIDI object to add drums to
            audio: Audio data
            sr: Sample rate
        """
        # Create a drum instrument (channel 10)
        drum_program = 0  # Standard drum kit
        drums = pretty_midi.Instrument(program=drum_program, is_drum=True, name="Drums")
        
        # Detect onsets for different drum components
        # This is a simplified approach - a real implementation would use
        # more sophisticated drum separation techniques
        
        # Kick drum (low frequencies)
        kick_audio = librosa.effects.harmonic(audio)
        kick_audio = librosa.feature.rms(y=librosa.effects.percussive(audio), frame_length=2048, hop_length=512)
        kick_onsets = librosa.onset.onset_detect(
            onset_envelope=np.mean(kick_audio, axis=0),
            sr=sr,
            units='time'
        )
        
        # Snare and hi-hat (high frequencies)
        high_audio = librosa.effects.percussive(audio)
        high_onsets = librosa.onset.onset_detect(
            y=high_audio,
            sr=sr,
            units='time'
        )
        
        # Add kick drum notes
        for onset in kick_onsets:
            # Create a note
            note = pretty_midi.Note(
                velocity=100,  # Velocity (loudness)
                pitch=DRUM_MAPPINGS['kick'],
                start=onset,
                end=onset + 0.1  # Short duration for drums
            )
            drums.notes.append(note)
        
        # Add snare and hi-hat notes
        for i, onset in enumerate(high_onsets):
            # Alternate between snare and hi-hat
            if i % 2 == 0:
                pitch = DRUM_MAPPINGS['snare']
            else:
                pitch = DRUM_MAPPINGS['hi-hat']
            
            # Create a note
            note = pretty_midi.Note(
                velocity=80,  # Velocity (loudness)
                pitch=pitch,
                start=onset,
                end=onset + 0.1  # Short duration for drums
            )
            drums.notes.append(note)
        
        # Add the drum instrument to the MIDI file
        midi.instruments.append(drums)
    
    def _convert_bass_to_midi(self, midi: pretty_midi.PrettyMIDI, audio: np.ndarray, sr: int) -> None:
        """
        Convert bass audio to MIDI.
        
        Args:
            midi: PrettyMIDI object to add bass to
            audio: Audio data
            sr: Sample rate
        """
        # Create a bass instrument
        bass_program = MIDI_INSTRUMENTS['bass']
        bass = pretty_midi.Instrument(program=bass_program, name="Bass")
        
        # Extract pitch
        pitches, magnitudes = librosa.piptrack(
            y=audio,
            sr=sr,
            fmin=30,  # Minimum frequency for bass
            fmax=250  # Maximum frequency for bass
        )
        
        # Detect onsets
        onsets = librosa.onset.onset_detect(
            y=audio,
            sr=sr,
            units='time'
        )
        
        # Get beat information for quantization
        if self.quantize and 'beats' in self.analysis_results:
            beat_times = np.array(self.analysis_results['beats'].get('beat_times', []))
        else:
            beat_times = np.array([])
        
        # Convert onsets to notes
        for i in range(len(onsets) - 1):
            start_time = onsets[i]
            end_time = onsets[i + 1]
            
            # Quantize to beats if enabled
            if self.quantize and len(beat_times) > 0:
                # Find nearest beat for start and end
                start_beat_idx = np.argmin(np.abs(beat_times - start_time))
                end_beat_idx = np.argmin(np.abs(beat_times - end_time))
                
                # Use beat times
                start_time = beat_times[start_beat_idx]
                end_time = beat_times[end_beat_idx]
            
            # Find the most prominent pitch in this segment
            start_frame = librosa.time_to_frames(start_time, sr=sr)
            end_frame = librosa.time_to_frames(end_time, sr=sr)
            
            # Ensure valid frame indices
            start_frame = max(0, min(start_frame, pitches.shape[1] - 1))
            end_frame = max(0, min(end_frame, pitches.shape[1] - 1))
            
            if start_frame < end_frame:
                segment_pitches = pitches[:, start_frame:end_frame]
                segment_magnitudes = magnitudes[:, start_frame:end_frame]
                
                # Find the pitch with the highest magnitude
                max_mag_idx = np.argmax(np.mean(segment_magnitudes, axis=1))
                pitch_hz = segment_pitches[max_mag_idx, 0]
                
                # Convert Hz to MIDI note number
                if pitch_hz > 0:
                    midi_note = int(round(librosa.hz_to_midi(pitch_hz)))
                    
                    # Create a note
                    note = pretty_midi.Note(
                        velocity=80,  # Velocity (loudness)
                        pitch=midi_note,
                        start=start_time,
                        end=end_time
                    )
                    bass.notes.append(note)
        
        # Add the bass instrument to the MIDI file
        midi.instruments.append(bass)
    
    def _convert_vocals_to_midi(self, midi: pretty_midi.PrettyMIDI, audio: np.ndarray, sr: int) -> None:
        """
        Convert vocal audio to MIDI.
        
        Args:
            midi: PrettyMIDI object to add vocals to
            audio: Audio data
            sr: Sample rate
        """
        # Create a vocal instrument
        vocal_program = MIDI_INSTRUMENTS['vocals']
        vocals = pretty_midi.Instrument(program=vocal_program, name="Vocals")
        
        # Extract pitch using CREPE or pYIN would be better for vocals,
        # but we'll use librosa's pitch tracking for simplicity
        pitches, magnitudes = librosa.piptrack(
            y=audio,
            sr=sr,
            fmin=80,   # Minimum frequency for vocals
            fmax=800   # Maximum frequency for vocals
        )
        
        # Detect onsets
        onsets = librosa.onset.onset_detect(
            y=audio,
            sr=sr,
            units='time'
        )
        
        # Get beat information for quantization
        if self.quantize and 'beats' in self.analysis_results:
            beat_times = np.array(self.analysis_results['beats'].get('beat_times', []))
        else:
            beat_times = np.array([])
        
        # Convert onsets to notes
        for i in range(len(onsets) - 1):
            start_time = onsets[i]
            end_time = onsets[i + 1]
            
            # Quantize to beats if enabled
            if self.quantize and len(beat_times) > 0:
                # Find nearest beat for start and end
                start_beat_idx = np.argmin(np.abs(beat_times - start_time))
                end_beat_idx = np.argmin(np.abs(beat_times - end_time))
                
                # Use beat times
                start_time = beat_times[start_beat_idx]
                end_time = beat_times[end_beat_idx]
            
            # Find the most prominent pitch in this segment
            start_frame = librosa.time_to_frames(start_time, sr=sr)
            end_frame = librosa.time_to_frames(end_time, sr=sr)
            
            # Ensure valid frame indices
            start_frame = max(0, min(start_frame, pitches.shape[1] - 1))
            end_frame = max(0, min(end_frame, pitches.shape[1] - 1))
            
            if start_frame < end_frame:
                segment_pitches = pitches[:, start_frame:end_frame]
                segment_magnitudes = magnitudes[:, start_frame:end_frame]
                
                # Find the pitch with the highest magnitude
                max_mag_idx = np.argmax(np.mean(segment_magnitudes, axis=1))
                pitch_hz = segment_pitches[max_mag_idx, 0]
                
                # Convert Hz to MIDI note number
                if pitch_hz > 0:
                    midi_note = int(round(librosa.hz_to_midi(pitch_hz)))
                    
                    # Create a note
                    note = pretty_midi.Note(
                        velocity=90,  # Velocity (loudness)
                        pitch=midi_note,
                        start=start_time,
                        end=end_time
                    )
                    vocals.notes.append(note)
        
        # Add the vocal instrument to the MIDI file
        midi.instruments.append(vocals)
    
    def _convert_other_to_midi(self, midi: pretty_midi.PrettyMIDI, audio: np.ndarray, sr: int) -> None:
        """
        Convert other instruments audio to MIDI.
        
        Args:
            midi: PrettyMIDI object to add other instruments to
            audio: Audio data
            sr: Sample rate
        """
        # Create an instrument for other sounds
        other_program = MIDI_INSTRUMENTS['other']
        other = pretty_midi.Instrument(program=other_program, name="Other")
        
        # Extract pitch
        pitches, magnitudes = librosa.piptrack(
            y=audio,
            sr=sr,
            fmin=60,   # Minimum frequency
            fmax=2000  # Maximum frequency
        )
        
        # Detect onsets
        onsets = librosa.onset.onset_detect(
            y=audio,
            sr=sr,
            units='time'
        )
        
        # Get beat information for quantization
        if self.quantize and 'beats' in self.analysis_results:
            beat_times = np.array(self.analysis_results['beats'].get('beat_times', []))
        else:
            beat_times = np.array([])
        
        # Convert onsets to notes
        for i in range(len(onsets) - 1):
            start_time = onsets[i]
            end_time = onsets[i + 1]
            
            # Quantize to beats if enabled
            if self.quantize and len(beat_times) > 0:
                # Find nearest beat for start and end
                start_beat_idx = np.argmin(np.abs(beat_times - start_time))
                end_beat_idx = np.argmin(np.abs(beat_times - end_time))
                
                # Use beat times
                start_time = beat_times[start_beat_idx]
                end_time = beat_times[end_beat_idx]
            
            # Find the most prominent pitch in this segment
            start_frame = librosa.time_to_frames(start_time, sr=sr)
            end_frame = librosa.time_to_frames(end_time, sr=sr)
            
            # Ensure valid frame indices
            start_frame = max(0, min(start_frame, pitches.shape[1] - 1))
            end_frame = max(0, min(end_frame, pitches.shape[1] - 1))
            
            if start_frame < end_frame:
                segment_pitches = pitches[:, start_frame:end_frame]
                segment_magnitudes = magnitudes[:, start_frame:end_frame]
                
                # Find the pitch with the highest magnitude
                max_mag_idx = np.argmax(np.mean(segment_magnitudes, axis=1))
                pitch_hz = segment_pitches[max_mag_idx, 0]
                
                # Convert Hz to MIDI note number
                if pitch_hz > 0:
                    midi_note = int(round(librosa.hz_to_midi(pitch_hz)))
                    
                    # Create a note
                    note = pretty_midi.Note(
                        velocity=70,  # Velocity (loudness)
                        pitch=midi_note,
                        start=start_time,
                        end=end_time
                    )
                    other.notes.append(note)
        
        # Add the other instrument to the MIDI file
        midi.instruments.append(other)


class MIDIConverter(QObject):
    """Class for converting audio to MIDI."""
    
    # Define signals
    conversionStarted = pyqtSignal()
    conversionProgress = pyqtSignal(int)
    conversionFinished = pyqtSignal(dict)
    conversionError = pyqtSignal(str)
    
    def __init__(self):
        """Initialize the MIDI converter."""
        super().__init__()
        self.worker = None
        self.results = {}
    
    def convert(self, stems: Dict[str, Dict], analysis_results: Dict[str, Any], 
                output_dir: str, quantize: bool = True) -> None:
        """
        Convert audio stems to MIDI.
        
        Args:
            stems: Dictionary of audio stems
            analysis_results: Dictionary of analysis results
            output_dir: Directory to save MIDI files
            quantize: Whether to quantize notes to the beat grid
        """
        # Create and start worker thread
        self.worker = ConversionWorker(stems, analysis_results, output_dir, quantize)
        self.worker.progress.connect(self.conversionProgress.emit)
        self.worker.finished.connect(self._on_conversion_finished)
        self.worker.error.connect(self.conversionError.emit)
        
        # Start conversion
        self.conversionStarted.emit()
        self.worker.start()
    
    def _on_conversion_finished(self, results: Dict) -> None:
        """
        Handle conversion finished signal.
        
        Args:
            results: Dictionary of conversion results
        """
        self.results = results
        self.conversionFinished.emit(results)
    
    def get_results(self) -> Dict:
        """
        Get conversion results.
        
        Returns:
            Dictionary of conversion results
        """
        return self.results
    
    def get_midi_file(self, name: str) -> Optional[str]:
        """
        Get the path to a specific MIDI file.
        
        Args:
            name: Name of the MIDI file ('vocals', 'drums', 'bass', 'other', 'combined')
            
        Returns:
            Path to the MIDI file or None if not found
        """
        if name in self.results:
            return self.results[name].get('path')
        return None

