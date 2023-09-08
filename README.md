
# Speech Analysis Tool

This tool is designed to extract various speech metrics from a video and save them to a CSV file for further analysis or visualization.
Features

## The tool extracts the following metrics from the video:

- Pitch: The perceived frequency of a sound. The tool extracts pitch values for each frame in the video.
- Intensity: Represents the loudness or softness of a spoken word. The tool captures the intensity values for each frame.
- Harmonicity: Refers to the degree to which the frequencies of a complex sound conform to a harmonic series. It can be used to determine the quality of the voice.
- Formants: Resonant frequencies of the human vocal tract. The tool extracts the first four formant values for each frame.

## Installation

```
pip install git+https://github.com/daedalusLAB/speech_analysis.git
```

## Usage

### Command line

```
speech_analysis --video /path/to/video.mp4 --csv /path/to/output.csv

```
