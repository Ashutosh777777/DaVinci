import uuid
from datetime import datetime, timezone

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.date import DateTrigger

from blogforge_ai.schemas import BlogRequest
from blogforge_ai.services.pipeline import run_blog_pipeline
from blogforge_ai.services import store

scheduler = BackgroundScheduler(timezone="UTC")


def _run_and_persist(job_id: str, request: BlogRequest) -> None:
    store.update_job(job_id, "running")
    result = run_blog_pipeline(request, job_id=job_id)
    store.update_job(job_id, result.status, result=result.model_dump(), error=result.error)


def start_scheduler() -> None:
    store.init_db()
    if not scheduler.running:
        scheduler.start()
    for job in store.pending_jobs():
        run_at = datetime.fromisoformat(job["scheduled_for"])
        if run_at < datetime.now(timezone.utc):
            run_at = datetime.now(timezone.utc)
        request = BlogRequest(**job["request"])
        scheduler.add_job(
            _run_and_persist,
            DateTrigger(run_date=run_at),
            args=[job["id"], request],
            id=job["id"],
            replace_existing=True,
        )


def submit(request: BlogRequest) -> str:
    job_id = str(uuid.uuid4())
    if request.scheduled_for:
        run_at = request.scheduled_for
        if run_at.tzinfo is None:
            run_at = run_at.replace(tzinfo=timezone.utc)
        store.create_job(job_id, request.model_dump(), "scheduled", run_at.isoformat())
        scheduler.add_job(
            _run_and_persist,
            DateTrigger(run_date=run_at),
            args=[job_id, request],
            id=job_id,
            replace_existing=True,
        )
    else:
        store.create_job(job_id, request.model_dump(), "queued")
        scheduler.add_job(_run_and_persist, args=[job_id, request], id=job_id, replace_existing=True)
    return job_id
