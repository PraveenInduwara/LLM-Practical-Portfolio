from __future__ import annotations

import ast
import ctypes
import math
import os
import platform
import re
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from langchain_core.tools import tool

from .google_integrations import GoogleCalendar
from .memory import SQLiteMemory
from .rag import Lab5KnowledgeBase


def calculate(expression: str) -> str:
    """Safely evaluate basic arithmetic without exposing Python builtins."""
    expression = expression.replace("×", "*").replace("÷", "/").replace("^", "**").strip()
    if len(expression) > 160:
        raise ValueError("Expression is too long.")
    try:
        tree = ast.parse(expression, mode="eval")
    except SyntaxError as exc:
        raise ValueError("Use a valid arithmetic expression, such as (25 * 4) / 2.") from exc

    def visit(node):
        if isinstance(node, ast.Expression):
            return visit(node.body)
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)) and not isinstance(node.value, bool):
            return node.value
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub)):
            value = visit(node.operand)
            return value if isinstance(node.op, ast.UAdd) else -value
        if isinstance(node, ast.BinOp) and isinstance(node.op, (ast.Add, ast.Sub, ast.Mult, ast.Div, ast.FloorDiv, ast.Mod, ast.Pow)):
            left, right = visit(node.left), visit(node.right)
            if isinstance(node.op, ast.Pow) and (abs(right) > 12 or abs(left) > 1_000_000):
                raise ValueError("Exponentiation is limited to keep calculations safe.")
            result = {
                ast.Add: lambda: left + right,
                ast.Sub: lambda: left - right,
                ast.Mult: lambda: left * right,
                ast.Div: lambda: left / right,
                ast.FloorDiv: lambda: left // right,
                ast.Mod: lambda: left % right,
                ast.Pow: lambda: left ** right,
            }[type(node.op)]()
            if not math.isfinite(float(result)) or abs(result) > 1e100:
                raise ValueError("The result is outside the supported numeric range.")
            return result
        raise ValueError("Only numbers and +, -, *, /, //, %, and ** operations are allowed.")

    try:
        result = visit(tree)
    except ZeroDivisionError:
        raise ValueError("Cannot divide by zero.") from None
    if isinstance(result, float) and result.is_integer():
        result = int(result)
    return str(result)


def current_datetime() -> str:
    now = datetime.now(ZoneInfo("Asia/Colombo"))
    return now.strftime("%A, %Y-%m-%d %H:%M:%S %Z (UTC%z)")


def search_files(directory: str, pattern: str, max_results: int = 50) -> str:
    """Read-only filename/extension search, bounded to configured allowed roots."""
    root = Path(directory).expanduser()
    if not root.exists():
        return f"Directory does not exist: {root}"
    if not root.is_dir():
        return f"Not a directory: {root}"
    if not pattern.strip():
        return "Provide a file name fragment or extension such as '.pdf'."
    resolved = root.resolve()
    allowed_env = os.getenv("LAB6_ALLOWED_SEARCH_ROOTS", "")
    allowed = [Path(item).expanduser().resolve() for item in allowed_env.split(os.pathsep) if item.strip()]
    if allowed and not any(resolved == base or base in resolved.parents for base in allowed):
        return "Search blocked: directory is outside LAB6_ALLOWED_SEARCH_ROOTS."
    pattern = pattern.casefold().strip()
    limit = max(1, min(int(max_results), 100))
    results = []
    try:
        for candidate in resolved.rglob("*"):
            if candidate.is_file() and not candidate.is_symlink() and pattern in candidate.name.casefold():
                results.append(str(candidate))
                if len(results) >= limit:
                    break
    except (PermissionError, OSError) as exc:
        return f"Search was incomplete: {exc}"
    if not results:
        return f"No files matching {pattern!r} were found under {resolved}."
    suffix = " (result limit reached)" if len(results) == limit else ""
    return "\n".join(results) + suffix


def create_text_file(filename: str, content: str, output_directory: str | Path,
                     directory: str | Path | None = None) -> str:
    """Create a .txt file in generated output or an explicitly allowed existing folder."""
    name = Path(filename).name
    if name != filename or name in {"", ".", ".."} or "/" in filename or "\\" in filename:
        return "File was not created: provide a simple filename without directory components."
    if Path(name).suffix.lower() != ".txt":
        return "File was not created: only .txt files are accepted."
    if directory is None or not str(directory).strip():
        target_root = Path(output_directory).resolve()
        target_root.mkdir(parents=True, exist_ok=True)
    else:
        requested_root = Path(directory).expanduser()
        if not requested_root.is_dir():
            return f"File was not created: target directory does not exist: {requested_root}."
        target_root = requested_root.resolve()
        allowed_roots = [
            Path(item.strip()).expanduser().resolve()
            for item in os.getenv("LAB6_ALLOWED_WRITE_ROOTS", "").split(os.pathsep)
            if item.strip()
        ]
        if not any(target_root == allowed or allowed in target_root.parents for allowed in allowed_roots):
            return (
                "File was not created: target directory is not in LAB6_ALLOWED_WRITE_ROOTS. "
                "Add an existing, trusted folder there before retrying."
            )
    target = (target_root / name).resolve()
    if target.parent != target_root:
        return "File was not created: path escapes the allowed output folder."
    if target.exists():
        return f"File was not created: {target} already exists; existing files are not overwritten."
    target.write_text(content, encoding="utf-8", newline="\n")
    return f"Created {target} ({target.stat().st_size} bytes)."


