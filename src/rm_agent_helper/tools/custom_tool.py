import os
import json
from typing import List, Optional
from crewai.tools import BaseTool


def _extract_text_from_pdf(pdf_path: str) -> str:
    try:
        from pypdf import PdfReader
    except Exception:
        return ""

    try:
        reader = PdfReader(pdf_path)
        text_parts: List[str] = []
        for page in reader.pages:
            try:
                page_text: Optional[str] = page.extract_text()
            except Exception:
                page_text = None
            if page_text:
                text_parts.append(page_text)
        return "\n".join(text_parts)
    except Exception:
        return ""


class ResourceResumeAnalyzerTool(BaseTool):
    name: str = "Resource Resume Analyzer"
    description: str = (
        "Loads .txt/.md/.pdf resumes from knowledge/resource-resume and returns a JSON array of objects "
        "with fields: resource-file, text. The agent should extract details and format the final JSON."
    )

    def _run(self) -> str:
        resource_resume_dir = os.path.join("knowledge", "resource-resume")
        if not os.path.isdir(resource_resume_dir):
            return json.dumps([], indent=2)

        resource_files: List[str] = []
        for f in os.listdir(resource_resume_dir):
            path = os.path.join(resource_resume_dir, f)
            if not os.path.isfile(path):
                continue
            lower = f.lower()
            if lower.endswith(".txt") or lower.endswith(".pdf") or lower.endswith(".md"):
                resource_files.append(f)

        loaded_resumes: List[dict] = []

        for resource_file in resource_files:
            resource_path = os.path.join(resource_resume_dir, resource_file)
            resource_content = ""
            try:
                if resource_file.lower().endswith(".pdf"):
                    resource_content = _extract_text_from_pdf(resource_path)
                else:
                    with open(resource_path, "r", encoding="utf-8", errors="ignore") as f:
                        resource_content = f.read()
            except Exception:
                resource_content = ""

            resource_content = (resource_content or "").strip()

            loaded_resumes.append({
                "resource-file": resource_file,
                "text": resource_content,
            })

        return json.dumps(loaded_resumes, indent=2)
