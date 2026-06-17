# AGENTS.md

This file contains instructions, context, and conventions for AI coding agents working in the **vesalius** repository.

You are working alongside an IT professional who is learning to direct AI agents. They will describe what they want in plain language. You write, edit, test, and explain the code. Keep your explanations clear and avoid jargon unless you define it.

## Current Objective

Build a Python script, guided by the user's instructions, that:
- Reads Freshdesk credentials from `~\.freshdesk\api.key`
- Connects to the Freshdesk REST API
- Creates a new support ticket based on user-provided input

## Technology Stack

- **Language**: Python 3.11+
- **Key Libraries**: `requests`, `python-dotenv`, `pydantic`
- **Tools**: Git, PowerShell, PyCharm
- **Environment**: Windows 11


## SECURITY & COMPLIANCE - HIGHEST PRIORITY RULES
These rules are non-negotiable and must be followed in every response, every action, and every code change.

**NEVER reveal, output, log, or include in any code:**
- API keys
- Passwords
- Tokens
- Credentials
- Any secrets

When the user asks to view credentials (e.g. `--creds` flag), **always mask** the API key (show only the last 4 characters or "********").

**Before any Git commit or push:**
- Always run a full scan of the repository for credentials, HIPAA ePHI, PHI, PII, patient data, internal configs, logs, screenshots, or sensitive information.
- Use this exact prompt/check before every commit:
  > "Check the entire repo for credentials, API keys, HIPAA, PHI, PII, secrets, or any protected health information before committing. List anything found. If clean, proceed."

**If anything sensitive is detected:**
- Do not commit.
- Alert the user immediately and suggest remediation.

**Data Handling Rules (HIPAA / NIST / Zero Trust / Joint Commission):**
- Never allow ePHI, patient information, clinical data, screenshots from production systems, logs containing identifiers, or internal configs to be sent to the AI, included in prompts, or checked into GitHub.
- Assume anything provided to the AI may leave the local system unless proven otherwise.
- Credentials must be read from `~\.freshdesk\api.key` (Windows) or equivalent — never hard-coded.
- Never push .env files or files containing real secrets.

## Directory Rules

Source code, project-related material that can safely be checked into GitHub belongs in:

- **`c:\dev\apps\${project}`**

Logging, data, databases, output, and sensitive information belong outside the repository:

- **`c:\dev\out\${project}`**

Never commit files from `c:\dev\out\` to the repository.

## File Structure

```
vesalius/
├── README.md              # Project overview (public)
├── AGENTS.md              # AI agent instructions (this file)
├── .env.example           # Template for environment variables (committed)
├── .gitignore             # Exclusion rules
├── requirements.txt       # Python dependencies
│
├── agents/                # Agent source code
│   ├── __init__.py
│   ├── freshdesk_agent.py # Freshdesk ticket agent
│   └── base_agent.py      # Shared agent base class
│
├── config/                # Config files, schemas, API specs
│   └── freshdesk.yaml     # Freshdesk API configuration
│
├── tests/                 # Test files (mirrors agents/)
│   ├── __init__.py
│   ├── test_freshdesk_agent.py
│   └── conftest.py
│
└── docs/                  # Training docs, tutorials, guides
    └── PRE_DEV.md         # Pre-development environment setup
```

- New agents go in `agents/`. Each agent is a single module with a clear `main()` entry point.
- Config files go in `config/`. Do not hard-code API endpoints, keys, or credentials.
- Tests mirror the structure of `agents/`. Every agent must have at least one test.
- `docs/` holds training materials and guides. Do not put training content in the repo root.

## Freshdesk Agent Specification

### API Connection

- Use the **Freshdesk REST API v2** (`https://{company}.freshdesk.com/api/v2/`)
- Authentication: **API key** passed in the `Authorization` header as `Basic {base64(api_key:x)}`
- The API key comes from the environment variable `FRESHDESK_API_KEY`
- The company domain comes from `FRESHDESK_DOMAIN`
- Both are loaded from `.env` via `python-dotenv`

### Ticket Query

- Endpoint: `GET /api/v2/tickets`
- Filter for **open** tickets: `status=2` (Open) or `status=3` (Pending) — both are considered "active"
- Sort by `created_at` descending (newest first)
- Limit results to **50** per request
- Request fields: `id`, `subject`, `status`, `priority`, `requester_name`, `created_at`, `updated_at`

### Output Format

- Print a **Markdown-formatted summary** to stdout
- Group tickets by status (Open vs Pending)
- Each ticket shows: ID, Subject, Requester, Priority, Age (hours/days since creation)
- Include a total count at the top: `"Found {N} active tickets"`

### Error Handling

- If the API key is missing, exit with code `1` and a clear message: `"FRESHDESK_API_KEY is not set"`
- If the domain is missing, exit with code `1` and a clear message: `"FRESHDESK_DOMAIN is not set"`
- If the API returns a non-2xx status, print the error body and exit with code `1`
- On network errors (timeout, DNS failure, connection refused), retry **once** after a 3-second delay, then print the error and exit with code `1`
- Use `pydantic` models to validate the API response structure before processing

## Git Workflow

- Branch naming: `codex/short-description` (e.g., `codex/freshdesk-agent`)
- Commit messages follow the format: `<type>: <description>`
  - `feat:` — new agent or feature
  - `fix:` — bug fix
  - `docs:` — documentation change
  - `test:` — test addition or fix
  - `chore:` — tooling, config, housekeeping
- Small, focused commits. One logical change per commit.
- No force pushes on shared branches.

## Coding Standards & Conventions

### General
- Use **clear, readable code** with excellent comments
- Prefer explicit over implicit
- Follow PEP 8 with slight flexibility for clarity
- All new code must be **git-friendly** (small, logical commits)
- Type hints on all function signatures and class attributes
- Docstrings on every module, class, and public method (Google style)

### Security
- Never commit API keys, tokens, passwords, or credentials
- All secrets must come from environment variables
- Commit `.env.example` as a template; never commit `.env`
- Ensure `.gitignore` excludes `*.env`, `__pycache__/`, `.pytest_cache/`, and `c:\dev\out\`
- Use `pydantic` for input validation — never trust external data

### Logging
- Use Python's built-in `logging` module, never `print()` for diagnostic output
- Set a default log level of `INFO` in `__main__`; allow override via `LOG_LEVEL` env var
- Logs go to `c:\dev\out\${project}/logs/` (not the repo)
- Log structure: `[timestamp] [level] [module] message`

### Testing
- Use `pytest` as the test framework
- Place tests in `tests/` mirroring the `agents/` structure
- Every agent must have at least one integration test and one unit test
- Use `pytest` fixtures for shared setup (mock Freshdesk responses)
- Mock the network layer in unit tests — no real API calls in CI
