#!/bin/bash
set -e

# === CONFIG ===
BUNDLE_DIR="whisperx-bundle"
PYTHON_VERSION="3.9"
WHISPER_MODEL="medium"
FFMPEG_URL="https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz"

# === SAFETY: Prevent running inside wrong virtualenv ===
if [[ -n "$VIRTUAL_ENV" && "$VIRTUAL_ENV" != "$(pwd)/$BUNDLE_DIR/whisperx-env" ]]; then
  echo "❌ You're already inside another virtual environment: $VIRTUAL_ENV"
  echo "Please deactivate it before running this script."
  exit 1
fi

# === STEP 1: Handle existing bundle directory ===
if [[ -d "$BUNDLE_DIR" ]]; then
  echo "⚠️  Bundle directory '$BUNDLE_DIR' already exists."
  read -p "Reuse existing directory and skip recreating it? (y/n): " reuse
  if [[ "$reuse" != "y" ]]; then
    echo "❌ Aborting. Delete the folder or rename it first."
    exit 1
  fi
else
  echo "📁 Creating bundle directory: $BUNDLE_DIR"
  mkdir -p "$BUNDLE_DIR"
fi

cd "$BUNDLE_DIR"

# === STEP 2: Virtualenv Setup ===
if [[ ! -d "whisperx-env" ]]; then
  echo "🐍 Creating Python $PYTHON_VERSION virtual environment..."
  python3 -m venv whisperx-env
else
  echo "🐍 Virtual environment already exists. Reusing."
fi

source whisperx-env/bin/activate

if [[ "$VIRTUAL_ENV" != "$(pwd)/whisperx-env" ]]; then
  echo "❌ Failed to activate expected virtualenv: whisperx-env"
  deactivate || true
  exit 1
fi

# === STEP 3: Install Python packages ===
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

echo "📦 Installing PyTorch (CPU)..."
pip install torch torchvision torchaudio

echo "📦 Installing WhisperX..."
pip install git+https://github.com/m-bain/whisperx.git

echo "🧠 Downloading WhisperX model: $WHISPER_MODEL"
python -c "import whisperx; whisperx.load_model('$WHISPER_MODEL', device='cpu', compute_type='int8')"

# === STEP 4: FFmpeg Download ===
if [[ -f "ffmpeg/ffmpeg" ]]; then
  echo "🎞️  FFmpeg already exists. Skipping download."
else
  echo "🎞️  Downloading static FFmpeg..."
  mkdir -p ffmpeg
  curl -L "$FFMPEG_URL" -o ffmpeg.tar.xz
  tar -xf ffmpeg.tar.xz --strip-components=1 -C ffmpeg
  rm ffmpeg.tar.xz
fi

# === DONE ===
deactivate
echo "✅ WhisperX bundle ready at: $(pwd)"
du -sh .
