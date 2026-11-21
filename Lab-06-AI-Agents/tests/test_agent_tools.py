from __future__ import annotations

import tempfile
import unittest
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo
from unittest.mock import Mock, patch

from lab6_agent import tools as agent_tools
from lab6_agent.google_integrations import GoogleCalendar
from lab6_agent.memory import SQLiteMemory
from lab6_agent.tools import calculate, create_text_file, current_datetime, open_notepad_with_text, search_files


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

    def test_calculator_tool_opens_ui_and_enters_expression_when_enabled(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as tmp:
            tools = agent_tools.build_tools(
                SQLiteMemory(Path(tmp) / "memory.sqlite3"), "test", Mock(), tmp
            )
            calculator = next(item for item in tools if item.name == "calculator")
            fake_window, gui, windows = Mock(), Mock(), Mock()
            windows.getWindowsWithTitle.return_value = [fake_window]
            with (
                patch.dict(os.environ, {"LAB6_SHOW_CALCULATOR": "1"}),
                patch.dict(sys.modules, {"pyautogui": gui, "pygetwindow": windows}),
                patch.object(agent_tools.sys, "platform", "win32"),
                patch.object(agent_tools.subprocess, "Popen") as launch,
                patch.object(agent_tools.time, "sleep"),
            ):
                answer = calculator.invoke({"expression": "25 * 4"})
            self.assertTrue(answer.startswith("100 (Displayed"))
            launch.assert_called_once()
            gui.write.assert_called_once_with("25*4", interval=0.03)
            gui.press.assert_called_once_with("enter")


class WindowsToolTests(unittest.TestCase):
    def test_notepad_opens_and_types_requested_text(self):
        fake_window, gui, windows = Mock(), Mock(), Mock()
        windows.getWindowsWithTitle.return_value = [fake_window]
        with (
            patch.dict(sys.modules, {"pyautogui": gui, "pygetwindow": windows}),
            patch.object(agent_tools.sys, "platform", "win32"),
            patch.object(agent_tools.subprocess, "Popen") as launch,
            patch.object(agent_tools.time, "sleep"),
        ):
            result = open_notepad_with_text("Hello Students")
        self.assertEqual(result, "Opened Notepad and typed the requested text.")
        launch.assert_called_once_with(["notepad.exe"], close_fds=True)
        gui.write.assert_called_once_with("Hello Students", interval=0.02)


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
            self.assertIn("already exists", create_text_file("test.txt", "overwrite", tmp))

    def test_explicit_directory_requires_and_obeys_write_allowlist(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as tmp:
            with patch.dict(os.environ, {"LAB6_ALLOWED_WRITE_ROOTS": ""}):
                blocked = create_text_file("test.txt", "Hello World", Path(tmp) / "generated", tmp)
            self.assertIn("not in LAB6_ALLOWED_WRITE_ROOTS", blocked)
            with patch.dict(os.environ, {"LAB6_ALLOWED_WRITE_ROOTS": tmp}):
                created = create_text_file("test.txt", "Hello World", Path(tmp) / "generated", tmp)
            self.assertIn("Created", created)
            self.assertEqual((Path(tmp) / "test.txt").read_text(encoding="utf-8"), "Hello World")

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
    def test_calendar_read_uses_today_colombo_window(self):
        calendar = GoogleCalendar()
        service = Mock()
        today_at_ten = datetime.now(ZoneInfo("Asia/Colombo")).replace(
            hour=10, minute=0, second=0, microsecond=0
        ).isoformat()
        service.events.return_value.list.return_value.execute.return_value = {
            "items": [{"summary": "Study", "start": {"dateTime": today_at_ten}}]
        }
        calendar._service = lambda: service
        result = calendar.calendar_today()
        self.assertIn("Study", result)
        self.assertIn(today_at_ten, result)
        query = service.events.return_value.list.call_args.kwargs
        self.assertTrue(query["timeMin"].endswith("+05:30"))
        self.assertTrue(query["timeMax"].endswith("+05:30"))
        self.assertTrue(query["singleEvents"])

    def test_event_creation_uses_approved_iso_datetimes(self):
        calendar = GoogleCalendar(confirm=lambda _: True)
        service = Mock()
        service.events.return_value.insert.return_value.execute.return_value = {
            "summary": "Study", "id": "test-event-id"
        }
        calendar._service = lambda: service
        start = (datetime.now(ZoneInfo("Asia/Colombo")) + timedelta(days=1)).replace(
            hour=10, minute=0, second=0, microsecond=0
        )
        end = start + timedelta(minutes=30)
        result = calendar.create_calendar_event("Study", start.isoformat(), end.isoformat())
        self.assertIn("test-event-id", result)
        body = service.events.return_value.insert.call_args.kwargs["body"]
        self.assertEqual(body["start"]["timeZone"], "Asia/Colombo")
        self.assertEqual(body["end"]["timeZone"], "Asia/Colombo")

    def test_calendar_creation_requires_explicit_confirmation_before_auth(self):
        workspace = GoogleCalendar(confirm=lambda _: False)
        result = workspace.create_calendar_event(
            "Test", "2026-12-01T10:00:00+05:30", "2026-12-01T10:30:00+05:30"
        )
        self.assertIn("cancelled", result)
        self.assertIsNone(workspace._service_instance)

    def test_reversed_calendar_range_rejected(self):
        workspace = GoogleCalendar(confirm=lambda _: True)
        result = workspace.create_calendar_event(
            "Test", "2026-12-01T11:00:00+05:30", "2026-12-01T10:00:00+05:30"
        )
        self.assertIn("end time must be later", result)
        self.assertIsNone(workspace._service_instance)


if __name__ == "__main__":
    unittest.main()

