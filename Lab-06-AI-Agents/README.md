# Lab 6 — AI Agents (Lab Sheet pages 1–5)

## Objective

Build a tool-using local AI agent with Ollama. The work follows the Lab Sheet through page 5 only: a calculator agent, practical tools, SQLite memory, Lab 5 RAG, and Google Calendar read/create tools.

## Project structure

```text
Lab-06-AI-Agents/
├── README.md
├── agent.py
├── requirements.txt
├── .env.example
├── lab6_agent/
│   ├── tools.py               # Calculator, date/time, file, Notepad, system info
│   ├── memory.py              # SQLite conversation and fact memory
│   ├── rag.py                 # Lab 5 hierarchical retrieval adapter
│   └── google_integrations.py # Google Calendar read/create and approval
├── notebooks/
│   └── lab06_ai_agents.ipynb  # Guided run-through
├── results/
│   └── verification-results.md
├── screenshots/               # Optional visual evidence
├── data/
│   ├── knowledge_base/        # Add selectable-text course/university PDFs here
│   └── generated/             # Default safe file-creation folder
└── tests/                     # Automated tool and routing checks
```

## Tasks and implementation

### Page 1 — Build a calculator agent

1. Check the local Ollama model with `ollama list`; the required `llama3.2:3b` model was available.
2. Install the worksheet's `langchain`, `langchain-ollama`, `pyautogui`, and `pygetwindow` libraries with `python -m pip install -r requirements.txt`. The requirements file also pins the RAG and Calendar dependencies used later in the lab.
3. Imports, local LLM initialization, the safe calculator tool, tool registration, and the interactive agent loop are implemented in `agent.py` and `lab6_agent/tools.py`.
4. Test with `Calculate 25 times 4`. The calculator tool returns `100`; when enabled, the Windows Calculator UI opens and enters the calculation.

### Page 2 — Expand with multiple tools

The agent includes the five requested tool types:

- Date and time in the `Asia/Colombo` timezone.
- Notepad: open Windows Notepad and type user-provided text.
- File search: find files by a name fragment or extension beneath a specified folder; search is read-only.
- File creation: create a `.txt` file with supplied text in the default generated folder or an existing trusted folder listed in `LAB6_ALLOWED_WRITE_ROOTS`. Existing files are not overwritten.
- System information: operating system, processor, architecture, Python version, and physical memory.

The six worksheet queries and their run outcomes are recorded in [results/verification-results.md](results/verification-results.md): calculate `25 × 4`; ask today's date; write `Hello Students` in Notepad; find PDFs in `D:\MSC AI`; create a `.txt` file there with `Hello World`; and show computer specifications. The default-folder check used the requested name `test.txt`; after enabling the custom-folder allowlist, the verified repeat used `lab6_write_check.txt` to avoid any overwrite.

### Page 3 — Give the agent memory

`lab6_agent/memory.py` provides persistent SQLite storage and memory search. It supports the worksheet example: save “My name is Alex,” then recall Alex when asked “What is my name?” The calculator remains available alongside the memory search tool.

### Page 4 — RAG-powered agent

The agent exposes the calculator, memory search, and RAG search tools together. `lab6_agent/rag.py` adapts the Lab 5 hierarchical PDF retrieval workflow and returns source/page labels. The verification used the available Lab 5 course handout and returned a relevant answer with citation `[S1]`. No separate institutional handbook was supplied for testing.

### Page 5 — Google Calendar tools

The agent can check today's schedule and create events after showing the proposed title and time and receiving explicit approval. Google OAuth was configured and tested for the user's calendar. The worksheet mentions getting an API key; this implementation uses OAuth because user-specific calendar reads and writes require user authorization. It does not put credentials or tokens in the repository.

## Results and checks

See [results/verification-results.md](results/verification-results.md) for the task-by-task inputs, observed outcomes, and limitations. The automated suite has **25 passing tests** covering calculator safety, file allowlisting, date/time, SQLite persistence, mocked Windows UI actions, RAG behavior, Calendar date windows and approval, and request routing.

Run checks from this folder:

```powershell
python -m unittest discover -s tests -v
```

## Run locally

1. Install Ollama and download the model: `ollama pull llama3.2:3b`.
2. Install Python dependencies: `python -m pip install -r requirements.txt`.
3. Copy `.env.example` to `.env` and configure trusted file-search/write roots as needed.
4. Start Ollama and run `python agent.py` from this directory.
5. Add selectable-text course/university PDFs to `data/knowledge_base/` for RAG; scanned PDFs need OCR before indexing.
6. For Calendar, enable the Google Calendar API, configure an OAuth consent screen, create a Desktop OAuth client, and save its JSON as `credentials.json` here. Authorize when prompted. Google OAuth credentials and tokens are gitignored.

The guided notebook is [notebooks/lab06_ai_agents.ipynb](notebooks/lab06_ai_agents.ipynb). Calendar setup follows Google's [Python quickstart](https://developers.google.com/workspace/calendar/api/quickstart/python).
