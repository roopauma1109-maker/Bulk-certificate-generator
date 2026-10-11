# Bulk Certificate Generator

A Python FastAPI backend that accepts one bulk request, validates recipients individually, generates PDF certificates from one predefined template, stores job/results in SQLite, and provides status and download endpoints.

## Requirements
- Python 3.10+
- pip

## Setup (Windows)
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

## Run
```bash
uvicorn main:app --reload
```
Open http://127.0.0.1:8000/docs for Swagger UI.

## Create a bulk job
Send `POST /jobs` with JSON:
```json
{
  "event_name": "Python Workshop",
  "issuer": "Example Organization",
  "certificate_date": "2026-10-11",
  "recipients": [
    {"name": "Anu Kumar", "email": "anu@example.com"},
    {"name": "Bala Raj", "email": "bala@example.com"}
  ]
}
```
The response includes `job_id`, total, succeeded, failed, status, progress, and a results URL. Each recipient is processed independently. Invalid recipient data is recorded as a failure; other recipients continue.

## Check status and results
- `GET /jobs/{job_id}` — status and progress summary
- `GET /jobs/{job_id}/certificates` — per-recipient success/failure details
- `GET /certificates/{certificate_id}` — download a generated PDF
- `GET /docs` — interactive API documentation

## Tests
```bash
pytest -v
```

## Design decisions and limitations
- SQLite is used as the relational database for easy local setup.
- Processing is synchronous to keep this assignment simple. The POST request returns after all recipients are processed; the progress endpoint records the final state. For very large production workloads, a background worker/queue should be added.
- Each recipient is validated and generated independently so one failure does not stop the batch.
- A single predefined PDF design is generated with ReportLab.
- Generated PDFs are stored in `generated/`; the database stores their file paths. Do not delete this directory while certificates need to remain downloadable.
- This is an assignment implementation, not a hardened production service. Authentication, rate limits, retention policy, and asynchronous processing are not included.
