import os
import json
from typing import Any, Dict, List


def _html_escape(text: str) -> str:
    return (
        str(text)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#39;")
    )


def generate_job_match_html_report(job_json_input_path: str, html_output_path: str) -> None:
    os.makedirs(os.path.dirname(html_output_path), exist_ok=True)

    try:
        with open(job_json_input_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        data = []

    jobs: List[Dict[str, Any]] = data if isinstance(data, list) else []

    sections: List[str] = []
    for job in jobs:
        if not isinstance(job, dict):
            continue
        job_title = _html_escape(job.get("job-title") or job.get("job_file") or job.get("job-file") or "Job")
        matches = job.get("matches") if isinstance(job, dict) else []
        if not isinstance(matches, list):
            matches = []

        bars: List[str] = []
        for m in matches:
            if not isinstance(m, dict):
                continue
            name = _html_escape(m.get("resource-name") or m.get("resource_file") or m.get("resource-file") or "Unknown")
            try:
                width = max(0, min(100, int(m.get("percent", 0))))
            except Exception:
                width = 0
            bars.append(
                f'<div class="bar"><div class="bar-fill" style="width:{width}%"></div><div class="bar-label">{name} — {width}%</div></div>'
            )

        sections.append(
            f"""
            <section class=\"job\">
              <h3 class=\"job-title\">{job_title}</h3>
              <div class=\"bars\">{''.join(bars)}</div>
            </section>
            """
        )

    body_html = "\n".join(sections) if sections else '<div class="empty">No job matches found. Ensure job profiles and resumes are present.</div>'

    html = f"""
<!DOCTYPE html>
<html lang=\"en\">
<head>
  <meta charset=\"UTF-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>Job Match Report</title>
  <style>
    :root {{
      --gold: #FFCC00;
      --black: #000000;
      --grey-1: #f7f7f7;
      --grey-2: #eaeaea;
      --grey-3: #8c8c8c;
      --white: #ffffff;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Helvetica, Arial, sans-serif;
      color: #1f1f1f;
      background: var(--grey-1);
      line-height: 1.5;
    }}
    header {{
      background: linear-gradient(90deg, var(--gold), #ffd84d);
      color: var(--black);
      padding: 24px 16px;
      border-bottom: 4px solid var(--black);
    }}
    main {{
      max-width: 1000px;
      margin: 24px auto;
      padding: 0 16px 48px;
    }}
    .job {{
      background: var(--white);
      border: 1px solid var(--grey-2);
      border-radius: 10px;
      box-shadow: 0 2px 0 rgba(0,0,0,0.06);
      padding: 16px;
      margin-bottom: 16px;
    }}
    .job-title {{
      margin: 0 0 12px 0;
      font-size: 18px;
      color: var(--black);
    }}
    .bar {{
      position: relative;
      background: var(--grey-2);
      border-radius: 8px;
      height: 28px;
      margin: 8px 0;
      overflow: hidden;
    }}
    .bar-fill {{
      background: var(--gold);
      height: 100%;
      width: 0;
      transition: width 0.6s ease;
    }}
    .bar-label {{
      position: absolute;
      inset: 0;
      display: flex;
      align-items: center;
      padding: 0 10px;
      font-size: 13px;
      color: #1f1f1f;
      font-weight: 600;
    }}
    .empty {{
      margin-top: 24px;
      color: var(--grey-3);
      font-style: italic;
    }}
  </style>
  <meta name=\"theme-color\" content=\"#FFCC00\" />
  <script>
    window.addEventListener('load', () => {{
      document.querySelectorAll('.bar-fill').forEach(el => {{
        const width = el.style.width;
        el.style.width = '0%';
        requestAnimationFrame(() => {{ el.style.width = width; }});
      }});
    }});
  </script>
  </head>
  <body>
    <header>
      <div class=\"title\">Job Match Report</div>
    </header>
    <main>
      {body_html}
    </main>
  </body>
  </html>
  """

    with open(html_output_path, "w", encoding="utf-8") as f:
        f.write(html)


