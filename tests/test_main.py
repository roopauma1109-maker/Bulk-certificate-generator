from fastapi.testclient import TestClient
from main import app
from database import Base, engine
from models import Job, CertificateRecord

client = TestClient(app)

def setup_function():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

def sample_payload():
    return {
        "event_name": "Python Workshop",
        "issuer": "Example Organization",
        "certificate_date": "2026-10-11",
        "recipients": [
            {"name": "Anu", "email": "anu@example.com"},
            {"name": "Bala", "email": "bala@example.com"},
        ],
    }

def test_create_job_and_generate_certificates():
    response = client.post("/jobs", json=sample_payload())
    assert response.status_code == 201
    data = response.json()
    assert data["total"] == 2
    assert data["succeeded"] == 2
    assert data["failed"] == 0
    assert data["status"] == "completed"

def test_invalid_recipient_does_not_stop_others():
    payload = sample_payload()
    payload["recipients"] = [
        {"name": "", "email": "bad@example.com"},
        {"name": "Valid Person", "email": "valid@example.com"},
    ]
    response = client.post("/jobs", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["succeeded"] == 1
    assert data["failed"] == 1
    assert data["status"] == "completed_with_errors"

def test_input_validation_for_missing_event():
    payload = sample_payload()
    payload.pop("event_name")
    response = client.post("/jobs", json=payload)
    assert response.status_code == 422

def test_job_status_and_results():
    created = client.post("/jobs", json=sample_payload()).json()
    job_id = created["job_id"]
    status = client.get(f"/jobs/{job_id}")
    results = client.get(f"/jobs/{job_id}/certificates")
    assert status.status_code == 200
    assert status.json()["progress_percent"] == 100
    assert results.status_code == 200
    assert len(results.json()["certificates"]) == 2

def test_download_generated_certificate():
    created = client.post("/jobs", json=sample_payload()).json()
    results = client.get(f"/jobs/{created['job_id']}/certificates").json()
    certificate_id = results["certificates"][0]["certificate_id"]
    download = client.get(f"/certificates/{certificate_id}")
    assert download.status_code == 200
    assert download.headers["content-type"] == "application/pdf"
    assert download.content.startswith(b"%PDF")

def test_missing_job_returns_404():
    response = client.get("/jobs/999999")
    assert response.status_code == 404
