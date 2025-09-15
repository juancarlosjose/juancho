# MP3 to MIDI Converter

An application that allows you to load an MP3 file and analyze it in depth to separate each voice and instrument and convert them into Musescore-compatible MIDI files. The application also detects the tempo and main key of the audio.

![Application Screenshot](docs/screenshot.png)

## Features

- Load and play MP3 files
- Separate audio into different stems (vocals, drums, bass, other instruments)
- Detect tempo (BPM) and musical key
- Convert separated stems to MIDI files
- Play back both the original MP3 and generated MIDI files
- Download MIDI files to your computer
- Visualize audio waveforms and MIDI data

## Installation

### Prerequisites

- Python 3.8 or higher
- FFmpeg (required for audio processing)

### Install FFmpeg

#### Windows
1. Download FFmpeg from [here](https://ffmpeg.org/download.html)
2. Extract the files to a folder (e.g., `C:\ffmpeg`)
3. Add the `bin` folder to your PATH environment variable

#### macOS
```
brew install ffmpeg
```

#### Linux
```
sudo apt-get install ffmpeg
```

### Install the Application

1. Clone this repository:
```
git clone https://github.com/yourusername/mp3-to-midi-converter.git
cd mp3-to-midi-converter
```

2. Create a virtual environment and activate it:
```
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install the required dependencies:
```
pip install -r requirements.txt
```

4. Alternatively, install the application as a package:
```
pip install -e .
```

## Usage

### Running the Application

Run the application:
```
python main.py
```

Or if installed as a package:
```
mp3tomidi
```

### Basic Workflow

1. Load an MP3 file using the "Open File" button or by dragging and dropping a file
2. Play the MP3 file to preview it
3. Click "Separate Audio" to split the audio into different stems
4. View the analysis results (tempo and key)
5. Convert the stems to MIDI by clicking "Convert to MIDI"
6. Play back the generated MIDI files
7. Download the MIDI files to your computer

For detailed usage instructions, see the [Usage Guide](docs/usage.md).

## How It Works

The application uses several advanced audio processing techniques:

1. **Audio Separation**: Uses [Demucs](https://github.com/facebookresearch/demucs) or [Spleeter](https://github.com/deezer/spleeter) to separate the audio into different stems.

2. **Audio Analysis**: Uses [Librosa](https://librosa.org/) to analyze the audio and detect tempo and key.

3. **MIDI Conversion**: Converts the separated audio stems to MIDI using onset detection, pitch estimation, and note quantization.

4. **Visualization**: Provides various visualizations of the audio and MIDI data to help understand the content.

## License

MIT

## Acknowledgements

- [Demucs](https://github.com/facebookresearch/demucs) - Audio source separation
- [Spleeter](https://github.com/deezer/spleeter) - Audio source separation
- [Librosa](https://librosa.org/) - Audio analysis
- [Mido](https://mido.readthedocs.io/) - MIDI handling
- [PyQt6](https://www.riverbankcomputing.com/software/pyqt/) - GUI framework

