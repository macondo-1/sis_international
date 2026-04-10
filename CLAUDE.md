# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Running the Project

This project uses [uv](https://docs.astral.sh/uv/) as its package manager with a workspace layout.

```bash
# Run any worker
uv run python database_worker.py
uv run python super_send_worker.py
uv run python smtp_worker.py
uv run python million_verifier_worker.py
uv run python bcc_bot_worker.py

# Run main utility scripts
uv run python main.py
```

## Cron Schedule (from notes.txt)

| Worker | Schedule |
|---|---|
| `super_send_worker.py` | `* * * * *` (every minute) |
| `million_verifier_worker.py` | `*/20 * * * *` (every 20 min) |

## Architecture Overview

This is a **multi-stage email outreach automation system** for SIS International research recruitment. The pipeline is:

```
CSV files (contacts)
  → [database_worker] ingests & deduplicates into SQLite
  → [super_send_worker] fetches quotas, sends via SuperSend API & queues MillionVerifier validation
  → [million_verifier_worker] polls completed validation jobs, updates DB with email validity
  → [smtp_worker] handles mail-merge campaigns via direct SMTP
  → [bcc_bot_worker] sends BCC emails via Selenium browser automation
```

### Key Design Patterns

- **File-based locking** — Workers write `.lock` files to prevent concurrent execution.
- **Quota management** — Daily/hourly send limits per project and per SMTP account, stored in `blasting_quotas` and `mailmerge_quotas` tables.
- **Async job tracking** — MillionVerifier jobs are created by `super_send_worker`, then polled separately by `million_verifier_worker`.
- **CSV filename convention** — Input files for `database_worker` use `{source}--{project_id}__{filename}.csv` to auto-associate records with a project.
- **Blast Master Excel** — Campaign templates, project metadata, and email copy live in a single Excel file (path defined in `modules/constants/main.py`).

### Module Responsibilities

| Module | Purpose |
|---|---|
| `modules/database` | All SQLite access (~34k lines). Central hub for every read/write. |
| `modules/constants` | All hardcoded paths, DB column names, SMTP config, API endpoints. |
| `modules/super_send` | REST wrapper for SuperSend.io API (bulk contact upload/management). |
| `modules/million_verifier_api` | REST wrapper for MillionVerifier bulk email validation API. |
| `modules/smtp_bot` | Direct SMTP sender (Office 365) with template rendering and quota tracking. |
| `modules/bcc_bot` | Selenium-based Gmail automation for BCC sending. |
| `modules/csv_tools` | CSV/Excel parsing, schema mapping, data cleaning before DB insert. |
| `modules/project_class` | `Project` dataclass — JSON-persisted project configuration and filter definitions. |

### Environment Variables (`.env`)

```
MV_API_KEY        # MillionVerifier API key
SS_API_KEY        # SuperSend.io API key
BCC_PASSWORD      # Passwords for BCC email accounts (multiple)
GODADDY_PASSWORD  # GoDaddy SMTP server password
```

### Database Tables (SQLite)

Core tables in `modules/database/database.py`:
- `recruits` / `project_recruits` — Contact records per project
- `projects` — Project metadata and campaign config
- `blasting_quotas` / `mailmerge_quotas` — Daily send limits
- `million_verifier_jobs` — Async validation job tracking
- `smtp_accounts` — SMTP credential pool with hourly/daily limits
- `surveys` / `survey_collectors` / `survey_responses` — Survey data

### `main.py`

Not a service — used for ad-hoc utility scripts: generating reports (Plotly/Matplotlib), exporting CSV queries, and bulk data operations. Edit and run sections as needed.
