# Lab 6 — AI Agents

## Objective

Build and evaluate a local AI agent that can call tools, retain useful information in memory, retrieve answers from course documents, and connect to workflow and Google services.

## Portfolio layout

```text
Lab-06-AI-Agents/
├── README.md
├── agent.py
├── requirements.txt
├── .env.example
├── lab6_agent/          # Agent tools, SQLite memory, RAG, and Google integrations
├── notebooks/           # Guided demo notebook
├── screenshots/         # Screenshots added after interactive runs
├── data/
│   ├── knowledge_base/  # Add approved, selectable-text university PDFs here
│   └── generated/       # Local generated files; runtime data is ignored by Git
└── tests/               # Automated checks for core tools and routing
```

## Practical tasks

- Use `llama3.2:3b` through Ollama and a LangChain agent.
- Add calculator, Colombo date/time, Notepad, file search/create, and system-information tools.
- Add persistent SQLite memory and a memory-search tool.
- Reuse the Lab 5 retrieval pipeline for document-grounded answers.
- Provide Google Calendar, Sheets, Docs, and Gmail integrations, with confirmation before write/send actions.
- Include an n8n workflow using a local Ollama model, memory, and Google Calendar tools.
- Outline the final university assistant workflow combining RAG and the Google services.

## Run locally

1. Install Ollama and download the model with `ollama pull llama3.2:3b`.
2. Install Python dependencies with `python -m pip install -r requirements.txt`.
3. Copy `.env.example` to `.env` and adjust settings if needed.
4. Start Ollama, then run `python agent.py` from this folder.
5. For RAG, add approved university/course PDFs to `data/knowledge_base/`. Answers are based on those local documents and include source labels.
6. For Google tools, create an OAuth desktop client in Google Cloud, save it as `credentials.json` in this folder, and authorize the account when prompted. Credentials and tokens are excluded from Git.

The guided notebook is [notebooks/lab06_ai_agents.ipynb](notebooks/lab06_ai_agents.ipynb). Automated checks can be run with `python -m unittest discover -s tests -v`.

## Progress and limits

The Python agent, local tools, SQLite memory, Lab 5 RAG adapter, and Google integration code are included. The automated suite passes (18 tests). A local smoke run returned `100` for `Calculate 25 × 4`, returned the current Asia/Colombo time, saved and recalled the demo name `Alex`, created a safe test file, and reported this machine's Windows/CPU/memory details. Searching the Lab 6 folder returned no PDFs, as expected. A real retrieval check against the supplied Lab Sheet 6 PDF successfully located the Part B tool description; that handout is only a retrieval test and is **not** an institutional university knowledge base.

Live Google Calendar/Sheets/Docs/Gmail operations require the user's OAuth setup and have not been verified against a Google account. Docker is not installed in the current environment, so the n8n workflow has not been run. Interactive Windows Calculator/Notepad actions have not been executed; add screenshots only after those interactive steps have actually been performed. The worksheet's example directory `D:\MSC AI` does not exist on this computer, so its requested PDF search and file-creation examples must be repeated on a machine that has that directory.

The computer-shop `D:\MSC AI` paths in the worksheet are example paths from the lab handout. File creation is sandboxed to `data/generated/` so the agent cannot overwrite arbitrary files; file search can be restricted with `LAB6_ALLOWED_SEARCH_ROOTS` in `.env`.
