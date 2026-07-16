# Agent Template

A master scaffold for spinning up a new Claude-powered coaching/sales agent
(Flask + RAG via Pinecone/Voyage + Supabase chat history). It's the
TonyRobbinsAgent codebase with all branding, persona, and color choices
pulled out into `{{PLACEHOLDER}}` tokens.

## How to scaffold a new agent

1. Copy this whole directory to `~/Desktop/<NewAgentName>`.
2. Find-and-replace every `{{PLACEHOLDER}}` token below across all files
   (e.g. with `grep -rl '{{' .` to find files, then edit or `sed -i ''
   "s/{{TOKEN}}/value/g" <file>` per token).
3. Fill in `.env` (copy from `.env.example`) with real API keys, then
   `pip install -r requirements.txt` and run `python app.py`.
4. Build the knowledge base: run `download_and_transcribe.py` to produce the
   transcript source file, then run `load_transcripts.py` to chunk and embed
   it into Pinecone. See [Content acquisition pipeline](#content-acquisition-pipeline)
   below for the full workflow.

## Placeholder reference

### 1. Agent identity (used in `ui.html`, `app.py`, `chat.py`)

| Placeholder | Where it appears | Tony Robbins example |
|---|---|---|
| `{{AGENT_NAME}}` | Browser tab title, welcome heading, CLI banner | `Tony Robbins Mindset Coach` |
| `{{AGENT_ROLE_TITLE}}` | Header bar title | `Mindset & Peak Performance Coach` |
| `{{AGENT_SHORT_NAME}}` | Password screen heading | `Mindset Coach` |
| `{{AGENT_TAGLINE}}` | Password screen subheading | `Tony Robbins Peak Performance Coaching` |
| `{{AGENT_BADGE}}` | Small header badge (short, all-caps) | `TONY` |
| `{{AGENT_EMOJI}}` | Icon shown on password/welcome screens | `🔥` |
| `{{COACH_LABEL}}` | Label on the agent's chat bubbles (`ui.html` and `chat.py`) | `Tony Coach` |
| `{{WELCOME_DESCRIPTION}}` | Paragraph under the welcome heading | `Ask a coaching question, start a breakthrough session, or upload a screenshot of your goals or journal for feedback.` |
| `{{CONTENT_LABEL}}` | RAG context framing: "Relevant ___ content" | `Tony Robbins` |
| `{{IMAGE_ANALYSIS_PROMPT}}` | Default prompt sent when a user uploads an image with no text | `Please analyze this and coach me on my mindset, beliefs, and next decisive action.` |

### 2. Accent color (CSS in `ui.html`)

| Placeholder | Description | Tony Robbins example |
|---|---|---|
| `{{ACCENT_COLOR}}` | Primary accent hex (buttons, highlights, user message bubbles) | `#e8622c` |
| `{{ACCENT_COLOR_HOVER}}` | Darker hover variant of the accent | `#c14d1d` |
| `{{ACCENT_COLOR_RGB}}` | Same color as `r, g, b` (used in `rgba(...)` for the drag-over tint) | `232, 98, 44` |

The rest of the dark-navy theme (backgrounds, borders, text colors) is shared
across agents and is not templated.

### 3. Pinecone index name (`app.py`, `chat.py`, `load_transcripts.py`)

| Placeholder | Description | Tony Robbins example |
|---|---|---|
| `{{PINECONE_INDEX_NAME}}` | Pinecone index that stores the agent's knowledge base | `tony-robbins-agent` |

### 4. Persona description (`app.py`, `chat.py`)

| Placeholder | Description |
|---|---|
| `{{PERSONA_SYSTEM_PROMPT}}` | Full Claude system prompt: the agent's expertise, its modes of operation, image-handling instructions, and closing principles. |

A persona prompt generally has four parts:
1. **Expertise statement** — who/what the agent is trained on.
2. **Modes** — typically a "COACH/TEACHING" mode for direct Q&A and a
   second specialized mode (roleplay, breakthrough session, etc.) with its
   own behavior rules.
3. **Image handling** — how to react when the user uploads a screenshot.
4. **Closing principles** — a short list of hard rules the agent should
   always follow.

Reference example (Tony Robbins agent):
```
You are an AI coach trained exclusively on Tony Robbins' mindset and peak
performance methodology. You have deep knowledge of his frameworks on
psychology, emotional mastery, decision-making, and personal transformation
— including the Six Human Needs, the Triad (physiology, focus, language),
Neuro-Associative Conditioning (NAC), the Dickens Process, Rapid Planning
Method (RPM), and his teachings on beliefs, state management, and
breakthrough.

You have two modes:

1. COACH MODE: Answer questions about Tony's frameworks, explain concepts,
break down his models for change, and give tactical advice on mindset and
peak performance. Always ground your answers in Tony's actual teachings. Be
direct, high-energy, and practical.

2. BREAKTHROUGH MODE: Play the role of a strategic intervention coach in
Tony's style — high intensity, pattern interrupts, bold reframes, and
powerful questions that challenge the user's limiting beliefs. Push the user
past their excuses, call out incongruence between what they say they want
and how they're acting, and guide them toward an empowering decision. After
each exchange, break character briefly to name one limiting belief or
pattern you noticed and one shift to make. Then return to character
immediately. No coddling.

If the user shares a screenshot or image (e.g. a journal entry, goal list, or
note), read it carefully and coach them on their mindset, beliefs, and next
decisive action using Tony's framework.

Always evaluate against Tony's actual framework. Change happens in an
instant, the moment a real decision is made. Focus on state, story, and
strategy — in that order. Identify the limiting belief beneath the surface
problem. Push for massive action, not just insight.
```

### 5. Quick-action cards (`ui.html`, appears twice — initial welcome and `newChat()`)

Four cards, each with an icon, a short label, and the prompt sent when clicked.

| Placeholder | Tony Robbins example |
|---|---|
| `{{QUICK_CARD_1_ICON}}` / `{{QUICK_CARD_1_LABEL}}` / `{{QUICK_CARD_1_PROMPT}}` | `🧠` / `Six Human Needs` / `Explain the Six Human Needs` |
| `{{QUICK_CARD_2_ICON}}` / `{{QUICK_CARD_2_LABEL}}` / `{{QUICK_CARD_2_PROMPT}}` | `🔥` / `Breakthrough Session` / `Start a breakthrough session. I keep procrastinating on my biggest goal.` |
| `{{QUICK_CARD_3_ICON}}` / `{{QUICK_CARD_3_LABEL}}` / `{{QUICK_CARD_3_PROMPT}}` | `🔓` / `Limiting Beliefs` / `How do I break a limiting belief about money?` |
| `{{QUICK_CARD_4_ICON}}` / `{{QUICK_CARD_4_LABEL}}` / `{{QUICK_CARD_4_PROMPT}}` | `⚡` / `State Control` / `What is the Triad and how do I use it to change my state instantly?` |

### 6. Infrastructure

| Placeholder | Where | Description | Tony Robbins example |
|---|---|---|---|
| `{{SERVICE_SLUG}}` | `render.yaml` | Kebab-case service/repo name | `tony-robbins-agent` |
| `{{DEFAULT_APP_PASSWORD}}` | `app.py` | Fallback password if `APP_PASSWORD` env var is unset | `Got1Robbinsagent!` |
| `{{TRANSCRIPT_SOURCE_FILE}}` | `download_and_transcribe.py`, `load_transcripts.py` | Filename (under `~/Desktop/`) of the combined transcript text - written by the pipeline, read by the embedding step | `TonyRobbinsPodcast_Combined.txt` |
| `{{YOUTUBE_CHANNEL_URL}}` | `download_and_transcribe.py` | URL of the YouTube channel or playlist to pull source content from | `https://www.youtube.com/@TonyRobbins/videos` |

## Content acquisition pipeline

Two scripts build the knowledge base, in order:

1. **`download_and_transcribe.py`** — given a YouTube channel/playlist URL,
   produces a single combined text file under `~/Desktop/`.
2. **`load_transcripts.py`** — chunks that text file and upserts embeddings
   into Pinecone.

Both are one-off local scripts (gitignored, like `load_transcripts.py` was
before) — they're not part of the deployed Flask app.

### Prerequisites

```bash
pip install -r requirements-pipeline.txt
brew install ffmpeg yt-dlp
```

`ffmpeg` is required by both `yt-dlp` (audio extraction) and Whisper
(transcription).

### Step 1: `download_and_transcribe.py`

Fill in the two placeholders at the top of the file:

- `{{YOUTUBE_CHANNEL_URL}}` — e.g. a channel's `/videos` page or a playlist URL.
- `{{TRANSCRIPT_SOURCE_FILE}}` — the output filename, e.g.
  `TonyRobbinsPodcast_Combined.txt`. Use the **same value** here and in
  `load_transcripts.py` so the two scripts agree on the file.

Then run:

```bash
python download_and_transcribe.py
```

It does three things:

1. **Download** — uses `yt-dlp` to pull audio (m4a) for every video in the
   channel/playlist, plus any auto-generated English captions (VTT), into
   `~/Desktop/content_pipeline_downloads/`. A download archive file prevents
   re-downloading videos on repeat runs.
2. **Transcribe** — for any video that didn't come with captions, runs
   `whisper` (default model: `base`) on its audio and writes a VTT file.
3. **Clean & combine** — strips VTT headers, timestamps, cue numbers, and
   inline tags from every VTT file, collapses the duplicate/rolling lines
   that both YouTube captions and Whisper produce, and concatenates
   everything into `~/Desktop/{{TRANSCRIPT_SOURCE_FILE}}`.

### Step 2: `load_transcripts.py`

With `{{PINECONE_INDEX_NAME}}` and `{{TRANSCRIPT_SOURCE_FILE}}` filled in
(and `VOYAGE_API_KEY`/`PINECONE_API_KEY` set in your environment), run:

```bash
python load_transcripts.py
```

This creates the Pinecone index if it doesn't exist, splits the transcript
file into ~500-character chunks, embeds them with Voyage, and upserts them
into the index. The Flask app's `get_relevant_context()` then queries this
index for RAG context on every chat message.

## Files

- `app.py` — Flask backend (chat, password, conversation persistence).
- `chat.py` — standalone CLI chat for testing the persona/RAG without the UI.
- `ui.html` — single-page chat UI (drag/drop + paste image upload, up to 5
  images, conversation sidebar).
- `download_and_transcribe.py` — content pipeline step 1: download YouTube
  audio/captions, transcribe with Whisper, clean and combine into a single
  transcript file (gitignored; run locally).
- `load_transcripts.py` — content pipeline step 2: chunk the transcript file
  and upsert embeddings into Pinecone (gitignored; run locally).
- `requirements-pipeline.txt` — dependencies for the content pipeline scripts
  (not needed by the deployed app).
- `render.yaml` — Render Blueprint for deployment.
- `.env.example` — copy to `.env` and fill in for local development.
