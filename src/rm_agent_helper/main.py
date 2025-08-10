#!/usr/bin/env python
import os
import sys
import json
import warnings
from datetime import datetime

from rm_agent_helper.crew import RmAgentHelper

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")


def _coerce_to_json_text(result_obj) -> str:
    try:
        if isinstance(result_obj, str):
            return result_obj
        if isinstance(result_obj, (list, dict)):
            return json.dumps(result_obj)
        # Try common CrewOutput attributes
        for attr in [
            "raw",
            "raw_output",
            "output",
            "final_output",
            "json",
        ]:
            if hasattr(result_obj, attr):
                value = getattr(result_obj, attr)
                if callable(value):
                    try:
                        value = value()
                    except Exception:
                        continue
                if isinstance(value, str):
                    return value
                if isinstance(value, (list, dict)):
                    return json.dumps(value)
        # Try to_json method
        if hasattr(result_obj, "to_json") and callable(getattr(result_obj, "to_json")):
            try:
                return result_obj.to_json()
            except Exception:
                pass
        # Fallback to string and trust if it looks like JSON
        text = str(result_obj).strip()
        if text.startswith("[") or text.startswith("{"):
            return text
    except Exception:
        pass
    # Ultimate fallback: empty array
    return "[]"


def run():
    """Run the crew and save consolidated JSON to output/resource_report.json."""
    os.makedirs("output", exist_ok=True)
    result = RmAgentHelper().crew().kickoff(inputs={})
    json_text = _coerce_to_json_text(result)

    output_path = os.path.join("output", "resource_report.json")
    with open(output_path, "w") as f:
        f.write(json_text)

    print(f"Saved consolidated report to {output_path}")


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