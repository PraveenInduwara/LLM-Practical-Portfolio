from __future__ import annotations

import sys
import re
from pathlib import Path


class Lab5KnowledgeBase:
    """Reuse Lab 5's PDF extraction, hierarchical chunking and Ollama embeddings."""

    def __init__(self, pdf_directory: str | Path, top_k: int = 5):
        self.pdf_directory = Path(pdf_directory).expanduser().resolve()
        self.top_k = max(1, min(int(top_k), 10))
        self._index = None
        self._retrieve = None
        self._pages = []
        self._load_error: str | None = None

    def _ensure_index(self) -> None:
        if self._index is not None or self._load_error:
            return
        pdfs = list(self.pdf_directory.glob("*.pdf")) if self.pdf_directory.is_dir() else []
        if not pdfs:
            self._load_error = (
                f"No PDF files found in {self.pdf_directory}. Add selectable-text university PDFs "
                "to that folder, then restart the agent."
            )
            return
        lab5 = Path(__file__).resolve().parents[2] / "Lab-05-RAG-Pipeline"
        if not (lab5 / "rag_app" / "core.py").is_file():
            self._load_error = "The adjacent Lab-05-RAG-Pipeline/rag_app/core.py module was not found."
            return
        sys.path.insert(0, str(lab5))
        try:
            from rag_app.core import build_index, load_pdf_directory, retrieve

            pages = load_pdf_directory(self.pdf_directory)
            self._pages = pages
            self._index = build_index(
                pages,
                strategy="parent_child",
                collection_name="lab06_university_knowledge",
            )
            self._retrieve = retrieve
        except Exception as exc:
            self._load_error = f"Could not build the Lab 5 vector index: {type(exc).__name__}: {exc}"

    @staticmethod
    def _lexical_score(text: str, terms: set[str]) -> float:
        tokens = re.findall(r"[a-z0-9]+", text.casefold())
        if not tokens or not terms:
            return 0.0
        counts = {token: tokens.count(token) for token in terms}
        overlap = [count for count in counts.values() if count]
        if not overlap:
            return 0.0
        return sum(1.0 + min(count - 1, 2) * 0.2 for count in overlap) / len(terms)

    def search(self, query: str) -> str:
        self._ensure_index()
        if self._load_error and not self._pages:
            return self._load_error
        vector_documents = []
        vector_error = None
        if self._index is not None:
            try:
                vector_documents = self._retrieve(self._index, query, k=self.top_k)
            except Exception as exc:
                vector_error = f"Vector retrieval error: {type(exc).__name__}: {exc}"
        stopwords = {"the", "and", "for", "with", "from", "does", "doesn", "what", "when", "where", "which", "that", "this", "are", "was", "were", "how", "should", "would", "could", "tell", "find", "use", "using", "have", "has", "agent"}
        terms = {token for token in re.findall(r"[a-z0-9]+", query.casefold()) if len(token) > 2 and token not in stopwords}
        ranked_pages = sorted(
            ((self._lexical_score(page.page_content, terms), page) for page in self._pages),
            key=lambda pair: pair[0], reverse=True,
        )
        # Merge semantic retrieval with a page-level lexical pass. This helps short
        # headings such as "Part B" remain findable in the lab handout.
        candidates = {}
        for document in vector_documents:
            key = (document.metadata.get("source", "unknown source"), document.metadata.get("page", "?"))
            candidates[key] = document
        for score, page in ranked_pages[: self.top_k]:
            if score <= 0:
                continue
            key = (page.metadata.get("source", "unknown source"), page.metadata.get("page", "?"))
            candidates.setdefault(key, page)
        documents = list(candidates.values())
        documents.sort(
            key=lambda doc: self._lexical_score(doc.page_content, terms),
            reverse=True,
        )
        documents = documents[: self.top_k]
        if not documents:
            if vector_error:
                return f"No passages were retrieved. {vector_error}"
            return "No relevant passages were found in the configured PDF knowledge base."
        parts = []
        for i, doc in enumerate(documents, start=1):
            source = doc.metadata.get("source", "unknown source")
            page = doc.metadata.get("page", "?")
            parts.append(f"[S{i}] {source}, page {page}\n{doc.page_content[:1800]}")
        prefix = f"Note: {self._load_error}. Used lexical PDF retrieval for this query.\n\n" if self._load_error else ""
        return prefix + "\n\n".join(parts)

