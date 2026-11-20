# Lab 5 Group Activity: Technical Report

## Project and objective

**Group 2 — Context-aware / hierarchical RAG.** Compare fixed-size, section-aware, and parent-child chunking for question answering over academic documents, evaluating whether parent context improves retrieval and answer quality.

## Problem statement

The Lab 5 brief identifies limitations in fixed-size chunking and dense top-k retrieval for complex queries, long documents, exact academic terms, and information distributed across documents. This project implements three chunking strategies, a multi-PDF Streamlit app, and a controlled comparison using common question sets. It measures page-level Recall@5, mean reciprocal rank (MRR), latency, required-fact lexical coverage, inline citation presence, and manually reviewed answer quality.

## System and method

PDF pages are extracted with pypdf while retaining source and one-based page metadata. Chroma indexes the chunks. Qwen3 Embedding 0.6B via Ollama creates vectors; Llama 3.2 3B via Ollama generates answers from retrieved excerpts. The Streamlit app accepts multiple PDFs, exposes the three chunking methods, displays the generated response, and exposes retrieved passages with source/page labels.

- Fixed-size: 900-character chunks, 140-character overlap.
- Section-aware: infer heading boundaries, then 1,000-character chunks with 120-character overlap.
- Parent-child: 1,500-character parent chunks with 180-character overlap; 420-character children with 80-character overlap; retrieve children and give parent text to generation.

The evaluator uses the same corpus, questions, models, prompt, and top-k (5) for all three strategies in each run. Separate runs were used for the handout and the longer handbook sample.

## Runtime and reproducibility

The full handout run completed on 2026-11-21 at 02:02 Sri Lanka time; the handbook-sample run completed at 02:50. Runtime was CPU-only local Ollama, without CUDA. The chat model was `llama3.2:3b`, embedding model `qwen3-embedding:0.6b`, context length 2,048, max output 256 tokens, and keep-alive 0 during evaluation. Retrieval used k=5.

The primary handbook source is the 210-page University Grants Commission of Sri Lanka University Admissions Handbook for academic year 2025/2026. Due to CPU runtime, the completed comparison uses only its first 50 physical pages. The PDF is excluded from the public repository because redistribution permissions are unclear; the official download link and a script to recreate the excerpt are provided under `data/source_documents/README.md` and `scripts/prepare_handbook_sample.py`. The 8 handbook questions cite pages within those first 50 pages. The handout experiment used one six-page PDF and 10 questions. The full handbook indexing attempt was stopped because it remained CPU-bound for several minutes before completing a strategy. It produced no results and is not counted as a run.

## Results: 50-page handbook sample

| Strategy | Chunks | Recall@5 | MRR | Mean retrieval (s) | Mean generation (s) | Fact coverage* | Fully correct | Partial | Incorrect | Strict accuracy | Inline citation |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Fixed-size | 131 | 0.938 | 1.000 | 2.137 | 46.659 | 0.642 | 5/8 | 3/8 | 0/8 | 0.625 | 3/8 (0.375) |
| Section-aware | 167 | 0.938 | 1.000 | 2.923 | 34.951 | 0.344 | 4/8 | 2/8 | 2/8 | 0.500 | 4/8 (0.500) |
| Parent-child | 302 | 0.938 | 1.000 | 2.456 | 40.332 | 0.663 | 7/8 | 1/8 | 0/8 | 0.875 | 4/8 (0.500) |

Mean end-to-end latency was 48.795 s fixed-size, 37.874 s section-aware, and 42.788 s parent-child. Parent-child gave the strongest answer quality and required-fact coverage in this 50-page, 8-question sample. All strategies had equal Recall@5 and MRR on these questions. Section-aware was fastest end to end. The small sample does not prove a general long-handbook advantage.

## Results: Lab 5 handout

| Strategy | Chunks | Recall@5 | MRR | Mean retrieval (s) | Mean generation (s) | Fact coverage* | Fully correct | Partial | Incorrect | Strict accuracy | Inline citation |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Fixed-size | 9 | 1.000 | 0.695 | 3.004 | 33.264 | 0.742 | 5/10 | 4/10 | 1/10 | 0.500 | 1/10 (0.100) |
| Section-aware | 15 | 0.900 | 0.850 | 2.118 | 28.493 | 0.562 | 4/10 | 5/10 | 1/10 | 0.400 | 2/10 (0.200) |
| Parent-child | 16 | 1.000 | 0.875 | 1.928 | 30.184 | 0.847 | 8/10 | 1/10 | 1/10 | 0.800 | 2/10 (0.200) |

Parent-child also led in strict answer accuracy and lexical coverage on the handout run. Across both datasets, it is the strongest observed configuration in this project’s limited tests.

*Required-fact coverage is an automated lexical proxy, not answer correctness. Strict accuracy counts only fully correct answers; partial judgments are separate. Citation rate only counts whether the answer text contains an `[S#]` marker. The app separately displays retrieved source and page evidence, but this inline citation rate is low and should be improved before relying on generated responses without checking the evidence panel.

## Manual review and findings

All 54 generated answers (30 handout answers and 24 handbook-sample answers) were checked against their reference answers and retrieved evidence. In the handbook sample, parent-child returned correct answers for seven of eight questions; its one partial answer omitted some details about annual cut-off variation. Section-aware abstained incorrectly on the Z-score factors and Arts-course exceptions even though those facts were retrieved. Fixed-size omitted the remaining 5% quota category and the application fee in two answers. These failures appear in the per-question CSV and manual-review JSON.

On the handout set, parent-child had one incorrect abstention on the report/evaluation question and one partial answer on Group 4’s knowledge-graph task. Lexical coverage and answer correctness do not always align, which is why both metrics are reported.

## Limitations and outstanding work

1. **Partial handbook coverage:** the official UGC handbook is 210 pages, but only the first 50 physical pages were evaluated after full indexing proved too slow on CPU. The complete 210-page handbook objective remains incomplete.
2. **Institution specificity:** the brief asks about long academic handbooks but names no institution-specific PDF. The UGC handbook is a relevant public Sri Lankan admissions handbook; it may differ from the user's university handbook.
3. **Small test set:** the 8 questions cover a few sections in the first 50 pages; results cannot generalize to the entire handbook or other universities.
4. **CPU latency:** model generation averaged 35–47 seconds per answer in the handbook sample. A GPU run was not tested.
5. **Citation compliance:** only 37.5–50% of sample answers contained inline `[S#]` markers. The UI evidence panel provides source passages, but citation formatting should be made more reliable.
6. **PDF extraction:** pypdf warned that rotated text could be incomplete. The tested answer pages extracted legible relevant text, but other pages may need layout cleanup or OCR.
7. **Live demo:** the application imports and starts, but a browser-based upload/query demo and screenshots have not been verified in this runtime.
8. **Chunking heuristic:** heading detection is based on text patterns and can miss complex PDF layouts, tables, and inconsistent headings.

## Conclusion

The app and both controlled comparisons have been implemented and run. Parent-child is the leading method in the measured results, including the tested 50-page handbook sample. The evidence does **not** establish performance on all 210 handbook pages. To close the remaining gap, run the full handbook on a faster runtime (or a user-selected campus handbook), improve inline citation reliability, and complete the live Streamlit demonstration with screenshots.
