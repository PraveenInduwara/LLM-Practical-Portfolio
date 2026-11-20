# Lab 5 — RAG Pipeline

## Objective

Build and evaluate a local retrieval-augmented question-answering app over PDFs. The Streamlit app accepts multiple selectable-text PDFs, indexes them locally, answers questions from retrieved passages, and displays source/page evidence.

## Group 2 — Context-aware / hierarchical RAG

Compare three chunking methods on the same corpus and questions:

1. **Fixed-size baseline:** overlapping character windows.
2. **Section-aware:** detect likely headings, then chunk within each section.
3. **Parent-child:** retrieve smaller child passages and expand hits to their larger parent passages.

The comparison records page-level Recall@5, mean reciprocal rank (MRR), latency, required-fact lexical coverage, inline citation presence, and manual answer review. Lexical coverage is not accuracy.

## Project files

- `app.py` — Streamlit PDF chat interface.
- `rag_app/core.py` — PDF extraction, chunking, Chroma indexing, retrieval, and answer generation.
- `ingest.py` / `rag_pipeline.py` — command-line indexing and question answering.
- `evaluation/dataset.json` — 10 questions about the Lab 5 handout.
- `evaluation/dataset_handbook_sample.json` — 8 questions with page references into the handbook sample.
- `evaluation/run_evaluation.py` — comparison CLI, with selectable corpus, dataset, methods, and results directory.
- `evaluation/results/` — handout comparison outputs and manual review.
- `evaluation/results/handbook_sample/` — 50-page handbook sample outputs and manual review.
- `group-activity/` — architecture, technical report, and live-demo checklist.
- `data/source_documents/README.md` — official handbook source link and local sample preparation steps (the handbook PDF is not redistributed).
- `scripts/prepare_handbook_sample.py` — recreates the 50-page evaluation excerpt from the downloaded official PDF.
- `data/evaluation_corpus/` — handout and 50-page handbook evaluation excerpt.

## Windows setup

Use Python 3.11 or 3.12 and a virtual environment. Install Ollama separately from [ollama.com/download](https://ollama.com/download), then run:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
ollama pull llama3.2:3b
ollama pull qwen3-embedding:0.6b
ollama serve
```

In another terminal, from this folder with the environment activated:

```powershell
streamlit run app.py
python evaluation\run_evaluation.py
python evaluation\run_evaluation.py --corpus data\evaluation_corpus\handbook_sample --dataset evaluation\dataset_handbook_sample.json --results-dir evaluation\results\handbook_sample
```

The default evaluation uses only the six-page Lab 5 handout. To reproduce the second experiment, download the official 210-page UGC handbook into `data/source_documents/` and run `python scripts\prepare_handbook_sample.py`; then the second command compares the three methods on its first 50 physical pages. To run retrieval-only diagnostics, add `--retrieval-only`; this skips generation and cannot assess answer quality. Settings can be overridden with a local `.env` copied from `.env.example`.

### PDF handling

Use selectable-text PDFs; scanned/image PDFs need OCR. The Streamlit app accepts PDFs at runtime. Keep private PDFs, local databases, and `.env` files out of Git. The full UGC handbook source and public provenance are documented in `data/source_documents/README.md`.

## Results and limitations

The 50-page handbook sample run used 8 questions, Llama 3.2 3B for generation, Qwen3 Embedding 0.6B for retrieval, and top-k 5. Parent-child scored Recall@5 0.938, MRR 1.000, required-fact lexical coverage 0.663, and 7/8 fully correct answers (strict accuracy 0.875). Fixed-size and section-aware each had Recall@5 0.938 and MRR 1.000; their strict accuracies were 0.625 and 0.500. See `evaluation/results/handbook_sample/` for the per-question records and notes.

The source handbook is 210 pages, but full-book indexing was too slow on the CPU-only runtime. **Only the first 50 pages were evaluated.** The handbook PDF is not included in GitHub; its official source and sample-generation script are provided. This is a long-document sample, not a full-handbook result, and the UGC handbook is a representative public source rather than the user's institution-specific handbook. The sample run averaged 35–47 seconds of generation per answer. Inline citation presence was 37.5% fixed-size, 50% section-aware, and 50% parent-child; answer quality labels are separate from the fact-coverage proxy. The live Streamlit upload/chat demonstration and screenshots remain outstanding.
