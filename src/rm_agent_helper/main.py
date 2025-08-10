#!/usr/bin/env python
import os
import sys
import json
import warnings
from rm_agent_helper.report import generate_html_report
from datetime import datetime

from rm_agent_helper.crew import RmAgentHelper
from rm_agent_helper.utils import coerce_result_to_json_text, normalize_candidates_json
from rm_agent_helper.enrich import load_resume_texts, enrich_candidates

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")


def _coerce_to_json_text(result_obj) -> str:
    return coerce_result_to_json_text(result_obj)


def run():
    """Run the crew, save JSON to output/resource_report.json, and render HTML report."""
    os.makedirs("output", exist_ok=True)
    output_json = os.path.join("output", "resource_report.json")
    output_html = os.path.join("output", "resource_report.html")

    try:
        result = RmAgentHelper().crew().kickoff(inputs={})
        json_text = _coerce_to_json_text(result)
    except Exception as e:
        # If the workflow fails, keep going and try to produce an empty/placeholder report
        print(f"Warning: crew kickoff failed: {e}")
        json_text = "[]"

    json_text_stripped = (json_text or "").strip()
    should_overwrite = True
    if json_text_stripped == "[]" and os.path.exists(output_json):
        try:
            if os.path.getsize(output_json) > 2:
                should_overwrite = False
        except Exception:
            should_overwrite = True

    if should_overwrite:
        final_json_text = normalize_candidates_json(json_text)
        # Enrich with basic heuristics for missing fields
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
        print(f"Saved consolidated report to {output_json}")
    else:
        print(f"Kept existing non-empty report at {output_json}")

    # Generate HTML report using the JSON
    try:
        generate_html_report(output_json, output_html)
        print(f"Saved HTML report to {output_html}")
    except Exception as e:
        print(f"Warning: failed to generate HTML report: {e}")


def train():
    inputs = {"current_year": str(datetime.now().year)}
    RmAgentHelper().crew().train(n_iterations=int(sys.argv[1]), filename=sys.argv[2], inputs=inputs)


def replay():
    RmAgentHelper().crew().replay(task_id=sys.argv[1])


def test():
    inputs = {"current_year": str(datetime.now().year)}
    RmAgentHelper().crew().test(n_iterations=int(sys.argv[1]), eval_llm=sys.argv[2], inputs=inputs)


if __name__ == "__main__":
    run()