def system_information() -> str:
    info = [f"Operating system: {platform.platform()}", f"Processor: {platform.processor() or platform.machine()}",
            f"Architecture: {platform.architecture()[0]}", f"Python: {platform.python_version()}"]
    if sys.platform == "win32":
        class MEMORYSTATUSEX(ctypes.Structure):
            _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
                        ("ullTotalPhys", ctypes.c_ulonglong), ("ullAvailPhys", ctypes.c_ulonglong),
                        ("ullTotalPageFile", ctypes.c_ulonglong), ("ullAvailPageFile", ctypes.c_ulonglong),
                        ("ullTotalVirtual", ctypes.c_ulonglong), ("ullAvailVirtual", ctypes.c_ulonglong),
                        ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]
        status = MEMORYSTATUSEX()
        status.dwLength = ctypes.sizeof(status)
        if ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status)):
            info.append(f"Physical memory: {status.ullTotalPhys / (1024 ** 3):.2f} GiB total, {status.ullAvailPhys / (1024 ** 3):.2f} GiB available")
    return "\n".join(info)


def open_notepad_with_text(text: str) -> str:
    """Open Windows Notepad and type ASCII text into its window."""
    if sys.platform != "win32":
        return "Notepad tool is available only on Windows."
    if not text.isascii():
        return "Notepad tool currently accepts ASCII text only."
    try:
        import pyautogui
        import pygetwindow
    except ImportError:
        return "Install the optional UI tools with: python -m pip install pyautogui pygetwindow"
    subprocess.Popen(["notepad.exe"], close_fds=True)
    time.sleep(1.5)
    windows = pygetwindow.getWindowsWithTitle("Notepad") or pygetwindow.getWindowsWithTitle("Untitled")
    if not windows:
        return "Notepad opened, but its window was not found; text was not typed."
    windows[0].activate()
    time.sleep(0.3)
    pyautogui.write(text, interval=0.02)
    return "Opened Notepad and typed the requested text."


def open_windows_calculator(expression: str) -> str:
    """Display a calculation in the Windows Calculator app when available."""
    if sys.platform != "win32":
        return "The calculation was performed by the Python calculator tool; Windows Calculator is unavailable on this OS."
    try:
        import pyautogui
        import pygetwindow
    except ImportError:
        return "The calculation was performed by Python; install pyautogui and pygetwindow to show Windows Calculator."
    display_expression = re.sub(r"\s+", "", expression).replace("**", "^")
    if not re.fullmatch(r"[0-9.+*/%()^\-]+", display_expression):
        return "The calculation was performed by Python; this expression could not safely be sent to Windows Calculator."
    try:
        subprocess.Popen(["calc.exe"], close_fds=True)
        time.sleep(1.5)
        windows = pygetwindow.getWindowsWithTitle("Calculator")
        if not windows:
            return "The calculation was performed by Python; Windows Calculator opened but its window was not detected."
        windows[0].activate()
        time.sleep(0.2)
        pyautogui.write(display_expression, interval=0.03)
        pyautogui.press("enter")
        return "Displayed the expression in Windows Calculator."
    except Exception as exc:
        return f"The calculation was performed by Python; Windows Calculator UI failed: {type(exc).__name__}: {exc}"


def build_tools(memory: SQLiteMemory, session_id: str, rag: Lab5KnowledgeBase,
                workspace: str | Path, confirm_google=None):
    workspace = Path(workspace).resolve()
    output_dir = workspace / "data" / "generated"
    google = GoogleCalendar(confirm=confirm_google)

    @tool
    def calculator(expression: str) -> str:
        """Calculate arithmetic, for example '25 * 4'."""
        try:
            result = calculate(expression)
            if os.getenv("LAB6_SHOW_CALCULATOR", "1").strip().casefold() not in {"0", "false", "no", "off"}:
                display_result = open_windows_calculator(expression)
                return f"{result} ({display_result})"
            return result
        except ValueError as exc:
            return f"Calculation error: {exc}"

    @tool
    def date_time() -> str:
        """Get the current date and time in Asia/Colombo."""
        return current_datetime()

    @tool
    def notepad(text: str) -> str:
        """Open Windows Notepad and type the supplied text."""
        return open_notepad_with_text(text)

    @tool
    def file_search(directory: str, pattern: str) -> str:
        """Search files read-only by a filename fragment or extension in a directory."""
        return search_files(directory, pattern)

    @tool
    def create_file(filename: str, content: str, directory: str = "") -> str:
        """Create a .txt file in Lab 6 output or in a configured allowed directory."""
        return create_text_file(filename, content, output_dir, directory or None)

    @tool
    def calendar_today() -> str:
        """Read today's Google Calendar events in Asia/Colombo."""
        try:
            return google.calendar_today()
        except Exception as exc:
            return f"Google Calendar could not be read: {type(exc).__name__}: {exc}"

    @tool
    def create_calendar_event(summary: str, start: str, end: str, description: str = "") -> str:
        """Create a Google Calendar event only after explicit interactive approval. Use ISO-8601 datetimes."""
        try:
            return google.create_calendar_event(summary, start, end, description)
        except Exception as exc:
            return f"Google Calendar event failed: {type(exc).__name__}: {exc}"

    @tool
    def system_info() -> str:
        """Show operating system, processor, architecture, Python version, and available physical memory."""
        return system_information()

    @tool
    def remember_information(fact: str) -> str:
        """Save useful user-provided information to persistent SQLite memory."""
        return memory.remember(session_id, fact)

    @tool
    def search_memory(query: str) -> str:
        """Search earlier conversation turns and saved facts for this chat session."""
        return memory.search(session_id, query)

    @tool
    def rag_search(query: str) -> str:
        """Find relevant passages in configured university PDF documents using Lab 5's RAG pipeline."""
        return rag.search(query)

    return [calculator, date_time, notepad, file_search, create_file, system_info,
            remember_information, search_memory, rag_search, calendar_today,
            create_calendar_event]

