from fastapi import APIRouter, HTTPException

from app.jobs.queue import QueueDependencyError, get_queue
from app.jobs.tasks import scrape_and_analyze
from app.models.job import JobProgress, JobRequest, JobResponse, JobResult, JobStatus, ReviewData

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.post("", response_model=JobResponse)
async def create_job(payload: JobRequest) -> JobResponse:
    try:
        queue = get_queue()
        job = queue.enqueue(
            scrape_and_analyze,
            payload.get_url(),
            payload.mode,
            payload.limit_qty,
            payload.start_date,
            payload.end_date,
        )
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
    
    result = None
    error = None
    progress = None
    
    if job.meta and "progress" in job.meta:
        progress = JobProgress(**job.meta["progress"])
    
    if job.is_finished:
        status = JobStatus.FINISHED
        if isinstance(job.result, dict):
            reviews = [
                ReviewData(**r) for r in job.result.get("reviews", [])
            ]
            result = JobResult(
                place_id=job.result.get("place_id"),
                place_url=job.result.get("place_url"),
                review_count=job.result.get("review_count", 0),
                analyzed_count=job.result.get("analyzed_count", 0),
                reviews=reviews,
            )
    elif job.is_failed:
        status = JobStatus.FAILED
        error = str(job.exc_info) if job.exc_info else "Unknown error"
    elif job.is_started:
        status = JobStatus.STARTED
    else:
        status = JobStatus.QUEUED
    
    return JobResponse(job_id=job.id, status=status, progress=progress, result=result, error=error)
