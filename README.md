# RM Agent Helper

An intelligent resume analysis and job matching assistant built with CrewAI. This tool analyzes resumes and matches them against job profiles using AI agents to provide comprehensive insights

## Features

- **Resume Analysis**: Extracts key information from resumes (PDF, DOCX, TXT, MD)
- **Job Matching**: Matches resumes against job descriptions with percentage scores
- **Multiple Output Formats**: Generates both JSON and HTML reports
- **REST API**: FastAPI-based web service for programmatic access
- **Flexible Input**: Supports various document formats and structures

## Prerequisites

- Python 3.10–3.12
- macOS/Linux/Windows

## Installation

```bash
# Using uv (recommended)
uv sync

# Or using pip
pip install -e .
```

This installs the console script `rm_agent_helper`.

## Project Structure

```
rm_agent_helper/
├── api/                    # FastAPI web service
│   └── app/
│       ├── main.py        # FastAPI app and health endpoint
│       └── routers/
│           └── crew.py    # POST /crew/kickoff endpoint
├── knowledge/             # Input data directory
│   ├── resource-resume/   # Resume files (PDF, DOCX, TXT, MD)
│   └── job-profile/       # Job description files (TXT, MD)
├── output/               # Generated reports
│   ├── resource_report.json      # Resume analysis results
│   ├── resource_report.html      # Resume analysis HTML report
│   ├── job_match_report.json     # Job matching results
│   └── job_match_report.html     # Job matching HTML report
├── src/rm_agent_helper/   # Main application code
│   ├── config/           # Agent and task configurations
│   ├── tools/            # Custom tools for data extraction
│   └── main.py           # CLI entry point
└── tests/                # Test files
```

## Usage

### Command Line Interface

Run the complete analysis pipeline:

```bash
crewai run
# or
rm_agent_helper
```

This will:
1. Analyze all resumes in `knowledge/resource-resume/`
2. Match resumes against job profiles in `knowledge/job-profile/`
3. Generate comprehensive reports in the `output/` directory

### Input Data Preparation

#### Resumes
Place resume files in `knowledge/resource-resume/`:
- **Supported formats**: PDF, DOCX, TXT, MD
- **Example files included**: Various resume templates and formats

#### Job Profiles
Place job description files in `knowledge/job-profile/`:
- **Supported formats**: TXT, MD
- **Example files included**: Sample job descriptions

### Output Reports

The tool generates four types of reports:

#### 1. Resource Report (JSON)
`output/resource_report.json` - Extracted resume data:
```json
[
  {
    "resource-name": "Deepak Shanmugasundaram",
    "resource-job-title": "Senior Test Engineer",
    "experties": ["Automation", "Java", "Agile"],
    "resource-file": "Deepak Shanmugasundaram-Resume.pdf"
  }
]
```

#### 2. Resource Report (HTML)
`output/resource_report.html` - Visual resume analysis report

#### 3. Job Match Report (JSON)
`output/job_match_report.json` - Job matching results:
```json
[
  {
    "job-file": "job1.txt",
    "job-title": "Analyst/Consultant/Senior Consultant in T&T Team",
    "matches": [
      {
        "resource-file": "Deepak Shanmugasundaram-Resume.pdf",
        "resource-name": "Deepak Shanmugasundaram",
        "percent": 85
      }
    ]
  }
]
```

#### 4. Job Match Report (HTML)
`output/job_match_report.html` - Visual job matching report

## REST API

Run the API server for programmatic access:

```bash
uv run uvicorn api.app.main:app --host 0.0.0.0 --port 8000 --reload
```

### API Endpoints

#### Health Check
```bash
GET /healthz
```
Example:
```bash
curl http://127.0.0.1:8000/healthz
```

#### Start Analysis (Background)
```bash
POST /crew/kickoff
```
Returns immediately with output file paths. Analysis runs in background.
Example:
```bash
curl -X POST http://127.0.0.1:8000/crew/kickoff
```

## Configuration

### Agents Configuration
Edit `src/rm_agent_helper/config/agents.yaml` to customize:
- Agent roles and goals
- Analysis behavior
- Output formatting preferences

### Tasks Configuration
Edit `src/rm_agent_helper/config/tasks.yaml` to customize:
- Task descriptions and requirements
- Expected output formats
- Processing instructions

## Development

### Run Locally Without Installation
```bash
uv run python -m rm_agent_helper.main
# or
python -m rm_agent_helper.main
```

### Available Commands
- `rm_agent_helper` or `run_crew` - Run the main analysis
- `train` - Train the crew with custom iterations
- `replay` - Replay a specific task
- `test` - Test the crew with custom parameters

### Custom Tools
The application includes custom tools in `src/rm_agent_helper/tools/custom_tool.py`:
- `ResourceResumeAnalyzerTool` - Extracts text from various resume formats
- `JobProfileLoaderTool` - Loads job description files

## Dependencies

Key dependencies include:
- `crewai[tools]` - Core AI agent framework
- `pypdf` - PDF text extraction
- `python-docx`, `docx2txt`, `mammoth` - DOCX processing
- `fastapi`, `uvicorn` - Web API framework

