import json
import os
from typing import Any, Dict, List


def _html_escape(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#39;")
    )


def _render_skill_badges(skills: List[str]) -> str:
    if not skills:
        return ""
    badges = []
    for skill in skills:
        skill_text = _html_escape(str(skill))
        badges.append(
            f'<span class="badge" title="{skill_text}">{skill_text}</span>'
        )
    return "\n".join(badges)


def _render_candidate_card(candidate: Dict[str, Any]) -> str:
    name = candidate.get("resource-name") or candidate.get("name") or "Unknown"
    title = candidate.get("resource-job-title") or candidate.get("title") or ""
    file_name = candidate.get("resource-file") or ""
    skills = candidate.get("experties") or candidate.get("skills") or []

    name_html = _html_escape(str(name))
    title_html = _html_escape(str(title))
    file_html = _html_escape(str(file_name))

    meta = []
    if file_name:
        meta.append(f"<span class=\"file\" title=\"{file_html}\">{file_html}</span>")
    meta_html = " &middot; ".join(meta)

    skills_html = _render_skill_badges(skills if isinstance(skills, list) else [])

    return f"""
    <article class=\"card\">
      <div class=\"card-header\">
        <h3 class=\"name\">{name_html}</h3>
        <div class=\"title\">{title_html}</div>
        <div class=\"meta\">{meta_html}</div>
      </div>
      <div class=\"skills\">{skills_html}</div>
    </article>
    """


def generate_html_report(json_input_path: str, html_output_path: str) -> None:
    os.makedirs(os.path.dirname(html_output_path), exist_ok=True)

    try:
        with open(json_input_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        data = []

    # Normalize: accept either the final structured array or raw tool output
    candidates: List[Dict[str, Any]]
    if isinstance(data, list) and data and isinstance(data[0], dict) and (
        "resource-name" in data[0] or "experties" in data[0]
    ):
        candidates = data  # Already structured
    elif isinstance(data, list) and data and isinstance(data[0], dict) and (
        "resource-file" in data[0] and "text" in data[0]
    ):
        # Fallback: show files even if the analysis didn't run
        candidates = [
            {
                "resource-name": os.path.splitext(item.get("resource-file", "Unknown"))[0],
                "resource-job-title": "",
                "experties": [],
                "resource-file": item.get("resource-file", ""),
            }
            for item in data
        ]
    else:
        candidates = []

    total = len(candidates)

    cards_html = "\n".join(_render_candidate_card(c) for c in candidates)

    # CBA-inspired palette (gold/black with neutrals)
    # --cba-gold: #FFCC00; --cba-black: #000000; greys for backgrounds and borders
    html = f"""
<!DOCTYPE html>
<html lang=\"en\">
<head>
  <meta charset=\"UTF-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>Resource Report</title>
  <style>
    :root {{
      --cba-gold: #FFCC00;
      --cba-black: #000000;
      --cba-dark: #1f1f1f;
      --cba-grey-1: #f7f7f7;
      --cba-grey-2: #eaeaea;
      --cba-grey-3: #8c8c8c;
      --cba-white: #ffffff;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Helvetica, Arial, sans-serif;
      color: var(--cba-dark);
      background: var(--cba-grey-1);
      line-height: 1.5;
    }}
    header {{
      background: linear-gradient(90deg, var(--cba-gold), #ffd84d);
      color: var(--cba-black);
      padding: 24px 16px;
      border-bottom: 4px solid var(--cba-black);
    }}
    header .title {{
      display: flex;
      align-items: center;
      gap: 12px;
      font-size: 20px;
      font-weight: 700;
    }}
    header .count {{
      margin-top: 4px;
      color: var(--cba-black);
      opacity: 0.85;
      font-weight: 600;
    }}
    main {{
      max-width: 1100px;
      margin: 24px auto;
      padding: 0 16px 48px;
    }}
    .grid {{
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
      gap: 16px;
    }}
    .card {{
      background: var(--cba-white);
      border: 1px solid var(--cba-grey-2);
      border-radius: 10px;
      box-shadow: 0 2px 0 rgba(0,0,0,0.06);
      padding: 16px;
    }}
    .card-header {{
      border-left: 6px solid var(--cba-gold);
      padding-left: 12px;
      margin-bottom: 12px;
    }}
    .name {{
      margin: 0 0 2px 0;
      font-size: 18px;
      color: var(--cba-black);
    }}
    .title {{
      font-size: 14px;
      color: var(--cba-dark);
      opacity: 0.9;
    }}
    .meta {{
      margin-top: 6px;
      font-size: 12px;
      color: var(--cba-grey-3);
    }}
    .skills {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
    }}
    .badge {{
      background: var(--cba-grey-1);
      border: 1px solid var(--cba-grey-2);
      border-radius: 999px;
      padding: 6px 10px;
      font-size: 12px;
      color: var(--cba-dark);
    }}
    footer {{
      text-align: center;
      color: var(--cba-grey-3);
      font-size: 12px;
      padding: 24px 16px;
    }}
    .empty {{
      margin-top: 24px;
      color: var(--cba-grey-3);
      font-style: italic;
    }}
  </style>
  <meta name=\"theme-color\" content=\"#FFCC00\" />
</head>
<body>
  <header>
    <div class=\"title\">Resource Report</div>
    <div class=\"count\">{total} candidate{'' if total == 1 else 's'}</div>
  </header>
  <main>
    {'' if total else '<div class="empty">No candidates found. Ensure resumes are present and analysis has run.</div>'}
    <section class=\"grid\">
      {cards_html}
    </section>
  </main>
  <footer>Generated by rm_agent_helper</footer>
  </body>
</html>
"""

    with open(html_output_path, "w", encoding="utf-8") as f:
        f.write(html)


