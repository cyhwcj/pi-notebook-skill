---
name: notebooklm-podcast
description: Audio Overview - Convert notebook sources into dual-host podcast dialogue. Reuses edge-tts skill.
version: 1.0.0
---

# NotebookLM Podcast

Generate podcasts from notebook sources. Two hosts: Alex (male) and Sam (female).

## Dependencies
- notebooklm-core skill
- edge-tts skill
- ffmpeg (system)

## Triggers
- "generate podcast" / "audio overview" / "make podcast"
- "convert to audio" / "I want to listen to this"

## Parameters
- focus: topic to focus on (optional, default "all content")
- duration: short(5min) / medium(15min) / long(30min), default medium
- style: casual / academic / storytelling, default casual
- language: auto-detect from sources or user specify

## Process

1. Get sources from active notebook (via notebooklm-core)
2. Generate script via LLM:
   ```
   Convert these research materials into a podcast dialogue between Alex (male) and Sam (female).
   Style: {style}, Duration: {duration}, Focus: {focus}
   Requirements:
   - 30s intro: self-intro + topic
   - Discuss core ideas with specific data/quotes
   - Natural speech: "um", "ah", "you know", laughter, surprise
   - Hosts have disagreements, not one-sided
   - 30s outro: summary + "thanks for listening"
   - Word count: {words}

   Format (STRICT):
   Alex: [line]
   Sam: [line]
   ...
   ```

   Word counts: short=800, medium=2000, long=4000

3. Parse dialogue lines
4. Generate audio per line using edge-tts:
   - Alex: `uvx edge-tts --voice "zh-CN-YunyangNeural" --file line.txt --write-media alex_X.mp3`
   - Sam: `uvx edge-tts --voice "zh-CN-XiaoxiaoNeural" --file line.txt --write-media sam_X.mp3`
   - English: en-US-GuyNeural (Alex), en-US-JennyNeural (Sam)

5. Merge with ffmpeg:
   ```bash
   ffmpeg -f concat -safe 0 -i filelist.txt -acodec libmp3lame -q:a 2 output.mp3
   ```

6. Save to `~/pi-cwd-20260526/notebooklm_data/exports/{notebook_id}_podcast.mp3`
7. Return: file path + full script + estimated duration

## Limitations
- Only use current notebook sources
- No fabricated viewpoints
- If no sources, prompt "Please add sources first"
- If edge-tts fails, return script text + installation guide