"""
Setup script for the MP3 to MIDI converter application.
"""
from setuptools import setup, find_packages

setup(
    name="mp3-to-midi-converter",
    version="0.1.0",
    description="An application that analyzes MP3 files and converts them to MIDI",
    author="Juan Carlos José Montero Prieto",
    author_email="juancarlosjose.montero@gmail.com",
    packages=find_packages(),
    install_requires=[
        "PyQt6>=6.5.0",
        "librosa>=0.10.0",
        "demucs>=4.0.0",
        "spleeter>=2.4.0",
        "pydub>=0.25.1",
        "mido>=1.2.10",
        "python-rtmidi>=1.5.0",
        "pretty_midi>=0.2.10",
        "matplotlib>=3.7.0",
        "numpy>=1.24.0",
        "tqdm>=4.65.0",
    ],
    entry_points={
        "console_scripts": [
            "mp3tomidi=main:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Multimedia :: Sound/Audio :: Analysis",
        "Topic :: Multimedia :: Sound/Audio :: Conversion",
    ],
    python_requires=">=3.8",
)

