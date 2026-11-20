from __future__ import annotations

import argparse
import csv
import json
import re
import statistics
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from rag_app.core import (
    OLLAMA_CHAT_KEEP_ALIVE,
    OLLAMA_CONTEXT_LENGTH,
    OLLAMA_EMBED_KEEP_ALIVE,
    OLLAMA_CHAT_MODEL,
    OLLAMA_EMBED_MODEL,
    OLLAMA_MAX_NEW_TOKENS,
    build_index,
    generate_answer,
    load_pdf_directory,
    ollama_embeddings,
    retrieve,
)

DATASET_PATH = Path(__file__).with_name("dataset.json")
RESULTS = Path(__file__).with_name("results")
STRATEGIES = ("fixed", "sections", "parent_child")


def rank_metrics(retrieved, source_name: str, relevant_pages: set[int], k: int = 5) -> tuple[float, float]:
    ranked = retrieved[:k]
    hits = [
        doc.metadata.get("source") == source_name and int(doc.metadata.get("page", -1)) in relevant_pages
        for doc in ranked
    ]
    recall = len({int(doc.metadata.get("page", -1)) for doc, hit in zip(ranked, hits) if hit}) / max(1, len(relevant_pages))
    reciprocal_rank = next((1.0 / (i + 1) for i, hit in enumerate(hits) if hit), 0.0)
    return min(1.0, recall), reciprocal_rank


def fact_coverage(answer: str, required_facts: list[str]) -> float:
    """Transparent lexical coverage proxy; not a substitute for human correctness review."""
    if not required_facts:
        return 0.0
    normalize = lambda value: "".join(ch for ch in value.casefold() if ch.isalnum())
    folded = normalize(answer)
    return sum(normalize(fact) in folded for fact in required_facts) / len(required_facts)


