# Resume Reviewer AI

A production-ready resume review application built with Streamlit and NVIDIA Nemotron 3.5 Lightning 30B A3B.

## Features

- Upload resume as PDF, DOCX, or TXT
- Upload a job description or paste it directly
- NVIDIA Nemotron-powered resume/job matching
- Overall match score and ATS score
- Strengths and gaps
- Keyword analysis
- Actionable recommendations
- Truthful rewritten professional summary
- Interview preparation focus
- JSON-structured model output
- Docker + Render deployment configuration
- Automated tests

## Architecture

```text
Browser
   |
   v
Streamlit UI
   |
   +--> PyMuPDF / python-docx --> document text
   |
   v
Review service
   |
   v
NVIDIA NIM OpenAI-compatible API
   |
   v
nemotron-3.5-lightning-30b-a3b
   |
   v
Validated JSON --> UI
```

The application does **not** run the 30B model on Render. Render hosts the web app; inference is sent to NVIDIA's hosted API.

## Local setup

### 1. Clone

```bash
git clone <your-repo-url>
cd ResumeReviewAI
```

### 2. Create environment

Windows:

```powershell
python -m venv .venv
.venv\Scripts\activate
```

macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install

```bash
pip install -r requirements.txt
```

### 4. Configure NVIDIA

Create `.env` locally or export the variable in your shell:

```text
NVIDIA_API_KEY=nvapi-...
NVIDIA_MODEL=nvidia/nemotron-3.5-lightning-30b-a3b
NVIDIA_BASE_URL=https://integrate.api.nvidia.com/v1
```

Do not commit `.env`.

### 5. Run

```bash
streamlit run app.py
```

Open the local URL shown by Streamlit.

## Tests

```bash
pytest -q
```

The NVIDIA request is mocked in tests, so tests do not consume API credits.

## Docker

```bash
docker build -t resume-reviewer-ai .
docker run --rm -p 8501:8501 \
  -e NVIDIA_API_KEY=nvapi-your-key \
  resume-reviewer-ai
```

Open:

```text
http://localhost:8501
```

## Deploy on Render

### Option A — Blueprint

Push this repository to GitHub, then create a new Render Blueprint using `render.yaml`.

Set:

```text
NVIDIA_API_KEY = your NVIDIA API key
```

The model and NVIDIA base URL are already defined in `render.yaml`.

### Option B — Web Service

Create a Render Web Service from the GitHub repository.

- Runtime: Docker
- Dockerfile: `Dockerfile`
- Health check path: `/`
- Environment:
  - `NVIDIA_API_KEY` = your NVIDIA key
  - `NVIDIA_MODEL` = `nvidia/nemotron-3.5-lightning-30b-a3b`
  - `NVIDIA_BASE_URL` = `https://integrate.api.nvidia.com/v1`

Render provides the `PORT` environment variable; the Docker command uses it automatically.

## Important deployment notes

- Never put `NVIDIA_API_KEY` in frontend JavaScript or Streamlit source.
- Keep the API key only in Render Environment Variables.
- Uploaded documents are processed in memory and are not intentionally persisted by this application.
- Render's free instance can sleep when idle, so the first request may be slower.
- NVIDIA hosted inference is separate from Render compute.

## Resume review scoring

The scores are model-generated guidance, not guarantees of interview selection or ATS behavior. The app is designed to surface evidence and gaps for a specific job description.

## Project structure

```text
ResumeReviewAI/
├── app.py
├── src/
│   ├── __init__.py
│   ├── resume_parser.py
│   └── review_agent.py
├── tests/
│   ├── test_resume_parser.py
│   └── test_review_agent.py
├── requirements.txt
├── Dockerfile
├── render.yaml
├── .env.example
├── .gitignore
└── README.md
```
