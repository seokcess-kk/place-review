from fastapi import APIRouter, HTTPException

from app.jobs.queue import QueueDependencyError, get_queue
from app.jobs.tasks import scrape_and_analyze
from app.models.job import JobRequest, JobResponse, JobStatus

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.post("", response_model=JobResponse)
async def create_job(payload: JobRequest) -> JobResponse:
    try:
        queue = get_queue()
        job = queue.enqueue(scrape_and_analyze, payload.url, payload.mode, payload.limit_qty)
    except QueueDependencyError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    return JobResponse(job_id=job.id, status=JobStatus.QUEUED)


@router.get("/{job_id}", response_model=JobResponse)
async def get_job(job_id: str) -> JobResponse:
    try:
        queue = get_queue()
    except QueueDependencyError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    job = queue.fetch_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    if job.is_finished:
        status = JobStatus.FINISHED
    elif job.is_failed:
        status = JobStatus.FAILED
    elif job.is_started:
        status = JobStatus.STARTED
    else:
        status = JobStatus.QUEUED
    return JobResponse(job_id=job.id, status=status)
