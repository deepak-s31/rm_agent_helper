from __future__ import annotations

import json
import os
from typing import Any, Dict, List


def load_resume_texts() -> dict[str, str]:
    base_dir = os.path.join("knowledge", "resource-resume")
    texts: dict[str, str] = {}
    try:
        for file_name in os.listdir(base_dir):
            path = os.path.join(base_dir, file_name)
            if not os.path.isfile(path):
                continue
            try:
                with open(path, "r", encoding="utf-8", errors="ignore") as f:
                    texts[file_name] = f.read()
            except Exception:
                texts[file_name] = ""
    except Exception:
        pass
    return texts


def enrich_candidates(candidates: List[Dict[str, Any]], texts: dict[str, str]) -> List[Dict[str, Any]]:
    enriched: List[Dict[str, Any]] = []
    for item in candidates:
        if not isinstance(item, dict):
            continue
        # For now, passthrough without heavy enrichment to keep API responsive.
        enriched.append(item)
    return enriched


