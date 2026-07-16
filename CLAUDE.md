# CLAUDE.md

Guidance for Claude Code when working in this repo. See `README.md` for the
full scaffolding/placeholder reference and the content acquisition pipeline
(`download_and_transcribe.py` + `load_transcripts.py`).

## Content Sourcing Framework

Person-agnostic checklist for building the knowledge base of any new agent
scaffolded from this template. Run through all steps before embedding.

1. **Map the subject's full digital footprint** before downloading anything:
   - Primary YouTube channel.
   - Any secondary YouTube channels.
   - Their own podcast — search `"[Subject Name] podcast"` on YouTube and on
     Spotify's RSS feed.
   - Guest podcast appearances — search YouTube for `"[Subject Name]
     interview"` and `"[Subject Name] podcast guest"`.
   - Their official website.
2. **YouTube transcripts** — download all available transcripts (own
   channel(s) + guest appearances) via `yt-dlp` with auto-subtitles
   (`--write-auto-sub --sub-lang en --skip-download`).
3. **Podcast audio without captions** — download the audio and run Whisper
   (`base` model) to transcribe it locally.
4. **Website content** — scrape all publicly available written content from
   the subject's official site (protocols, blog posts, about pages, FAQ)
   into text files.
5. **Local documents** — copy any PDFs or documents provided for the build
   into the transcripts folder and extract their text.
6. **Report content volume** — before proceeding to embedding, report total
   file count and total size of everything gathered.
