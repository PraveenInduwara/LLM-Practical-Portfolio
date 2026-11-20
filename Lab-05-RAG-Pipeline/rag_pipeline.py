from __future__ import annotations

import argparse
import time
from pathlib import Path

from rag_app.core import answer_question, build_index, load_pdf_directory


def main() -> None:
    parser = argparse.ArgumentParser(description="Ask a question over a folder of PDFs.")
    parser.add_argument("pdf_directory", type=Path)
    parser.add_argument("--strategy", choices=["fixed", "sections", "parent_child"], default="parent_child")
    parser.add_argument("--top-k", type=int, default=5)
    args = parser.parse_args()
    index = build_index(load_pdf_directory(args.pdf_directory), strategy=args.strategy)
    while True:
        question = input("Ask a question (or type exit): ").strip()
        if question.lower() in {"exit", "quit"}:
            break
        if not question:
            continue
        started = time.perf_counter()
        answer, sources = answer_question(index, question, k=args.top_k)
        print(f"\nAnswer ({time.perf_counter() - started:.2f}s):\n{answer}")
        for i, doc in enumerate(sources, 1):
            print(f"[S{i}] {doc.metadata.get('source')} - page {doc.metadata.get('page')}")
        print()


if __name__ == "__main__":
    main()
