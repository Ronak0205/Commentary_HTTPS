"""
Async HTTP service around the report-generation pipeline.

Endpoints:
    GET  /                     -- upload UI (static/index.html)
    POST /process              -- upload a PDF, returns a job_id immediately
    GET  /status/{job_id}      -- poll job status
    GET  /download/{job_id}    -- download the merged JSON once the job is done
"""

import os
import shutil
import tempfile
import uuid
from datetime import datetime, timezone
from enum import Enum

from fastapi import BackgroundTasks, FastAPI, File, HTTPException, UploadFile
from fastapi.responses import FileResponse

from pipeline.pipeline import PipelineError, process_pdf

app = FastAPI(title="Board Report Commentary API")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_DIR = os.path.join(BASE_DIR, "static")


@app.get("/")
def ui():
    index_path = os.path.join(STATIC_DIR, "index.html")
    if not os.path.isfile(index_path):
        raise HTTPException(status_code=500, detail="UI file not found (static/index.html missing).")
    return FileResponse(index_path, media_type="text/html")


JOBS_ROOT = os.path.join(tempfile.gettempdir(), "board_report_jobs")
os.makedirs(JOBS_ROOT, exist_ok=True)

MAX_UPLOAD_BYTES = 50 * 1024 * 1024  # 50 MB
PDF_MAGIC = b"%PDF-"


class JobStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    DONE = "done"
    ERROR = "error"


JOBS = {}


def _job_dir(job_id):
    return os.path.join(JOBS_ROOT, job_id)


def _run_job(job_id, pdf_path, pdf_name):
    JOBS[job_id]["status"] = JobStatus.RUNNING
    try:
        job_dir = _job_dir(job_id)
        result = process_pdf(
            pdf_path,
            pdf_name,
            extracted_img_dir=os.path.join(job_dir, "extracted_img"),
            data_dir=os.path.join(job_dir, "data"),
        )
        JOBS[job_id]["status"] = JobStatus.DONE
        JOBS[job_id]["result_path"] = result["final_output_path"]
    except PipelineError as e:
        JOBS[job_id]["status"] = JobStatus.ERROR
        JOBS[job_id]["error"] = str(e)
    except Exception as e:
        JOBS[job_id]["status"] = JobStatus.ERROR
        JOBS[job_id]["error"] = f"Unexpected error: {e}"


@app.post("/process")
async def process(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only .pdf files are accepted.")

    contents = await file.read()

    if len(contents) > MAX_UPLOAD_BYTES:
        raise HTTPException(
            status_code=413,
            detail=f"File exceeds the {MAX_UPLOAD_BYTES // (1024 * 1024)}MB limit.",
        )

    if not contents.startswith(PDF_MAGIC):
        raise HTTPException(status_code=400, detail="File does not look like a valid PDF.")

    job_id = uuid.uuid4().hex
    job_dir = _job_dir(job_id)
    os.makedirs(job_dir, exist_ok=True)

    pdf_name = os.path.splitext(os.path.basename(file.filename))[0]
    pdf_path = os.path.join(job_dir, f"{pdf_name}.pdf")
    with open(pdf_path, "wb") as f:
        f.write(contents)

    JOBS[job_id] = {
        "status": JobStatus.PENDING,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "error": None,
        "result_path": None,
        "pdf_name": pdf_name,
    }

    background_tasks.add_task(_run_job, job_id, pdf_path, pdf_name)

    return {"job_id": job_id, "status": JOBS[job_id]["status"]}


@app.get("/status/{job_id}")
def status(job_id: str):
    job = JOBS.get(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Unknown job_id.")

    response = {
        "job_id": job_id,
        "status": job["status"],
        "pdf_name": job["pdf_name"],
        "created_at": job["created_at"],
    }
    if job["status"] == JobStatus.ERROR:
        response["error"] = job["error"]
    return response


@app.get("/download/{job_id}")
def download(job_id: str):
    job = JOBS.get(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Unknown job_id.")

    if job["status"] != JobStatus.DONE:
        raise HTTPException(
            status_code=409,
            detail=f"Job is not ready for download (status: {job['status']}).",
        )

    result_path = job["result_path"]
    if not result_path or not os.path.isfile(result_path):
        raise HTTPException(status_code=500, detail="Result file is missing.")

    return FileResponse(
        result_path,
        media_type="application/json",
        filename=f"{job['pdf_name']}_report.json",
    )


@app.delete("/jobs/{job_id}")
def delete_job(job_id: str):
    job = JOBS.pop(job_id, None)
    if job is None:
        raise HTTPException(status_code=404, detail="Unknown job_id.")
    shutil.rmtree(_job_dir(job_id), ignore_errors=True)
    return {"deleted": job_id}