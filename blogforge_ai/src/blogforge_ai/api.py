from blogforge_ai.litellm_groq_patch import patch_litellm_for_groq
patch_litellm_for_groq()



from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo

import uvicorn
from fastapi import FastAPI, Form, Request, Query
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from blogforge_ai.config import settings
from blogforge_ai.schemas import BlogRequest
from blogforge_ai.services import scheduler, store

BASE_DIR = Path(__file__).parent
app = FastAPI(title="BlogForge AI", version="0.1.0")
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=BASE_DIR / "templates")


@app.on_event("startup")
def on_startup() -> None:
    scheduler.start_scheduler()


@app.get("/", response_class=HTMLResponse)
def home(request: Request, created_job_id: str | None = Query(default=None)):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "jobs": store.list_jobs(20),
            "created_job_id": created_job_id,
        },
    )


@app.post("/jobs", response_class=HTMLResponse)
def create_job(
    request: Request,
    topic: str = Form(...),
    weekly_notes: str = Form(""),
    scheduled_for: str = Form(""),
    target_audience: str = Form("developers and tech readers"),
    tone: str = Form("clear, practical and engaging"),
    devto_tags: str = Form("ai,programming,productivity"),
    publish_to_devto: str | None = Form(None),
    generate_images: str | None = Form(None),
): 
    dt = None
    if scheduled_for.strip():
        local_tz = ZoneInfo("Asia/Kolkata")
        local_dt = datetime.fromisoformat(scheduled_for.strip())
        dt = local_dt.replace(tzinfo=local_tz)
    req = BlogRequest(
        topic=topic,
        weekly_notes=weekly_notes,
        scheduled_for=dt,
        target_audience=target_audience,
        tone=tone,
        devto_tags=[tag.strip() for tag in devto_tags.split(",") if tag.strip()],
        publish_to_devto=publish_to_devto == "on",
        generate_images=generate_images == "on",
    )
    job_id = scheduler.submit(req)
    return RedirectResponse(
    url=f"/?created_job_id={job_id}",
    status_code=303,
    )

@app.get("/api/jobs")
def api_jobs():
    return store.list_jobs(50)


@app.get("/api/jobs/{job_id}")
def api_job(job_id: str):
    job = store.get_job(job_id)
    if not job:
        return JSONResponse({"error": "Job not found"}, status_code=404)
    return job


def run() -> None:
    uvicorn.run("blogforge_ai.api:app", host=settings.app_host, port=settings.app_port, reload=True)


if __name__ == "__main__":
    run()
