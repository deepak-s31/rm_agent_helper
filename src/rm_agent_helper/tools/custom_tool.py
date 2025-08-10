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


def _extract_text_from_docx(docx_path: str) -> str:
    # 1) Try python-docx
    try:
        import docx  # python-docx
        try:
            document = docx.Document(docx_path)
            parts: List[str] = []
            for p in document.paragraphs:
                text = (p.text or "").strip()
                if text:
                    parts.append(text)
            for table in getattr(document, "tables", []) or []:
                for row in table.rows:
                    for cell in row.cells:
                        cell_text = (cell.text or "").strip()
                        if cell_text:
                            parts.append(cell_text)
            content = "\n".join(parts).strip()
            if content:
                return content
        except Exception:
            pass
    except Exception:
        pass

    # 2) Fallback to docx2txt
    try:
        import docx2txt
        try:
            content = (docx2txt.process(docx_path) or "").strip()
            if content:
                return content
        except Exception:
            pass
    except Exception:
        pass

    # 3) Fallback to mammoth (HTML → text)
    try:
        import mammoth
        try:
            with open(docx_path, "rb") as f:
                result = mammoth.convert_to_html(f)
                html = (result.value or "").strip()
                if html:
                    # Strip tags very simply
                    import re
                    text = re.sub(r"<[^>]+>", "\n", html)
                    text = re.sub(r"\n+", "\n", text)
                    text = text.strip()
                    if text:
                        return text
        except Exception:
            pass
    except Exception:
        pass

    return ""


class ResourceResumeAnalyzerTool(BaseTool):
    name: str = "Resource Resume Analyzer"
    description: str = (
        "Loads .txt/.md/.pdf/.docx resumes from knowledge/resource-resume and returns a JSON array of objects "
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
            if (
                lower.endswith(".txt")
                or lower.endswith(".pdf")
                or lower.endswith(".md")
                or lower.endswith(".docx")
            ):
                resource_files.append(f)

        loaded_resumes: List[dict] = []

        for resource_file in resource_files:
            resource_path = os.path.join(resource_resume_dir, resource_file)
            resource_content = ""
            try:
                lower_name = resource_file.lower()
                if lower_name.endswith(".pdf"):
                    resource_content = _extract_text_from_pdf(resource_path)
                elif lower_name.endswith(".docx"):
                    resource_content = _extract_text_from_docx(resource_path)
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


class JobProfileLoaderTool(BaseTool):
    name: str = "Job Profile Loader"
    description: str = (
        "Loads .txt/.md job profiles from knowledge/job-profile and returns a JSON array "
        "of objects with fields: job-file, text."
    )

    def _run(self) -> str:
        job_profile_dir = os.path.join("knowledge", "job-profile")
        if not os.path.isdir(job_profile_dir):
            return json.dumps([], indent=2)

        job_files: List[str] = []
        for f in os.listdir(job_profile_dir):
            path = os.path.join(job_profile_dir, f)
            if not os.path.isfile(path):
                continue
            lower = f.lower()
            if lower.endswith(".txt") or lower.endswith(".md"):
                job_files.append(f)

        loaded_jobs: List[dict] = []
        for job_file in job_files:
            job_path = os.path.join(job_profile_dir, job_file)
            content = ""
            try:
                with open(job_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
            except Exception:
                content = ""
            loaded_jobs.append({"job-file": job_file, "text": (content or "").strip()})

        return json.dumps(loaded_jobs, indent=2)
