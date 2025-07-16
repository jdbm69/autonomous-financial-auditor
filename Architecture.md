# Architecture Note: Autonomous Financial Auditor

## 🔢 Overview

This solution continuously monitors a GitHub repository containing financial reports (Balance Sheet and Quarterly P\&L) to detect inconsistencies between them using an AI agent powered by OpenAI's GPT-4.

## 🌐 Components

### 1. GitHub Repository

- Contains `balance.csv` and `quarterly.csv`
- Triggers GitHub Actions on every push to `main`
- Stores issue reports and automation logic

### 2. GitHub Actions (CI/CD)

- **Trigger**: Push to `main` or manual dispatch
- **Job**: Builds the Docker container and runs `run_auditor_beeai.py`
- **Workflows**:
  - `audit.yml`: Executes Python script natively
  - `docker-audit.yml`: Executes script inside Docker container

### 3. AI Auditor Service (BeeAI Agents)

- **Main Script**: `run_auditor_beeai.py`
- **Framework**: [beeai-framework](https://framework.beeai.dev/)
- **Workflow**:
  1. Reads CSVs
  2. Runs multi-agent BeeAI workflow:
     - `ReaderAgent`: Confirms document intake
     - `AuditorAgent`: Performs technical analysis
     - `ReportAgent`: Writes a professional summary
  3. Detects issues via keyword analysis
  4. Creates a GitHub Issue if needed

### 4. GitHub Issue Creator

* If problems are found, creates/updates a single issue on GitHub with the findings
* Avoids duplicates by checking open issue titles

### 5. Environment Configuration

* `.env` file with:

  * `OPENAI_API_KEY`
  * `GH_TOKEN`
  * `GH_REPO`
* Secrets configured in GitHub repo as environment variables (e.g., `GH_REPO`, `GH_TOKEN`)

## ⚠️ Failure Modes & Resilience

| Failure                 | Handling                              |
| ----------------------- | ------------------------------------- |
| OpenAI API fails        | Logs error, skips issue creation      |
| GitHub Token invalid    | Action fails with 401, caught in logs |
| Missing CSV files       | Script throws and fails early         |
| GPT prompt is malformed | Controlled via structured prompting   |

## ⇢ Scaling Path

* Add persistent storage for historical audits
* Move audit logic to an API service (FastAPI)
* Add async job queue for processing large files
* Replace file-based input with vector store or database for richer queries

## 🔄 Flow Diagram

┌──────────────┐        ┌────────────────────┐        ┌──────────────┐
│   Push to    ├──────➔│ GitHub Action Trigger │──────➔│  Docker Build │
│    main      │        └────────────────────┘        └─────────────┘
                                                       │
                                                       v
                                      ┌────────────────────────────┐
                                      │ run_auditor_beeai.py       │
                                      │ - load BeeAI agents        │
                                      │ - process balance + P&L    │
                                      │ - detect inconsistencies   │
                                      │ - post GitHub Issue if any │
                                      └────────────────────────────┘