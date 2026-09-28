from __future__ import annotations

import json
import os
from typing import Any
from dotenv import load_dotenv
from openai import OpenAI


MODEL = os.getenv("NVIDIA_MODEL", "nvidia/nemotron-3.5-lightning-30b-a3b")
BASE_URL = os.getenv("NVIDIA_BASE_URL", "https://integrate.api.nvidia.com/v1")

SYSTEM_PROMPT = """
You are a professional technical recruiter and ATS resume reviewer.

Analyze a candidate resume against a target job description. Be evidence-based:
- Never invent experience, skills, education, metrics, companies, or certifications.
- Do not penalize a candidate for information that is simply absent unless it matters to the job.
- Distinguish a missing keyword from missing actual experience.
- Prefer specific, actionable recommendations.
- Keep the suggested professional summary truthful to the resume.

Return ONLY valid JSON matching this schema:
{
  "overall_score": integer 0-100,
  "ats_score": integer 0-100,
  "strengths": ["string"],
  "gaps": ["string"],
  "keyword_analysis": ["string"],
  "recommendations": ["string"],
  "rewritten_summary": "string",
  "interview_focus": ["string"]
}

Use 3-6 items for each list. Scores must be integers.
""".strip()


class ReviewError(RuntimeError):
    pass

load_dotenv()

MODEL = os.getenv(
    "NVIDIA_MODEL",
    "nvidia/nemotron-3.5-lightning-30b-a3b",
)

BASE_URL = os.getenv(
    "NVIDIA_BASE_URL",
    "https://integrate.api.nvidia.com/v1",
)

def _client() -> OpenAI:
    api_key = os.getenv("NVIDIA_API_KEY")
    if not api_key:
        raise ReviewError("NVIDIA_API_KEY is not configured. Add it to Render Environment Variables.")
    return OpenAI(api_key=api_key, base_url=BASE_URL, timeout=90.0, max_retries=2)


def _clean_json(text: str) -> dict[str, Any]:
    text = text.strip()
    if text.startswith("```"):
        text = text.replace("```json", "", 1).replace("```", "", 1).strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        raise ReviewError("The model returned an invalid review format. Please retry.") from exc


def _validate(result: dict[str, Any]) -> dict[str, Any]:
    required = [
        "overall_score",
        "ats_score",
        "strengths",
        "gaps",
        "keyword_analysis",
        "recommendations",
        "rewritten_summary",
        "interview_focus",
    ]
    missing = [key for key in required if key not in result]
    if missing:
        raise ReviewError(f"Review response is missing fields: {', '.join(missing)}")

    for score in ("overall_score", "ats_score"):
        result[score] = max(0, min(100, int(result[score])))

    for key in (
        "strengths",
        "gaps",
        "keyword_analysis",
        "recommendations",
        "interview_focus",
    ):
        if not isinstance(result[key], list):
            raise ReviewError(f"Invalid review field: {key}")
        result[key] = [str(x).strip() for x in result[key] if str(x).strip()]

    result["rewritten_summary"] = str(result["rewritten_summary"]).strip()
    return result


def review_resume(resume_text: str, job_description: str) -> dict[str, Any]:
    if not resume_text.strip():
        raise ReviewError("Resume text is empty.")
    if not job_description.strip():
        raise ReviewError("Job description is empty.")

    prompt = f"""
RESUME
------
{resume_text[:60000]}

JOB DESCRIPTION
---------------
{job_description[:40000]}

Review the resume specifically for this job. Focus on factual alignment, ATS
keywords, relevant evidence, measurable achievements, clarity, and truthful
improvements.
""".strip()

    try:
        response = _client().chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
            max_tokens=2200,
            response_format={"type": "json_object"},
            extra_body={"chat_template_kwargs": {"enable_thinking": False}},
        )
        content = response.choices[0].message.content
        if not content:
            raise ReviewError("The model returned an empty response.")
        return _validate(_clean_json(content))
    except ReviewError:
        raise
    except Exception as exc:
        raise ReviewError(f"NVIDIA API request failed: {exc}") from exc
