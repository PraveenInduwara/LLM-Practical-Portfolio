from pathlib import Path
import unittest

from rag_app.core import load_pdf_directory, make_chunks
from langchain_core.documents import Document


ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / "data" / "evaluation_corpus"


class ChunkingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pages = load_pdf_directory(CORPUS)

    def test_handout_extracts_six_nonempty_pages(self):
        self.assertEqual(len(self.pages), 6)
        self.assertTrue(all(page.metadata.get("page") for page in self.pages))

    def test_all_strategies_create_chunks_with_page_sources(self):
        for strategy in ("fixed", "sections", "parent_child"):
            with self.subTest(strategy=strategy):
                chunks, _, _ = make_chunks(self.pages, strategy)
                self.assertTrue(chunks)
                self.assertTrue(all(chunk.metadata.get("source") for chunk in chunks))
                self.assertTrue(all(chunk.metadata.get("page") for chunk in chunks))

    def test_parent_child_chunks_resolve_to_parents(self):
        chunks, parents, parent_meta = make_chunks(self.pages, "parent_child")
        self.assertTrue(chunks)
        self.assertEqual(set(parents), set(parent_meta))
        self.assertTrue(all(chunk.metadata["parent_id"] in parents for chunk in chunks))

    def test_section_chunk_keeps_bullet_deliverables_and_heading_context(self):
        page = Document(
            page_content=(
                "Expected Deliverables\n"
                "�   Working enhanced RAG application\n"
                "�   Proposed architecture diagram\n"
                "�   Technical report discussing methodology, findings, and limitations"
            ),
            metadata={"source": "synthetic.pdf", "page": 1},
        )
        chunks, _, _ = make_chunks([page], "sections")
        self.assertEqual(len(chunks), 1)
        self.assertIn("Expected Deliverables", chunks[0].page_content)
        self.assertIn("Working enhanced RAG application", chunks[0].page_content)
        self.assertIn("Proposed architecture diagram", chunks[0].page_content)


if __name__ == "__main__":
    unittest.main()