def main() -> None:
    parser = argparse.ArgumentParser(description="Compare three RAG chunking strategies on the same questions.")
    parser.add_argument("--corpus", type=Path, default=ROOT / "data" / "evaluation_corpus")
    parser.add_argument("--dataset", type=Path, default=DATASET_PATH)
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument("--results-dir", type=Path, default=RESULTS, help="Directory for metrics and per-question outputs")
    parser.add_argument("--strategies", nargs="+", choices=STRATEGIES, default=list(STRATEGIES))
    parser.add_argument("--retrieval-only", action="store_true", help="Skip generation and measure retrieval only")
    args = parser.parse_args()

    cases = json.loads(args.dataset.read_text(encoding="utf-8"))
    pages = load_pdf_directory(args.corpus)
    source_names = {p.name for p in args.corpus.glob("*.pdf")}
    missing_sources = sorted({c["source"] for c in cases} - source_names)
    if missing_sources:
        raise ValueError(f"Evaluation dataset names missing source PDF(s): {missing_sources}")

    embedder = ollama_embeddings()
    result_rows: list[dict] = []
    metrics: dict[str, dict] = {}
    run_time = time.strftime("%Y-%m-%d %H:%M:%S %Z")
    for strategy in args.strategies:
        index = build_index(pages, strategy=strategy, embeddings=embedder)
        recalls, mrrs, retrieval_ms, answer_ms, end_to_end_ms, coverages, citation_flags = [], [], [], [], [], []
        strategy_rows: list[dict] = []
        for case in cases:
            started = time.perf_counter()
            ranked = retrieve(index, case["question"], k=args.top_k)
            retrieval_elapsed = (time.perf_counter() - started) * 1000
            recall, reciprocal_rank = rank_metrics(
                ranked, case["source"], set(case["relevant_pages"]), k=args.top_k
            )
            recalls.append(recall)
            mrrs.append(reciprocal_rank)
            retrieval_ms.append(retrieval_elapsed)
            strategy_rows.append({
                "strategy": strategy,
                "case": case,
                "ranked": ranked,
                "answer": "",
                "generation_latency_ms": "",
                "recall_at_k": recall,
                "reciprocal_rank": reciprocal_rank,
                "retrieval_latency_ms": retrieval_elapsed,
            })

        # Retrieve all evidence before loading the chat model. This avoids
        # holding the embedding and generation models in memory together.
        for row in strategy_rows:
            case = row["case"]
            ranked = row["ranked"]
            answer = ""
            generation_elapsed = 0.0
            if not args.retrieval_only:
                generation_started = time.perf_counter()
                answer = generate_answer(case["question"], ranked)
                generation_elapsed = (time.perf_counter() - generation_started) * 1000
                answer_ms.append(generation_elapsed)
                end_to_end_ms.append(row["retrieval_latency_ms"] + generation_elapsed)
                coverages.append(fact_coverage(answer, case.get("required_facts", [])))
                citation_flags.append(bool(re.search(r"\[S\d+\]", answer)))
            row["answer"] = answer
            row["generation_latency_ms"] = generation_elapsed if not args.retrieval_only else ""
            result_rows.append({
                "strategy": strategy,
                "question_id": case["id"],
                "question": case["question"],
                "reference_answer": case["reference_answer"],
                "answer": answer,
                "retrieved_sources": " | ".join(
                    f"{d.metadata.get('source')} p.{d.metadata.get('page')}" for d in ranked
                ),
                "relevant_pages": ",".join(map(str, case["relevant_pages"])),
                "recall_at_k": row["recall_at_k"],
                "reciprocal_rank": row["reciprocal_rank"],
                "retrieval_latency_ms": row["retrieval_latency_ms"],
                "answer_latency_ms": generation_elapsed if not args.retrieval_only else "",
                "end_to_end_latency_ms": (row["retrieval_latency_ms"] + generation_elapsed) if not args.retrieval_only else "",
                "required_fact_coverage": fact_coverage(answer, case.get("required_facts", [])) if answer else "",
                "human_correctness": "REVIEW_REQUIRED" if answer else "NOT_RUN",
                "review_notes": "",
                "citation_present": "yes" if answer and re.search(r"\[S\d+\]", answer) else "no" if answer else "NOT_RUN",
            })
        metrics[strategy] = {
            "queries": len(cases),
            "k": args.top_k,
            "recall_at_k": statistics.mean(recalls),
            "mrr": statistics.mean(mrrs),
            "mean_retrieval_latency_ms": statistics.mean(retrieval_ms),
            "mean_answer_latency_ms": statistics.mean(answer_ms) if answer_ms else None,
            "mean_end_to_end_latency_ms": statistics.mean(end_to_end_ms) if end_to_end_ms else None,
            "mean_required_fact_coverage": statistics.mean(coverages) if coverages else None,
            "inline_citation_rate": statistics.mean(citation_flags) if citation_flags else None,
            "human_correctness": "must be reviewed in question_results.csv",
            "chunk_count": index.chunk_count,
        }
        index.vectorstore.delete_collection()

    results_dir = args.results_dir
    results_dir.mkdir(parents=True, exist_ok=True)
    with (results_dir / "question_results.csv").open("w", newline="", encoding="utf-8-sig") as stream:
        writer = csv.DictWriter(stream, fieldnames=[
            "strategy", "question_id", "question", "reference_answer", "answer",
            "retrieved_sources", "relevant_pages", "recall_at_k", "reciprocal_rank",
            "retrieval_latency_ms", "answer_latency_ms", "end_to_end_latency_ms",
            "required_fact_coverage", "human_correctness", "review_notes", "citation_present",
        ])
        writer.writeheader()
        writer.writerows(result_rows)
    report = {
        "run_time": run_time,
        "corpus_pdf_count": len(source_names),
        "nonempty_pages": len(pages),
        "evaluation_question_count": len(cases),
        "ollama_chat_model": OLLAMA_CHAT_MODEL,
        "ollama_embedding_model": OLLAMA_EMBED_MODEL,
        "model_runtime_config": {
            "context_length": OLLAMA_CONTEXT_LENGTH,
            "max_new_tokens": OLLAMA_MAX_NEW_TOKENS,
            "embedding_keep_alive": OLLAMA_EMBED_KEEP_ALIVE,
            "chat_keep_alive": OLLAMA_CHAT_KEEP_ALIVE,
        },
        "retrieval_only": args.retrieval_only,
        "strategies": metrics,
        "correctness_note": "Required-fact coverage is a lexical proxy, not correctness. Human correctness labels remain REVIEW_REQUIRED until a reviewer checks each answer against the reference and PDF evidence. Inline citation rate measures whether generated answer text contains an [S#] marker; the app also displays retrieved evidence separately.",
    }
    (results_dir / "metrics.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    print(f"Saved per-question evidence to {results_dir / 'question_results.csv'}")


if __name__ == "__main__":
    main()
