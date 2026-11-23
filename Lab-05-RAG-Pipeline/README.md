# Lab 5 — RAG Pipeline

## Objective

Build and evaluate a local retrieval-augmented question-answering app over PDFs. The Streamlit app accepts multiple selectable-text PDFs, indexes them locally, answers questions from retrieved passages, and displays source/page evidence.

## Tasks and implementation

1. Extract selectable text from each PDF page and preserve the source filename and one-based page number as metadata. Scanned PDFs require OCR before ingestion.
2. Normalize the extracted text and prepare one of three retrieval representations: overlapping fixed-size chunks, heading-aware section chunks, or smaller child chunks linked to larger parent passages.
3. Embed the chunks with the configured local Ollama embedding model and store them in a local Chroma collection. For parent-child retrieval, use the child hits to select and return their parent passages.
4. Retrieve the top five passages for each question. Ask the local Llama 3.2 3B chat model to answer using the retrieved context and include source/page evidence; the Streamlit app exposes this workflow for uploaded selectable-text PDFs.
5. Compare the strategies on the same handout and handbook-sample questions. Record retrieval measures, latency, fact coverage, citation markers, and manual answer judgements in `evaluation/results/`.

The implementation is in `rag_app/core.py`, with the interactive interface in `app.py` and repeatable evaluation commands in `evaluation/run_evaluation.py`. Use the setup and commands below to run the application and reproduce the saved evaluations.

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

## Observations

- On the six-page handout, parent-child retrieval produced the highest strict answer accuracy (8/10), while fixed-size and section-aware methods scored 5/10 and 4/10. On the separate 50-page handbook sample, parent-child scored 7/8. These are small, manually reviewed samples, not proof of general reliability.
- Recall@5 and MRR were similar across strategies on the handbook sample, even though strict answer accuracy differed. Retrieval ranking metrics alone did not describe answer quality.
- Inline citation markers were missing from many answers, and CPU generation took roughly 35–47 seconds per handbook answer. The interface may show retrieved evidence, but a citation displayed in the UI and a citation marker in the answer text are separate checks.
- Evaluation covered only a 50-page excerpt of a 210-page handbook and did not use NSBM-specific documents. Full-handbook indexing was too slow on the available CPU runtime.
- The application and evaluation code are in the repository, but the live upload/chat demonstration and its screenshots have not been captured. This visual evidence remains outstanding; no live-demo screenshot is claimed here.

## Learning Outcomes

- Built a local PDF retrieval pipeline that retains page metadata, compares chunking strategies, retrieves evidence, and generates answers from retrieved context.
- Used Recall@5 and MRR for retrieval, latency and lexical fact coverage as diagnostics, and manual review for strict/partial answer correctness and citation presence.
- Learned that relevant retrieval does not guarantee a complete or correct answer, and that automated lexical coverage is not an accuracy measure.
- Identified practical trade-offs in chunk size, document coverage, local compute time, and answer citations; a deployment would need broader tests on current institution-specific material.
