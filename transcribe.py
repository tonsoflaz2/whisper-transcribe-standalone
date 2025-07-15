import os
import sys
import whisperx

# Add local ffmpeg to path
os.environ["PATH"] = os.path.join(os.path.dirname(__file__), "whisperx-bundle", "ffmpeg") + ":" + os.environ.get("PATH", "")

def format_time(seconds):
    """Convert seconds to SRT time format (HH:MM:SS,mmm)"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = seconds % 60
    return f"{hours:02d}:{minutes:02d}:{secs:06.3f}".replace('.', ',')

device = "cpu"
model_name = "medium"
compute_type = "int8"

if len(sys.argv) < 2:
    print("❌ Usage: python transcribe.py <input_file> [output_dir] [--diarize] [--words-only]")
    sys.exit(1)

audio_file = sys.argv[1]
output_dir = None
# Check if the second argument is a directory (and not a flag)
if len(sys.argv) > 2 and not sys.argv[2].startswith('--'):
    output_dir = sys.argv[2]
    args_offset = 1
else:
    args_offset = 0

enable_diarization = "--diarize" in sys.argv
words_only = "--words-only" in sys.argv

# Generate output filenames
base_name = os.path.splitext(os.path.basename(audio_file))[0]
if output_dir:
    os.makedirs(output_dir, exist_ok=True)
    txt_file = os.path.join(output_dir, f"{base_name}_transcript.txt")
    srt_file = os.path.join(output_dir, f"{base_name}_subtitles.srt")
else:
    txt_file = f"{base_name}_transcript.txt"
    srt_file = f"{base_name}_subtitles.srt"

print(f"🔊 Transcribing: {audio_file}")
model = whisperx.load_model(model_name, device=device, compute_type=compute_type)
result = model.transcribe(audio_file)

print("🧠 Aligning words...")
align_model, metadata = whisperx.load_align_model(language_code=result["language"], device=device)
aligned = whisperx.align(result["segments"], align_model, metadata, audio_file, device=device)

if words_only:
    print("📌 Word-level timestamps only:")
    with open(txt_file, 'w', encoding='utf-8') as f:
        for word in aligned["word_segments"]:
            line = f"{word['start']:.2f} - {word['end']:.2f}: {word['word']}"
            print(line)
            f.write(line + '\n')
    print(f"✅ Saved to: {txt_file}")
    sys.exit(0)

if enable_diarization:
    print("🧍 Performing speaker diarization...")
    diarize_model = whisperx.DiarizationPipeline(use_auth_token=None, device=device)
    diarize_segments = diarize_model(audio_file)
    result_with_speakers = whisperx.assign_word_speakers(diarize_segments, aligned["word_segments"])

    print("🗣️ Speaker-separated transcript:")
    with open(txt_file, 'w', encoding='utf-8') as f:
        for word in result_with_speakers:
            line = f"[{word['speaker']}] {word['start']:.2f} - {word['end']:.2f}: {word['word']}"
            print(line)
            f.write(line + '\n')
    
    # Create SRT file for diarization
    with open(srt_file, 'w', encoding='utf-8') as f:
        subtitle_num = 1
        for word in result_with_speakers:
            start_time = format_time(word['start'])
            end_time = format_time(word['end'])
            f.write(f"{subtitle_num}\n")
            f.write(f"{start_time} --> {end_time}\n")
            f.write(f"[{word['speaker']}] {word['word']}\n\n")
            subtitle_num += 1
    
    print(f"✅ Saved to: {txt_file} and {srt_file}")
else:
    print("📝 Full transcript (with word-level alignment):")
    
    # Save segment-level transcript to TXT
    with open(txt_file, 'w', encoding='utf-8') as f:
        f.write("=== SEGMENT-LEVEL TRANSCRIPT ===\n")
        for segment in result["segments"]:
            line = f"[{segment['start']:.2f} - {segment['end']:.2f}] {segment['text']}"
            print(line)
            f.write(line + '\n')
        
        f.write("\n=== WORD-LEVEL TIMESTAMPS ===\n")
        for word in aligned["word_segments"]:
            line = f"{word['start']:.2f} - {word['end']:.2f}: {word['word']}"
            print(line)
            f.write(line + '\n')
    
    # Create SRT file from segments
    with open(srt_file, 'w', encoding='utf-8') as f:
        subtitle_num = 1
        for segment in result["segments"]:
            start_time = format_time(segment['start'])
            end_time = format_time(segment['end'])
            f.write(f"{subtitle_num}\n")
            f.write(f"{start_time} --> {end_time}\n")
            f.write(f"{segment['text'].strip()}\n\n")
            subtitle_num += 1
    
    print(f"✅ Saved to: {txt_file} and {srt_file}")
