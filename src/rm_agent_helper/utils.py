import json
import re
from typing import Any


_FENCE_RE = re.compile(r"```(?:json)?\s*([\s\S]*?)\s*```", re.IGNORECASE)


def _try_parse_and_dump(text: str) -> str | None:
    try:
        obj = json.loads(text)
        return json.dumps(obj)
    except Exception:
        return None


def extract_json_text(raw_text: str) -> str:
    if not isinstance(raw_text, str):
        return "[]"

    candidate = raw_text.strip()

    # 1) If entire content is fenced JSON or contains a fenced block, use it
    m = _FENCE_RE.search(candidate)
    if m:
        fenced = m.group(1).strip()
        dumped = _try_parse_and_dump(fenced)
        if dumped is not None:
            return dumped

    # 2) Try direct parse
    dumped = _try_parse_and_dump(candidate)
    if dumped is not None:
        return dumped

    # 3) Heuristic: locate first/last JSON array or object
    first_bracket = candidate.find("[")
    last_bracket = candidate.rfind("]")
    if first_bracket != -1 and last_bracket != -1 and last_bracket > first_bracket:
        sliced = candidate[first_bracket : last_bracket + 1]
        dumped = _try_parse_and_dump(sliced)
        if dumped is not None:
            return dumped

    first_brace = candidate.find("{")
    last_brace = candidate.rfind("}")
    if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
        sliced = candidate[first_brace : last_brace + 1]
        dumped = _try_parse_and_dump(sliced)
        if dumped is not None:
            return dumped

    return "[]"


def coerce_result_to_json_text(result_obj: Any) -> str:
    try:
        if isinstance(result_obj, (list, dict)):
            return json.dumps(result_obj)
        if isinstance(result_obj, str):
            return extract_json_text(result_obj)

        # Common CrewOutput attributes
        for attr in ["raw", "raw_output", "output", "final_output", "json"]:
            if hasattr(result_obj, attr):
                value = getattr(result_obj, attr)
                if callable(value):
                    try:
                        value = value()
                    except Exception:
                        continue
                if isinstance(value, (list, dict)):
                    return json.dumps(value)
                if isinstance(value, str):
                    return extract_json_text(value)

        # to_json method
        if hasattr(result_obj, "to_json") and callable(getattr(result_obj, "to_json")):
            try:
                text = result_obj.to_json()
                return extract_json_text(text)
            except Exception:
                pass

        # Fallback: stringify and try
        return extract_json_text(str(result_obj))
    except Exception:
        return "[]"


def _guess_name_from_filename(file_name: str) -> str:
    try:
        import os
        base = os.path.splitext(os.path.basename(file_name or ""))[0]
        # Remove common words
        cleaned = base.replace("resume", "").replace("cv", "").strip(" -_.")
        cleaned = cleaned.replace("_", " ").replace("-", " ")
        # Collapse spaces
        cleaned = " ".join(w for w in cleaned.split() if w)
        # Title case
        return cleaned.title() if cleaned else base
    except Exception:
        return file_name


def normalize_candidates_json(json_text: str) -> str:
    try:
        data = json.loads(json_text)
    except Exception:
        return "[]"

    if not isinstance(data, list):
        return "[]"

    normalized: list[dict] = []
    for item in data:
        if not isinstance(item, dict):
            continue
        file_name = item.get("resource-file") or item.get("file") or ""
        name = item.get("resource-name")
        title = item.get("resource-job-title")
        skills = item.get("experties")

        if not name or (isinstance(name, str) and not name.strip()):
            if isinstance(file_name, str) and file_name:
                name = _guess_name_from_filename(file_name)
            else:
                name = "Unknown"

        if not isinstance(title, str):
            title = ""
        if not isinstance(skills, list):
            skills = []

        normalized.append({
            "resource-name": name,
            "resource-job-title": title,
            "experties": skills,
            "resource-file": file_name,
        })

    return json.dumps(normalized)


