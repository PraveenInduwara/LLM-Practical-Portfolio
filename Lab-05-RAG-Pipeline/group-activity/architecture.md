# Group 2: Context-Aware / Hierarchical RAG

## Research question

For long academic handbooks, which context strategy gives the strongest evidence retrieval and answer quality: fixed-size chunks, section-aware chunks, or parent-child retrieval?

## Proposed architecture

```mermaid
flowchart TD
    U[PDF upload or local PDF folder] --> P[PyPDF text extraction with page metadata]
    P --> C{Chunking strategy}
    C --> F[Fixed-size baseline]
    C --> S[Section-aware chunks]
    C --> H[Large parent chunks and small child chunks]
    F --> E[Qwen3 embedding model through Ollama]
    S --> E
    H --> E
    E --> V[Chroma vector index]
    Q[User question] --> V
    V --> R[Top-k evidence retrieval]
    R --> X[Expand child matches to parent context]
    R --> G[Llama 3.2 3B through Ollama]
    X --> G
    G --> A[Cited answer or explicit abstention]
    A --> D[Streamlit chat interface]
    R --> M[Recall@5, MRR, latency, answer review]
```

The experiment holds the corpus, question set, embedding model, generation model, and top-k constant while changing the chunking strategy. Parent-child retrieval embeds smaller child passages and supplies their larger parent passage to generation. The app also accepts user-uploaded PDFs and shows the source PDF and page for each retrieved passage.

## Risks and limitations

- PDF text extraction does not OCR scanned pages.
- The supplied course handout is shorter than a full academic handbook; a longer handbook should be added before generalizing the outcome.
- The three strategies can produce different numbers of chunks. Chunk counts are recorded, while fixed top-k, same question set, and same corpus keep the principal comparison consistent.
- Latency includes local model startup/caching effects; report warm-run and cold-start conditions separately if both are measured.
- Lexical required-fact coverage is a diagnostic proxy. Human answer-correctness review against the cited source is also recorded.
