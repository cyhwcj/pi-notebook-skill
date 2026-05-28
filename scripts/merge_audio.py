import sys, json, os, subprocess

def create_filelist(dialogue, output_dir):
    """Create ffmpeg filelist for concatenation."""
    filelist_path = os.path.join(output_dir, "filelist.txt")
    with open(filelist_path, 'w', encoding='utf-8') as f:
        for i, line in enumerate(dialogue):
            mp3_file = f"{line['speaker'].lower()}_{i:04d}.mp3"
            f.write(f"file '{mp3_file}'\n")
    return filelist_path

def merge_audio(output_dir, output_file="podcast.mp3"):
    """Merge audio files using ffmpeg."""
    filelist_path = create_filelist([], output_dir)  # This will be overwritten with real data

    # Actually we need to read the actual dialogue from a JSON file
    dialogue_file = os.path.join(output_dir, "dialogue.json")
    if os.path.exists(dialogue_file):
        with open(dialogue_file, 'r', encoding='utf-8') as f:
            dialogue = json.load(f)
        create_filelist(dialogue, output_dir)

    output_path = os.path.join(output_dir, output_file)
    result = subprocess.run([
        'ffmpeg', '-f', 'concat', '-safe', '0',
        '-i', filelist_path,
        '-acodec', 'libmp3lame', '-q:a', '2',
        output_path
    ], capture_output=True, text=True)

    return {"status": "ok" if result.returncode == 0 else "error", "output": output_path, "stderr": result.stderr}

if __name__ == "__main__":
    output_dir = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser("~/pi-cwd-20260526/notebooklm_data/exports")
    result = merge_audio(output_dir)
    print(json.dumps(result, ensure_ascii=False))