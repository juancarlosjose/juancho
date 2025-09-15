"""
Audio player module for playing MP3 and other audio files.
"""
from PyQt6.QtCore import QUrl, QTimer, pyqtSignal, QObject
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from typing import Optional, Callable


class AudioPlayer(QObject):
    """Class for playing audio files using Qt's media player."""
    
    # Define signals
    positionChanged = pyqtSignal(int)  # Current position in milliseconds
    durationChanged = pyqtSignal(int)  # Total duration in milliseconds
    stateChanged = pyqtSignal(str)     # Player state (playing, paused, stopped)
    
    def __init__(self):
        """Initialize the audio player."""
        super().__init__()
        
        # Create media player and audio output
        self.player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.player.setAudioOutput(self.audio_output)
        
        # Set default volume
        self.audio_output.setVolume(0.7)
        
        # Connect signals
        self.player.positionChanged.connect(self._on_position_changed)
        self.player.durationChanged.connect(self._on_duration_changed)
        self.player.playbackStateChanged.connect(self._on_state_changed)
        
        # Initialize state
        self.current_file = None
        self.duration = 0
        self.position = 0
    
    def load_file(self, file_path: str) -> None:
        """
        Load an audio file.
        
        Args:
            file_path: Path to the audio file
        """
        # Stop any current playback
        self.stop()
        
        # Set the source
        self.current_file = file_path
        self.player.setSource(QUrl.fromLocalFile(file_path))
    
    def play(self) -> None:
        """Start or resume playback."""
        if self.current_file:
            self.player.play()
    
    def pause(self) -> None:
        """Pause playback."""
        self.player.pause()
    
    def stop(self) -> None:
        """Stop playback."""
        self.player.stop()
    
    def set_position(self, position_ms: int) -> None:
        """
        Set the playback position.
        
        Args:
            position_ms: Position in milliseconds
        """
        self.player.setPosition(position_ms)
    
    def set_volume(self, volume: float) -> None:
        """
        Set the playback volume.
        
        Args:
            volume: Volume level (0.0 to 1.0)
        """
        self.audio_output.setVolume(volume)
    
    def get_position(self) -> int:
        """
        Get the current playback position.
        
        Returns:
            Current position in milliseconds
        """
        return self.player.position()
    
    def get_duration(self) -> int:
        """
        Get the total duration of the current audio file.
        
        Returns:
            Duration in milliseconds
        """
        return self.player.duration()
    
    def is_playing(self) -> bool:
        """
        Check if the player is currently playing.
        
        Returns:
            True if playing, False otherwise
        """
        return self.player.playbackState() == QMediaPlayer.PlaybackState.PlayingState
    
    def _on_position_changed(self, position: int) -> None:
        """
        Handle position changed signal.
        
        Args:
            position: Current position in milliseconds
        """
        self.position = position
        self.positionChanged.emit(position)
    
    def _on_duration_changed(self, duration: int) -> None:
        """
        Handle duration changed signal.
        
        Args:
            duration: Total duration in milliseconds
        """
        self.duration = duration
        self.durationChanged.emit(duration)
    
    def _on_state_changed(self, state) -> None:
        """
        Handle state changed signal.
        
        Args:
            state: New playback state
        """
        state_map = {
            QMediaPlayer.PlaybackState.PlayingState: "playing",
            QMediaPlayer.PlaybackState.PausedState: "paused",
            QMediaPlayer.PlaybackState.StoppedState: "stopped"
        }
        self.stateChanged.emit(state_map.get(state, "unknown"))


class MIDIPlayer(QObject):
    """Class for playing MIDI files."""
    
    # Define signals
    positionChanged = pyqtSignal(int)  # Current position in milliseconds
    durationChanged = pyqtSignal(int)  # Total duration in milliseconds
    stateChanged = pyqtSignal(str)     # Player state (playing, paused, stopped)
    
    def __init__(self):
        """Initialize the MIDI player."""
        super().__init__()
        
        # We'll use QMediaPlayer for MIDI playback as well
        # This is a simplified approach - a more advanced implementation
        # would use a dedicated MIDI library like FluidSynth
        self.player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.player.setAudioOutput(self.audio_output)
        
        # Set default volume
        self.audio_output.setVolume(0.7)
        
        # Connect signals
        self.player.positionChanged.connect(self._on_position_changed)
        self.player.durationChanged.connect(self._on_duration_changed)
        self.player.playbackStateChanged.connect(self._on_state_changed)
        
        # Initialize state
        self.current_file = None
        self.duration = 0
        self.position = 0
    
    def load_file(self, file_path: str) -> None:
        """
        Load a MIDI file.
        
        Args:
            file_path: Path to the MIDI file
        """
        # Stop any current playback
        self.stop()
        
        # Set the source
        self.current_file = file_path
        self.player.setSource(QUrl.fromLocalFile(file_path))
    
    def play(self) -> None:
        """Start or resume playback."""
        if self.current_file:
            self.player.play()
    
    def pause(self) -> None:
        """Pause playback."""
        self.player.pause()
    
    def stop(self) -> None:
        """Stop playback."""
        self.player.stop()
    
    def set_position(self, position_ms: int) -> None:
        """
        Set the playback position.
        
        Args:
            position_ms: Position in milliseconds
        """
        self.player.setPosition(position_ms)
    
    def set_volume(self, volume: float) -> None:
        """
        Set the playback volume.
        
        Args:
            volume: Volume level (0.0 to 1.0)
        """
        self.audio_output.setVolume(volume)
    
    def get_position(self) -> int:
        """
        Get the current playback position.
        
        Returns:
            Current position in milliseconds
        """
        return self.player.position()
    
    def get_duration(self) -> int:
        """
        Get the total duration of the current MIDI file.
        
        Returns:
            Duration in milliseconds
        """
        return self.player.duration()
    
    def is_playing(self) -> bool:
        """
        Check if the player is currently playing.
        
        Returns:
            True if playing, False otherwise
        """
        return self.player.playbackState() == QMediaPlayer.PlaybackState.PlayingState
    
    def _on_position_changed(self, position: int) -> None:
        """
        Handle position changed signal.
        
        Args:
            position: Current position in milliseconds
        """
        self.position = position
        self.positionChanged.emit(position)
    
    def _on_duration_changed(self, duration: int) -> None:
        """
        Handle duration changed signal.
        
        Args:
            duration: Total duration in milliseconds
        """
        self.duration = duration
        self.durationChanged.emit(duration)
    
    def _on_state_changed(self, state) -> None:
        """
        Handle state changed signal.
        
        Args:
            state: New playback state
        """
        state_map = {
            QMediaPlayer.PlaybackState.PlayingState: "playing",
            QMediaPlayer.PlaybackState.PausedState: "paused",
            QMediaPlayer.PlaybackState.StoppedState: "stopped"
        }
        self.stateChanged.emit(state_map.get(state, "unknown"))

