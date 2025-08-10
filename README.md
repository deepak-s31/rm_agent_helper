## rm_agent_helper

Resume analysis assistant built with CrewAI. It scans resumes under `knowledge/resource-resume/`, runs an agentic extraction, and produces:

- **Consolidated JSON**: `output/resource_report.json`
- **HTML report (CBA-inspired palette)**: `output/resource_report.html`

### Prerequisites

- Python 3.10–3.12
- macOS/Linux/Windows

### Installation

```bash
# from the project root
uv sync  # or: pip install -e .
```

If you do not use `uv`, install via pip:

```bash
pip install -e .
```

This installs the console script `rm_agent_helper`.

### Prepare input resumes

Place resumes in `knowledge/resource-resume/` as `.pdf`, `.txt`, or `.md` files. Example already included.

### Run

```bash
crewai run
```

This will:

- Run the crew and write the consolidated JSON to `output/resource_report.json`
- Generate an HTML report at `output/resource_report.html`

Example output structure:

```json
[
  {
    "resource-name": "Jane Doe",
    "resource-job-title": "Senior Data Scientist",
    "experties": ["Python", "ML", "NLP"],
    "resource-file": "Jane_Doe_Resume.pdf"
  }
]
```

If the agent fails to run, the app still creates an empty JSON array and an HTML shell so you can verify the pipeline.

### FastAPI API

Run the API server to trigger the crew over HTTP.

```bash
uv run uvicorn api.app.main:app --host 0.0.0.0 --port 8000 --reload
```

- **Health check**
  - `GET /healthz`
  - Example:
    ```bash
    curl http://127.0.0.1:8000/healthz
    ```

- **Kickoff crew (runs in background)**
  - `POST /crew/kickoff`
  - Returns immediately with paths to outputs.
  - Example:
    ```bash
    curl -X POST http://127.0.0.1:8000/crew/kickoff
    ```

API outputs are written to:
- `output/resource_report.json`
- `output/resource_report.html`

API folder structure:

```
api/
  app/
    main.py            # FastAPI app and health endpoint
    routers/
      crew.py          # POST /crew/kickoff endpoint
```

### Configuration

- Agents: `src/rm_agent_helper/config/agents.yaml`
- Tasks: `src/rm_agent_helper/config/tasks.yaml`

Edit these to adjust prompts, fields, and behavior.

### Development

Run locally without install:

```bash
uv run python -m rm_agent_helper.main
# or
python -m rm_agent_helper.main
```

### Troubleshooting

- No output / empty report: ensure resumes are present in `knowledge/resource-resume/` and are readable. PDFs are parsed with `pypdf`.
- If PDFs have no extractable text (scans), convert them to searchable PDFs or provide `.txt` versions.

### License

MIT

