from fastapi import APIRouter, BackgroundTasks
from pydantic import BaseModel
import os
import json
from typing import Optional

from rm_agent_helper.main import run as run_cli
from rm_agent_helper.crew import RmAgentHelper
from rm_agent_helper.utils import coerce_result_to_json_text, normalize_candidates_json
from rm_agent_helper.report import generate_html_report
from rm_agent_helper.job_report import generate_job_match_html_report
from rm_agent_helper.enrich import load_resume_texts, enrich_candidates


router = APIRouter()


class KickoffResponse(BaseModel):
    message: str
    output_json: Optional[str] = None
    output_html: Optional[str] = None


def _kickoff_and_persist() -> None:
    os.makedirs("output", exist_ok=True)
    output_json = os.path.join("output", "resource_report.json")
    output_html = os.path.join("output", "resource_report.html")
    job_match_json = os.path.join("output", "job_match_report.json")
    job_match_html = os.path.join("output", "job_match_report.html")

    try:
        result = RmAgentHelper().crew().kickoff(inputs={})
        json_text = coerce_result_to_json_text(result)
    except Exception:
        json_text = "[]"

    json_text_stripped = (json_text or "").strip()
    should_overwrite = True
    if json_text_stripped == "[]" and os.path.exists(output_json):
        try:
            if os.path.getsize(output_json) > 2:
                should_overwrite = False
        except Exception:
            should_overwrite = True

    try:
        if should_overwrite:
            final_json_text = normalize_candidates_json(json_text)
            try:
                data = json.loads(final_json_text)
                if isinstance(data, list):
                    texts = load_resume_texts()
                    data = enrich_candidates(data, texts)
                    final_json_text = json.dumps(data)
            except Exception:
                pass
            with open(output_json, "w", encoding="utf-8") as f:
                f.write(final_json_text)
        # Always attempt to render HTML
        generate_html_report(output_json, output_html)
        # If the crew's result is job-match JSON, persist and render
        try:
            obj = json.loads(json_text)
            if isinstance(obj, list) and obj and isinstance(obj[0], dict) and (
                ("job-file" in obj[0] or "job_file" in obj[0]) and "matches" in obj[0]
            ):
                with open(job_match_json, "w", encoding="utf-8") as f:
                    json.dump(obj, f, ensure_ascii=False, indent=2)
                generate_job_match_html_report(job_match_json, job_match_html)
        except Exception:
            pass
    except Exception:
        pass


@router.post("/kickoff", response_model=KickoffResponse)
async def kickoff(background_tasks: BackgroundTasks) -> KickoffResponse:
    background_tasks.add_task(_kickoff_and_persist)
    return KickoffResponse(
        message="Crew kickoff started",
        output_json="output/resource_report.json",
        output_html="output/resource_report.html",
    )


