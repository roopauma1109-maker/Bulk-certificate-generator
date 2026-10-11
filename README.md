# Bulk Certificate Generator

A REST API built with **Python, FastAPI, SQLite, and ReportLab** to generate multiple PDF certificates from a single request. The application validates each recipient independently, stores processing results, and provides APIs to track jobs and download certificates.

## Key Features

- Bulk certificate generation through a single API request.
- Individual recipient validation and error handling.
- PDF certificate generation using ReportLab.
- Job tracking and recipient-level results.
- SQLite database for persistent records.
- Certificate downloads through REST endpoints.
- Interactive Swagger API documentation.
- Automated testing with pytest.

## Tech Stack

| Technology | Purpose |
|---|---|
| Python | Backend programming |
| FastAPI | REST API development |
| SQLite | Job and result storage |
| ReportLab | PDF certificate generation |
| Uvicorn | Application server |
| Pytest | Automated testing |

## Getting Started

### 1. Prerequisites

Install Python 3.10 or later and pip.

Verify the installation:

```bash
python --version
pip --version
```

### 2. Clone the Repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd bulk-certificate-generator
```

If you have already downloaded the project, open its folder in VS Code and run the following commands in the terminal.

### 3. Create and Activate a Virtual Environment

```bash
python -m venv venv
venv\Scripts\activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

## Start the Server

Run the following command from the project directory:

```bash
python -m uvicorn main:app --reload
```

After the server starts, open Swagger UI:

**http://127.0.0.1:8000/docs**

Use this page to execute API requests and inspect their responses.

## Generate Your First Certificates

### Step 1: Create a Job

Open `POST /jobs`, click **Try it out**, and enter the following request:

```json
{
  "event_name": "Python Workshop",
  "issuer": "Example Organization",
  "certificate_date": "2026-10-11",
  "recipients": [
    {
      "name": "Anu Kumar",
      "email": "anu@example.com"
    },
    {
      "name": "Bala Raj",
      "email": "bala@example.com"
    }
  ]
}
```

Click **Execute** to process the recipients.

### Step 2: Check the Result

A successful request should return a job identifier and a summary of the processing results. For example:

```json
{
  "job_id": "your-generated-job-id",
  "total": 2,
  "succeeded": 2,
  "failed": 0,
  "status": "completed",
  "progress": 100
}
```

The values above are illustrative. Use the actual response returned by your application.

### Step 3: Find the Generated PDFs

After successful processing, open the project directory and locate:

```text
bulk-certificate-generator/
└── generated/
    ├── certificate_1.pdf
    └── certificate_2.pdf
```

These filenames are examples; the actual filenames depend on your implementation.

Open a PDF file to view the generated certificate. The certificate should contain the recipient and event information supported by your template.

### Example Certificate Content

```text
       CERTIFICATE OF PARTICIPATION

              This is presented to

                  ANU KUMAR

      for participating in the Python Workshop

           Issued by Example Organization

                Date: 11 October 2026
```

The actual PDF design depends on the template defined in the application.

## API Reference

| HTTP Method | Endpoint | Function |
|---|---|---|
| POST | `/jobs` | Create a bulk certificate job |
| GET | `/jobs/{job_id}` | View job status and progress |
| GET | `/jobs/{job_id}/certificates` | View recipient results |
| GET | `/certificates/{certificate_id}` | Download a certificate |
| GET | `/docs` | Interactive API documentation |

### Download a Certificate Through the API

1. Submit a bulk request to `POST /jobs`.
2. Copy the returned `job_id`.
3. Call `GET /jobs/{job_id}/certificates`.
4. Copy a successful recipient's `certificate_id`.
5. Call `GET /certificates/{certificate_id}` to retrieve the PDF.

## Run Tests

Execute the automated test suite:

```bash
pytest -v
```

The tests should verify the behaviors covered by your test suite, including validation, certificate generation, and failure handling where applicable.

## How It Works

1. **Request:** The client submits event information and a list of recipients.
2. **Validation:** The application validates each recipient individually.
3. **Generation:** A PDF certificate is generated for each valid recipient.
4. **Storage:** Job details, recipient results, and certificate file paths are stored.
5. **Retrieval:** Clients can check job results and download generated PDFs.

## Error Handling

Each recipient is processed independently. If one recipient fails validation or certificate generation, the application records the failure and continues processing the remaining recipients.

## Limitations

- Processing is synchronous.
- Certificates are stored on the local filesystem.
- SQLite is used for local data persistence.
- Authentication and rate limiting are not implemented.
- Background workers are not included.
- Generated files must be retained for downloads to work.

## Future Improvements

- CSV and Excel recipient uploads.
- Email delivery of certificates.
- Custom certificate templates.
- Background job processing.
- Real-time progress updates.
- Authentication and access control.

