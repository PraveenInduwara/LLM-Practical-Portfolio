from __future__ import annotations

import argparse
from pathlib import Path

from pypdf import PdfReader, PdfWriter


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Create the reproducible first-50-page UGC handbook evaluation sample."
    )
    parser.add_argument(
        "source_pdf",
        nargs="?",
        type=Path,
        default=Path("data/source_documents/UGC_University_Admissions_Handbook_2025-2026.pdf"),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(
            "data/evaluation_corpus/handbook_sample/"
            "UGC_University_Admissions_Handbook_2025-2026_first50pages.pdf"
        ),
    )
    parser.add_argument("--pages", type=int, default=50)
    args = parser.parse_args()

    if not args.source_pdf.is_file():
        raise FileNotFoundError(
            f"Source PDF not found: {args.source_pdf}. Download the official handbook; "
            "see data/source_documents/README.md."
        )
    if args.pages < 1:
        raise ValueError("--pages must be a positive integer")

    reader = PdfReader(args.source_pdf, strict=False)
    if len(reader.pages) < args.pages:
        raise ValueError(
            f"Source has {len(reader.pages)} pages; cannot extract the first {args.pages}."
        )
    writer = PdfWriter()
    for page in reader.pages[: args.pages]:
        writer.add_page(page)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("wb") as stream:
        writer.write(stream)
    print(f"Created {args.output} with {args.pages} pages from {args.source_pdf}")


if __name__ == "__main__":
    main()
