# ⚠️ Disclaimer

**The goal of this project is to set up a standalone environment for local, free transcription using WhisperX. However, this setup does install software (ffmpeg and a portable Python interpreter) on your system. It tries to stay siloed but if you see a reason this is not safe please correct it or add it as an issue so others can evaluate! You should always review the scripts and code before running anything, especially on production or sensitive systems!**

---

# WhisperX Transcription Bundle

This repository provides a safe, portable way to set up [WhisperX](https://github.com/m-bain/whisperx) for transcribing audio/video files (e.g., `.mp4`) to text and SRT subtitles, with **no system-wide dependencies**.

## ⚡ Disk Space Requirements

**You will need at least 2–3 GB of free disk space** to install and run this project with the default "medium" model. Breakdown:

| Component         | Approx. Size |
|-------------------|--------------|
| Portable Python   | 50–100 MB    |
| venv + deps       | 200–500 MB   |
| PyTorch (CPU)     | 500–800 MB   |
| WhisperX model    | 1.5 GB       |
| FFmpeg            | 100 MB       |
| **Total**         | **2–3 GB**   |

- Using a larger model (e.g., "large") will require more space (2–3 GB+ for the model alone).
- If you process many files or keep lots of outputs, you'll need additional space.

---

## What's New: Fully Standalone with Portable Python 3.11

- The setup script now **downloads and uses its own portable Python 3.11 interpreter** (from [python-build-standalone](https://github.com/indygreg/python-build-standalone)).
- **No system Python or system packages are required or used.**
- All dependencies (Python, virtual environment, packages, FFmpeg) are local to the project directory.
- No root/sudo required.
- **Python 3.11 is used for best compatibility with WhisperX and onnxruntime.**

## Files

- **build-whisperx-bundle.sh**  
  Installs all dependencies in a local bundle directory using a portable Python 3.11 and virtual environment. Does not require root/sudo and will not affect system Python or packages.

- **transcribe.py**  
  Transcribes audio/video files using WhisperX, outputting both a timestamped `.txt` transcript and an `.srt` subtitle file. Can be run manually or called from other scripts (e.g., PHP/Laravel).

---

## Quick Start

### 1. Clone or Download

```bash
git clone https://github.com/tonsoflaz2/whisper-transcribe-standalone
cd whisper-transcribe-standalone
```

### 2. Run the Setup Script

```bash
chmod +x build-whisperx-bundle.sh
./build-whisperx-bundle.sh --clean
```

- This creates a `whisperx-bundle` directory with all dependencies and a local FFmpeg.
- The script will also create a `python-standalone` directory with a portable Python 3.11 interpreter.
- Use the `--clean` option to remove any previous install and start fresh.

### 3. Activate the Virtual Environment

```bash
source whisperx-bundle/whisperx-env/bin/activate
```

### 4. Transcribe a File

```bash
python transcribe.py /path/to/input.mp4 /path/to/output_dir
```
- The output directory is optional. If omitted, output files are saved in the current directory.
- Output files:  
  - `[input_basename]_transcript.txt`  
  - `[input_basename]_subtitles.srt`

---

## Usage from PHP/Laravel

You can call the transcription from a Laravel command or controller:

```php
$venvActivate = '/path/to/whisperx-bundle/whisperx-env/bin/activate';
$pythonScript = '/path/to/transcribe.py';
$inputFile = '/path/to/input.mp4';
$outputDir = '/path/to/output_dir';

$cmd = "source $venvActivate && python $pythonScript $inputFile $outputDir";
$output = shell_exec("bash -c '$cmd'");
```

---

## .gitignore

This repo is set up to only track `build-whisperx-bundle.sh`, `transcribe.py`, `README.md`, and `.gitignore` itself. All other files and folders (including the bundle, portable Python, and outputs) are ignored.

---

## Notes

- No root/sudo required.
- All dependencies are local to `whisperx-bundle` and `python-standalone`.
- Safe for use on shared or production servers.
- You can edit `transcribe.py` at any time without rerunning the setup.
- The setup script will **never use or modify system Python**.
- **Python 3.11 is used for best compatibility with WhisperX and onnxruntime.**

---

## License

MIT or your preferred license. 
