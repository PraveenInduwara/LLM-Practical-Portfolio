from __future__ import annotations

import argparse
from pathlib import Path

from rag_app.core import DEFAULT_PERSIST_DIRECTORY, build_index, load_pdf_directory


def main() -> None:
    parser = argparse.ArgumentParser(description="Ingest PDFs into the Lab 5 Chroma index.")
    parser.add_argument("pdf_directory", type=Path, help="Folder containing selectable-text PDF files")
    parser.add_argument("--strategy", choices=["fixed", "sections", "parent_child"], default="parent_child")
    parser.add_argument("--persist", type=Path, default=Path(DEFAULT_PERSIST_DIRECTORY))
    parser.add_argument("--collection", default="lab05_university_docs")
    args = parser.parse_args()
    pages = load_pdf_directory(args.pdf_directory)
    index = build_index(pages, args.strategy, args.persist, args.collection)
    print(f"Indexed {index.document_count} PDF(s), {len(pages)} non-empty page(s), "
          f"{index.chunk_count} {args.strategy} chunks into {args.persist}.")


if __name__ == "__main__":
    main()
