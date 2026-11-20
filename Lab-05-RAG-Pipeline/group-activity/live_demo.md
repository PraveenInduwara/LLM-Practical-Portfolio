# Live Demonstration Checklist

1. Start Ollama and confirm `ollama list` includes `llama3.2:3b` and `qwen3-embedding:0.6b`.
2. Start the app with `streamlit run app.py` from the Lab 5 folder.
3. Upload a selectable-text university PDF, choose Parent-child, and click **Index / refresh PDFs**.
4. Ask one answerable question and one question absent from the PDF.
5. Show the cited source name, page, and retrieved passage. The absent question should be answered with an explicit lack-of-evidence response.
6. Change to Fixed-size and Section-aware and re-index to show the same document under each chunking strategy.
7. Run `python evaluation/run_evaluation.py` to reproduce the comparison and show the output metrics.

Record the final demo date, machine/runtime, documents used, and any setup issues after the live demonstration.
