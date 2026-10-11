import re
from pathlib import Path
from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from certificate import generate_certificate
from database import Base, engine, get_db
from models import CertificateRecord, Job
from schemas import CreateJobRequest

Base.metadata.create_all(bind=engine)
app = FastAPI(
    title="Bulk Certificate Generator",
    description="Generate certificates in bulk, track job progress, and download PDFs.",
    version="1.0.0",
)

EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

def job_to_dict(job: Job):
    return {
        "job_id": job.id,
        "event_name": job.event_name,
        "issuer": job.issuer,
        "certificate_date": job.certificate_date,
        "status": job.status,
        "total": job.total,
        "succeeded": job.succeeded,
        "failed": job.failed,
        "progress_percent": round(((job.succeeded + job.failed) / job.total) * 100, 2) if job.total else 100,
        "results_url": f"/jobs/{job.id}/certificates",
    }

def certificate_to_dict(item: CertificateRecord):
    return {
        "certificate_id": item.id,
        "recipient_name": item.recipient_name,
        "recipient_email": item.recipient_email,
        "status": item.status,
        "download_url": f"/certificates/{item.id}" if item.status == "success" else None,
        "error": item.error,
    }

@app.get("/")
def home():
    return {"message": "Bulk Certificate Generator API", "docs": "/docs"}

@app.post("/jobs", status_code=201)
def create_job(request: CreateJobRequest, db: Session = Depends(get_db)):
    job = Job(
        event_name=request.event_name.strip(),
        issuer=request.issuer.strip(),
        certificate_date=request.certificate_date.strip(),
        status="processing",
        total=len(request.recipients),
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    for recipient in request.recipients:
        raw_name = recipient.name
        raw_email = recipient.email
        name = raw_name.strip() if isinstance(raw_name, str) else ""
        email = raw_email.strip() if isinstance(raw_email, str) else ""

        item = CertificateRecord(
            job_id=job.id,
            recipient_name=name or "Invalid recipient",
            recipient_email=email,
            status="pending",
        )
        db.add(item)
        db.commit()
        db.refresh(item)

        if not name:
            item.status = "failed"
            item.error = "Recipient name is required."
            job.failed += 1
        elif not email or not EMAIL_PATTERN.match(email):
            item.status = "failed"
            item.error = "A valid email address is required."
            job.failed += 1
        else:
            try:
                item.file_path = generate_certificate(
                    item.id, name, job.event_name, job.issuer, job.certificate_date
                )
                item.status = "success"
                job.succeeded += 1
            except Exception as exc:
                item.status = "failed"
                item.error = f"Certificate generation failed: {type(exc).__name__}"
                job.failed += 1

        db.commit()

    if job.failed == 0:
        job.status = "completed"
    elif job.succeeded == 0:
        job.status = "failed"
    else:
        job.status = "completed_with_errors"
    db.commit()
    db.refresh(job)
    return job_to_dict(job)

@app.get("/jobs/{job_id}")
def get_job(job_id: int, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job_to_dict(job)

@app.get("/jobs/{job_id}/certificates")
def list_job_certificates(job_id: int, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return {
        "job_id": job.id,
        "status": job.status,
        "total": job.total,
        "succeeded": job.succeeded,
        "failed": job.failed,
        "certificates": [certificate_to_dict(item) for item in job.certificates],
    }

@app.get("/certificates/{certificate_id}")
def download_certificate(certificate_id: int, db: Session = Depends(get_db)):
    item = db.query(CertificateRecord).filter(CertificateRecord.id == certificate_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Certificate not found")
    if item.status != "success" or not item.file_path:
        raise HTTPException(status_code=409, detail="Certificate was not generated successfully")
    path = Path(item.file_path).resolve()
    output_root = (Path(__file__).resolve().parent / "generated").resolve()
    if output_root not in path.parents or not path.is_file():
        raise HTTPException(status_code=404, detail="Generated PDF file not found")
    return FileResponse(path, media_type="application/pdf", filename=path.name)
