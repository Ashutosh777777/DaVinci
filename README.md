<img width="1160" height="699" alt="image" src="https://github.com/user-attachments/assets/d5740311-b37b-4153-8b3d-f2f9283a141d" />
# 🔥 DaVinci

> A multi-agent AI system that researches, writes, reviews, illustrates, and publishes blog posts to DEV.to — fully automated, scheduled from a local dashboard.

![DaVinci Architecture](architecture.png)

---

## What It Does

DaVinci turns a topic and a scheduled time into a published DEV.to blog post — no manual writing required. You pick the topic, date, and time from a web dashboard. The rest is handled by a crew of specialized AI agents working in sequence.

---

## Architecture

The diagram above shows the full pipeline:

1. **Content Planner** — takes your topic, uses Serper's web search API to research it, extracts themes and decides the blog structure. Powered by Llama 3.3 70B via Groq.
2. **Blog Writer** — receives the plan and writes a full Markdown blog post with title, intro, sections, and key takeaways. Powered by GPT-OSS 20B via Groq.
3. **Editor / Reviewer** — checks clarity, tone, and flow. Either approves the post or sends it back with suggested changes. Powered by GPT-OSS 20B via Groq.
4. **Image Director** — generates a cover image prompt and calls the Hugging Face image generation API to produce a cover image for the post.
5. **Publisher** — posts the final article (with cover image) to DEV.to via the DEV.to API.

All agents are orchestrated sequentially by **CrewAI**, scheduled by **APScheduler**, and exposed through a **FastAPI** dashboard.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Agent Framework | [CrewAI](https://github.com/crewAIInc/crewAI) |
| LLM Provider | [Groq](https://console.groq.com) via LiteLLM |
| Web Search | [Serper API](https://serper.dev) |
| Image Generation | [Hugging Face Inference API](https://huggingface.co/inference-api) |
| Image Hosting | [Cloudinary](https://cloudinary.com) *(optional)* |
| Blog Publishing | [DEV.to API](https://developers.forem.com/api) |
| Dashboard | [FastAPI](https://fastapi.tiangolo.com) + Jinja2 |
| Scheduler | [APScheduler](https://apscheduler.readthedocs.io) |
| Database | SQLite |
| Config | Pydantic Settings + python-dotenv |

---

## Getting Started

### Prerequisites

- Python 3.11+
- A [Groq API key](https://console.groq.com)
- A [Serper API key](https://serper.dev)
- A [DEV.to API key](https://dev.to/settings/extensions) *(for publishing)*
- A [Hugging Face token](https://huggingface.co/settings/tokens) *(for cover images)*
- Cloudinary credentials *(optional, for public image hosting)*

### Installation

```bash
git clone https://github.com/yourusername/blogforge_ai.git
cd blogforge_ai
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS/Linux
pip install -e .
```

### Configuration

Create a `.env` file in the project root:

```env
# Required
GROQ_API_KEY=your_groq_api_key
SERPER_API_KEY=your_serper_api_key

# For publishing
DEVTO_API_KEY=your_devto_api_key

# For cover images
HF_TOKEN=your_huggingface_token

# Optional: Cloudinary image hosting
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_cloudinary_api_key
CLOUDINARY_API_SECRET=your_cloudinary_api_secret
```

### Run

```bash
blogforge-api
```

Then open [http://127.0.0.1:8000](http://127.0.0.1:8000) in your browser.

---

## Usage

1. Open the dashboard at `http://127.0.0.1:8000`
2. Enter a blog topic
3. Pick a date and time (IST)
4. Hit **Schedule**

---

## Known Quirks

- **Groq rate limits** — free tier has low TPM limits. If a job fails mid-run, wait a minute and reschedule.
- **LiteLLM + Groq compatibility** — newer versions of CrewAI inject `cache_breakpoint` into messages, which Groq rejects. This project includes a runtime patch (`litellm_groq_patch.py`) that strips unsupported fields before they reach the Groq API.

---

## License

MIT
5. The crew runs at the scheduled time and posts directly to your DEV.to account

Scheduled jobs are stored in SQLite and survive server restarts.

---

## Project Structure



blogforge_ai/
├── src/
│   └── blogforge_ai/
│       ├── api.py                  # FastAPI app & routes
│       ├── crew.py                 # CrewAI agents & tasks
│       ├── services.py             # Scheduler & job store
│       ├── schemas.py              # Pydantic models
│       ├── config.py               # Settings & env vars
│       ├── litellm_groq_patch.py   # Groq compatibility patch
│       └── config/
│           ├── agents.yaml         # Agent definitions
│           └── tasks.yaml          # Task definitions
├── templates/                      # Jinja2 HTML templates
├── .env                            # Your API keys (not committed)
├── pyproject.toml
└── README.md
