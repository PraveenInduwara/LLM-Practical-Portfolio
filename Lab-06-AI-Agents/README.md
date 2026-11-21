# Lab 6 — AI Agents (Lab Sheet pages 1–5)

## Objective

Build a local Ollama agent that uses a calculator and practical tools, add SQLite memory and Lab 5 RAG, then connect tools for reading and creating Google Calendar events.

## Portfolio layout

```text
Lab-06-AI-Agents/
├── README.md
├── agent.py
├── requirements.txt
├── .env.example
├── lab6_agent/          # Calculator, local tools, SQLite memory, RAG, Calendar
├── notebooks/           # Guided demo notebook
├── screenshots/         # Evidence screenshots from interactive runs
├── data/
│   ├── knowledge_base/  # Selectable-text university/course PDFs for RAG
│   └── generated/       # Default safe location for generated text files
└── tests/               # Automated checks for tools and routing
```

## Tasks covered

1. **Calculator agent:** use `llama3.2:3b` through Ollama and LangChain; arithmetic is evaluated safely and Windows Calculator display is attempted when enabled.
2. **Multiple tools:** Asia/Colombo date and time, Notepad text entry, read-only file search, text-file creation, and OS/processor/memory information.
3. **Memory:** persistent SQLite conversation/fact store and a memory-search tool.
4. **RAG:** adapter to the Lab 5 PDF extraction, hierarchical indexing, and retrieval, with source/page labels.
5. **Google Calendar:** read today's schedule and create an event only after explicit interactive approval.

## Page-by-page verification status

| Worksheet page | Objective | Evidence and status |
| --- | --- | --- |
| 1 | Ollama calculator agent | **Partially verified:** the real `llama3.2:3b` model called the calculator tool and returned `100` for `25 * 4`. The visible Windows Calculator UI path has automated mock coverage, but was not verified in a persistent desktop window. |
| 2 | Date/time, Notepad, file search/create, computer specifications | **Partially verified:** date/time, PDF filename search, allowlisted text-file creation, and system details returned real local results in a temporary workspace. Notepad typing has mock coverage only. The exact `D:\MSC AI` examples cannot run here because this machine has no `D:` drive; the notebook contains them for a machine where that folder exists. |
| 3 | SQLite memory and recall of Alex | **Verified locally:** the agent saved `Alex` and answered “What is my name?” with “Your name is Alex.” |
| 4 | Calculator, memory search, and Lab 5 RAG | **Verified against the available Lab 5 course handout:** a group-task question returned a relevant answer with source label `[S1]`. This is not a check against an institution-specific handbook. |
| 5 | Google Calendar today view and event creation | **Implemented; live access unverified:** mocked API checks cover today's Asia/Colombo time window, event creation, and approval. A live run needs your Google Cloud project, enabled Calendar API, Desktop OAuth client JSON, and account authorization. |

The Calendar integration uses OAuth because it acts on a user's calendar. Google documents the required OAuth scopes for [listing events](https://developers.google.com/workspace/calendar/api/v3/reference/events/list) and [creating events](https://developers.google.com/workspace/calendar/api/v3/reference/events/insert). Setup follows Google's [Python Calendar quickstart](https://developers.google.com/workspace/calendar/api/quickstart/python): enable the Calendar API, configure the OAuth consent screen, create a Desktop app OAuth client, and save its downloaded JSON as `credentials.json` in this folder. The first run opens Google's authorization flow and stores a local token, which is gitignored. A plain API key is not used by this user-calendar read/write flow.

## Run locally

1. Install Ollama and download the model: `ollama pull llama3.2:3b`.
2. Install dependencies: `python -m pip install -r requirements.txt`.
3. Copy `.env.example` to `.env`; set allowed folders for file search/write if required.
4. Start Ollama, then run `python agent.py` from this directory.
5. Add selectable-text university/course PDFs to `data/knowledge_base/` for RAG. Responses cite retrieved passages as `[S#]` with source and page.
6. For Calendar, create a Google Desktop OAuth client JSON, save as `credentials.json` here, then authorize when first prompted. OAuth tokens and credentials are ignored by Git.

The guided notebook is [notebooks/lab06_ai_agents.ipynb](notebooks/lab06_ai_agents.ipynb). Automated checks: `python -m unittest discover -s tests -v`.

## Verified results and limitations

The automated suite passes **25 tests** covering arithmetic, safe file operations, date/time, SQLite memory, mocked Calculator/Notepad UI actions, RAG fallback behavior, and mocked Calendar API reads/creates and approval checks. Regression tests verify that a request for today's Calendar events reaches the Calendar tool rather than the date tool, and that event-creation requests remain on the approval-gated model path. The live local model check confirmed that `llama3.2:3b` called the calculator tool and returned `100` for `25 * 4`.

A local smoke run on 2026-11-21 returned the Colombo timestamp, saved and recalled the demo name `Alex`, found a temporary sample PDF, created `test.txt` only in an allowlisted temporary folder, and returned OS/processor/memory information. The end-to-end RAG check used the existing Lab 5 course handout and answered: “The group task is to investigate, design, implement, and evaluate an advanced RAG architecture that improves at least one limitation of the existing university RAG system” with citation `[S1]`. A separate retrieval check located the Lab Sheet 6 Part B tools on page 3. These are course-handout checks, not evidence against an institution-specific handbook.

The worksheet's example folder `D:\MSC AI` is absent on this computer. Its exact PDF-search and file-create examples therefore cannot be completed here; file search reports the missing directory, and file creation requires the requested folder to exist and be listed in `LAB6_ALLOWED_WRITE_ROOTS`. Without a requested destination, new text files are safely written to `data/generated/`, and existing files are never overwritten.

Google Calendar live access still requires your OAuth client and account authorization; the API behavior was tested with mocks only. The notebook now contains an optional pages 1–5 Calendar exercise for listing today's events and creating a sample event after typing `APPROVE`. Calculator and Notepad UI actions were tested with mocks, not a visible desktop run. The repository root `agent.py` provided as a reference was empty, so implementation was checked against Lab Sheet 6 pages 1–5 and the existing Lab 5 RAG module.
