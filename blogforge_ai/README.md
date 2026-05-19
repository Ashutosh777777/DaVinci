# BlogForge AI

A CrewAI-powered multi-agent architecture that turns weekly notes + a chosen topic into a finished blog. It can plan, write, review, generate cover-image prompts, generate an image with Hugging Face, and optionally create a DEV.to draft/post.

## What this implements

- **Content Planner Agent**: extracts themes from weekly notes, uses Serper web search, and decides the blog structure.
- **Blog Writer Agent**: writes the first Markdown draft.
- **Editor / Reviewer Agent**: improves clarity, tone, structure, and flow.
- **Image Director Agent**: creates cover/inline image prompts.
- **Hugging Face image tool**: generates a local cover image.
- **DEV.to posting tool**: creates a DEV.to draft/post using the DEV.to API.
- **FastAPI dashboard**: lets you enter topic, notes, time/date, tags, and run/schedule with one click.
- **SQLite job storage**: stores job status and output paths.

## Architecture

```text
Weekly notes + topic + schedule
        |
FastAPI dashboard / CLI
        |
APScheduler + SQLite job store
        |
CrewAI sequential crew
        |-- Content Planner + Serper
        |-- Blog Writer
        |-- Editor / Reviewer
        |-- Image Director
        |
Hugging Face image generation
        |
DEV.to draft/post
        |
outputs/YYYY-MM-DD/<blog-slug>/blog.md
```

## Setup

### 1. Create environment

```bash
cd blogforge_ai
python -m venv .venv
```

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Linux/macOS:

```bash
source .venv/bin/activate
```

### 2. Install dependencies

Using pip:

```bash
pip install -r requirements.txt
pip install -e .
```

Or using uv:

```bash
uv venv
uv pip install -r requirements.txt
uv pip install -e .
```

### 3. Configure API keys

```bash
cp .env.example .env
```

Fill these values:

```env
GROQ_API_KEY=...
SERPER_API_KEY=...
HF_TOKEN=...
DEVTO_API_KEY=...
```

Minimum required to run the CrewAI blog pipeline:

```env
GROQ_API_KEY=...
SERPER_API_KEY=...
```

Image generation needs `HF_TOKEN`. DEV.to posting needs `DEVTO_API_KEY`.

## Run the web app

```bash
blogforge-api
```

Then open:

```text
http://127.0.0.1:8000
```

Choose topic, notes, time/date, tags, image option and DEV.to option, then click **Run / Schedule Blog**.

## Run from CLI

```bash
blogforge --topic "Building a multi-agent blogging workflow" --notes "This week I explored CrewAI, Groq, Serper, Hugging Face and DEV.to automation."
```

Without image generation:

```bash
blogforge --topic "CrewAI blog automation" --no-images
```

With DEV.to draft/post:

```bash
blogforge --topic "CrewAI blog automation" --publish-to-devto
```

By default `DEVTO_PUBLISH=false`, so the DEV.to API creates an unpublished draft. Set `DEVTO_PUBLISH=true` only when you want direct publishing.

## Output

Generated files are saved under:

```text
outputs/YYYY-MM-DD/<blog-slug-jobid>/blog.md
outputs/YYYY-MM-DD/<blog-slug-jobid>/image_prompts.txt
outputs/images/cover-<slug>-<timestamp>.png
```

## Important notes

1. DEV.to cover images need a public URL. Hugging Face images are saved locally. If you want DEV.to to use them as cover images, upload the image somewhere public and set `IMAGE_PUBLIC_BASE_URL` or modify the upload step.
2. Scheduled jobs persist in SQLite, but they only execute while the FastAPI app is running.
3. Groq model names change over time. If a configured model fails, update `PLANNER_MODEL`, `WRITER_MODEL`, or `EDITOR_MODEL` in `.env`.
4. Keep `.env` out of GitHub. It is already included in `.gitignore`.

## Project structure

```text
blogforge_ai/
├── pyproject.toml
├── requirements.txt
├── .env.example
├── README.md
├── outputs/
└── src/blogforge_ai/
    ├── api.py
    ├── main.py
    ├── crew.py
    ├── config.py
    ├── schemas.py
    ├── utils.py
    ├── config/
    │   ├── agents.yaml
    │   └── tasks.yaml
    ├── services/
    │   ├── pipeline.py
    │   ├── scheduler.py
    │   └── store.py
    ├── tools/
    │   ├── devto_tool.py
    │   └── hf_image_tool.py
    ├── templates/
    │   └── index.html
    └── static/
        └── styles.css
```
