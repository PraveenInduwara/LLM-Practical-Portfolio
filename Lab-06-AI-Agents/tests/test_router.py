from __future__ import annotations

import tempfile
import unittest
import os
from unittest.mock import patch
from pathlib import Path

from agent import UniversityAgent


class DirectToolRoutingTests(unittest.TestCase):
    def setUp(self):
        self.env_patch = patch.dict(os.environ, {"LAB6_SHOW_CALCULATOR": "0"})
        self.env_patch.start()
        self.temp = tempfile.TemporaryDirectory(dir=Path(__file__).parent)
        self.workspace = Path(self.temp.name)
        (self.workspace / "data" / "knowledge_base").mkdir(parents=True)
        self.agent = UniversityAgent(
            session_id="route-test",
            workspace=self.workspace,
            knowledge_dir=self.workspace / "data" / "knowledge_base",
        )

    def tearDown(self):
        self.temp.cleanup()
        self.env_patch.stop()

    def test_calculator_request_calls_calculator(self):
        self.assertEqual(self.agent.ask("Calculate 25 times 4 using the calculator tool."), "100")

    def test_date_request_uses_timezone_tool(self):
        self.assertIn("UTC+0530", self.agent.ask("What is today's date and time in Colombo?"))

    def test_calendar_schedule_request_routes_to_calendar_not_date_time(self):
        with patch.object(self.agent, "_invoke_tool", return_value="Today's events: Study at 10:00") as invoke:
            answer = self.agent.ask("What events are on my calendar today?")
        self.assertIn("Study at 10:00", answer)
        invoke.assert_called_once_with("calendar_today")

    def test_calendar_event_create_request_is_not_misrouted_to_date(self):
        self.assertIsNone(self.agent._direct_answer(
            "Create a Google Calendar event today called Lab review from 10:00 to 10:30."
        ))

    def test_name_is_saved_and_recalled_from_sqlite(self):
        self.agent.ask("My name is Alex. Please remember that.")
        self.assertIn("Your name is Alex", self.agent.ask("What is my name? Search memory."))

    def test_file_creation_is_in_lab_generated_folder(self):
        answer = self.agent.ask("Create a file named audit.txt with the exact content Hello World.")
        self.assertIn("Created", answer)
        self.assertEqual((self.workspace / "data" / "generated" / "audit.txt").read_text(), "Hello World")

    def test_worksheet_file_creation_wording_is_understood(self):
        with patch.dict(os.environ, {"LAB6_ALLOWED_WRITE_ROOTS": str(self.workspace)}):
            answer = self.agent.ask(f"Create a file called test.txt in {self.workspace} with Hello World")
        self.assertIn("Created", answer)
        self.assertEqual((self.workspace / "test.txt").read_text(), "Hello World")

    def test_short_worksheet_file_creation_wording_is_understood(self):
        answer = self.agent.ask("Create test.txt with Hello World")
        self.assertIn("Created", answer)
        self.assertEqual((self.workspace / "data" / "generated" / "test.txt").read_text(), "Hello World")

    def test_pdf_search_wording_is_routed_to_file_search(self):
        (self.workspace / "handout.pdf").write_bytes(b"test pdf placeholder")
        answer = self.agent.ask(f"Find all PDFs in {self.workspace}")
        self.assertIn("handout.pdf", answer)

    def test_rag_does_not_make_up_answers_when_no_pdfs_exist(self):
        answer = self.agent.ask("According to the university handbook, when is registration?")
        self.assertIn("No PDF files found", answer)


if __name__ == "__main__":
    unittest.main()

