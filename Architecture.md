# Architecture Note: Autonomous Financial Auditor

## 🔢 Overview

This solution continuously monitors a GitHub repository containing financial reports (Balance Sheet and Quarterly P\&L) to detect inconsistencies between them using an AI agent powered by OpenAI's GPT-4.

## 🌐 Components

### 1. GitHub Repository

* Contains `balance.csv` and `quarterly.csv`
* Triggers GitHub Actions on every push to `main`

### 2. GitHub Actions (CI/CD)

* Trigger: `on.push` to main or manual dispatch
* Job: Builds Docker container and runs the `run_auditor.py` script

### 3. AI Auditor Service (Python)

* Reads CSV files from the repo
* Sends them to GPT-4 via OpenAI API
* Analyzes for:

  * Accounting discrepancies
  * Net income vs retained earnings
  * Missing depreciation or loan payments

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

```text
┌──────────────┐        ┌────────────────────┐        ┌──────────────┐
│   Push to    ├──────➔│ GitHub Action Trigger │──────➔│  Docker Build │
│    main      │        └────────────────────┘        └─────────────┘
     
                                                   │
                                                   v
                                      ┌────────────────────────┐
                                      │   run_auditor.py       │
                                      │ - read CSVs            │
                                      │ - GPT-4 comparison     │
                                      │ - create issue if needed│
                                      └─────────────────────┘
```
