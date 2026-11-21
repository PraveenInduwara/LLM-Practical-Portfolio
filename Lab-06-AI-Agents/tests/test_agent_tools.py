from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from lab6_agent.google_integrations import GoogleWorkspace
from lab6_agent.memory import SQLiteMemory
from lab6_agent.tools import calculate, create_text_file, current_datetime, search_files


class CalculatorTests(unittest.TestCase):
    def test_worksheet_calculation(self):
        self.assertEqual(calculate("25 × 4"), "100")

    def test_fraction_and_precedence(self):
        self.assertEqual(calculate("(25 * 4) / 2"), "50")

    def test_python_code_is_rejected(self):
        with self.assertRaises(ValueError):
            calculate("__import__('os').getcwd()")

    def test_division_by_zero_is_reported(self):
        with self.assertRaisesRegex(ValueError, "zero"):
            calculate("1 / 0")


class FileAndTimeTests(unittest.TestCase):
    def test_date_time_in_colombo(self):
        self.assertIn("UTC+0530", current_datetime())

    def test_create_text_file_confines_path(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as tmp:
            message = create_text_file("test.txt", "Hello World", tmp)
            self.assertIn("Created", message)
            self.assertEqual((Path(tmp) / "test.txt").read_text(encoding="utf-8"), "Hello World")
            self.assertIn("without directory", create_text_file("../escape.txt", "bad", tmp))
            self.assertFalse((Path(tmp).parent / "escape.txt").exists())

    def test_search_by_extension(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as tmp:
            Path(tmp, "handbook.pdf").touch()
            Path(tmp, "notes.txt").touch()
            result = search_files(tmp, ".pdf")
            self.assertIn("handbook.pdf", result)
            self.assertNotIn("notes.txt", result)


class MemoryTests(unittest.TestCase):
    def test_sqlite_persists_turns_and_facts(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as tmp:
            path = Path(tmp) / "memory.sqlite3"
            memory = SQLiteMemory(path)
            memory.add_turn("session-a", "user", "My name is Alex.")
            memory.add_turn("session-a", "assistant", "Nice to meet you, Alex.")
            memory.remember("session-a", "Alex is studying computer science.")
            self.assertEqual(memory.recent_turns("session-a")[-1]["role"], "assistant")
            result = SQLiteMemory(path).search("session-a", "name Alex")
            self.assertIn("My name is Alex", result)
            self.assertNotIn("session-b", SQLiteMemory(path).search("session-b", "Alex"))


class GoogleApprovalTests(unittest.TestCase):
    def test_calendar_creation_requires_explicit_confirmation_before_auth(self):
        workspace = GoogleWorkspace(confirm=lambda _: False)
        result = workspace.create_calendar_event(
            "Test", "2026-12-01T10:00:00+05:30", "2026-12-01T10:30:00+05:30"
        )
        self.assertIn("cancelled", result)
        self.assertFalse(workspace._services)

    def test_reversed_calendar_range_rejected(self):
        workspace = GoogleWorkspace(confirm=lambda _: True)
        result = workspace.create_calendar_event(
            "Test", "2026-12-01T11:00:00+05:30", "2026-12-01T10:00:00+05:30"
        )
        self.assertIn("end time must be later", result)
        self.assertFalse(workspace._services)


if __name__ == "__main__":
    unittest.main()

