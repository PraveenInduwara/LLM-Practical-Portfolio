# Lab 6 verification results

Scope: **Lab Sheet pages 1–5 only.** Pages after page 5 are intentionally excluded. This file records results; the Lab Sheet PDF itself is not part of this repository update.

## Page 1 — Calculator agent

| Worksheet task | Run/check | Result |
| --- | --- | --- |
| Check required Ollama model | `ollama list` | `llama3.2:3b` was installed and available. |
| Install `langchain`, `langchain-ollama`, `pyautogui`, and `pygetwindow`; import libraries and initialize local LLM | Install from `requirements.txt`, then start `agent.py` | Required packages are declared; local Ollama model initialized successfully. RAG and Calendar dependencies are included in the same requirements file. |
| Create/register calculator tool and implement agent loop | Ask `Calculate 25 times 4` | The real model selected the calculator tool; calculation returned `100`. User confirmed the interactive calculator task completed. |

## Page 2 — Multiple tools

| Worksheet query | Result |
| --- | --- |
| `Calculate 25 × 4` | Calculator returned `100`. |
| `What is the date today?` | The date/time tool returned the current date/time using `Asia/Colombo`. |
| `Open Notepad and write Hello Students` | User confirmed Notepad opened and the text was entered. Automated UI tests also pass with mocks. |
| `Find all PDF files in D:\MSC AI` | Search ran under the existing folder (resolved by Windows to `C:\MSC-AI-Drive\MSC AI`) and returned no `.pdf` files. The folder was empty, so this is the correct search result. |
| `Create a file called test.txt in D:\MSC AI with Hello World` | The exact `test.txt` name was created and verified in the default generated folder. To verify the custom destination safely, after adding the existing folder to `LAB6_ALLOWED_WRITE_ROOTS`, the agent created `lab6_write_check.txt` (11 bytes) in `D:\MSC AI`; PowerShell read it and returned `Hello World`. |
| `Show my computer specifications` | Tool returned operating system, processor, architecture, Python version, and physical-memory information. |

The initial custom-folder write attempt was correctly denied while the folder was not allowlisted. After setting the allowlist in the same PowerShell session that launched the agent, a custom-folder write succeeded and was verified from disk. The default generated-folder write was also verified at `data/generated/test.txt` (11 bytes, `Hello World`). Runtime-generated files are gitignored.

## Page 3 — SQLite memory

- Stored the example fact “My name is Alex.”
- Asked “What is my name?”; the agent recalled Alex.
- Automated tests verify that facts and turns persist in SQLite and that memory-search requests route to the memory tool.

## Page 4 — RAG-powered agent

- The calculator, memory-search, and RAG-search tools are available together.
- Tested retrieval against the available Lab 5 course handout.
- A question about the group task received a relevant answer with source label `[S1]`.
- No separate institutional handbook was supplied or evaluated. Add another selectable-text course/university PDF under `data/knowledge_base/` to test against that source.

## Page 5 — Google Calendar

- Completed local Google OAuth authorization.
- Asked for today's events; the agent reported no events for the queried date in `Asia/Colombo`.
- The agent proposed a test event and requested confirmation. The user explicitly approved it and reported successful creation.
- Event details and OAuth data are omitted from this public repository.

OAuth is used instead of a plain API key for user-specific Calendar access, since the agent needs permission to read and create events on the user's calendar.

## Automated validation

Command: `python -m unittest discover -s tests -v`

Result: **25 tests passed.** Coverage includes safe calculator parsing, file-search and write allowlisting, Colombo date/time, SQLite persistence, mocked Calculator/Notepad UI actions, RAG no-document behavior, Calendar date windows and explicit approval, and tool routing.

## Scope and privacy

- The tested `D:\MSC AI` folder contained no PDFs; the agent correctly returned an empty search result.
- RAG verification is based on the Lab 5 course handout, not a separate institutional handbook.
- Credentials, OAuth tokens, local memory databases, and generated text files are excluded from Git. No Calendar event title, date, or attendee details are published here.
