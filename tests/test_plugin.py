import ast
import pytest
from typing import List, Tuple, Type

from flake8_close_io_buffers.plugin import UnclosedIOChecker


def run_checker(source: str) -> List[Tuple[int, int, str, Type]]:
    """
    Parses the source code, runs the UnclosedIOChecker, and returns a list
    of error tuples.
    """
    tree = ast.parse(source)
    checker = UnclosedIOChecker(tree, filename="dummy.py")
    return list(checker.run())


# Two variants:
# 1. Using "import io" and then "io.BytesIO()"
# 2. Using a direct import "from io import BytesIO, StringIO" and then "BytesIO()"
IMPORT_VARIANTS = [
    ("import io", "io."),
    ("from io import BytesIO, StringIO", ""),
]


@pytest.mark.parametrize("import_line,prefix", IMPORT_VARIANTS)
def test_unassigned_bytesio(import_line: str, prefix: str) -> None:
    source = f"""{import_line}
def foo():
    {prefix}BytesIO()
"""
    errors = run_checker(source)
    assert len(errors) == 1
    _, _, message, _ = errors[0]
    assert "IO100 unclosed IO object instantiation not assigned to a variable" in message


@pytest.mark.parametrize("import_line,prefix", IMPORT_VARIANTS)
def test_unassigned_stringio(import_line: str, prefix: str) -> None:
    source = f"""{import_line}
def foo():
    {prefix}StringIO()
"""
    errors = run_checker(source)
    assert len(errors) == 1
    _, _, message, _ = errors[0]
    assert "IO100 unclosed IO object instantiation not assigned to a variable" in message


@pytest.mark.parametrize("import_line,prefix", IMPORT_VARIANTS)
def test_assigned_unclosed(import_line: str, prefix: str) -> None:
    source = f"""{import_line}
def foo():
    b = {prefix}BytesIO()
    s = {prefix}StringIO()
"""
    errors = run_checker(source)
    # Expect two errors (one for each unclosed variable)
    assert len(errors) == 2
    messages = [msg for _, _, msg, _ in errors]
    assert any("IO100 unclosed IO object 'b' is not closed" in msg for msg in messages)
    assert any("IO100 unclosed IO object 's' is not closed" in msg for msg in messages)


@pytest.mark.parametrize("import_line,prefix", IMPORT_VARIANTS)
def test_assigned_closed(import_line: str, prefix: str) -> None:
    source = f"""{import_line}
def foo():
    b = {prefix}BytesIO()
    b.close()
    s = {prefix}StringIO()
    s.close()
"""
    errors = run_checker(source)
    # No errors should be reported since both IO objects are closed.
    assert errors == []


@pytest.mark.parametrize("import_line,prefix", IMPORT_VARIANTS)
def test_with_context(import_line: str, prefix: str) -> None:
    source = f"""{import_line}
def foo():
    with {prefix}BytesIO() as b:
        pass
    with {prefix}StringIO() as s:
        pass
"""
    errors = run_checker(source)
    # With-statement context managers should prevent any errors.
    assert errors == []


@pytest.mark.parametrize("import_line,prefix", IMPORT_VARIANTS)
def test_multiple_assignment(import_line: str, prefix: str) -> None:
    source = f"""{import_line}
def foo():
    a, b = {prefix}BytesIO(), {prefix}StringIO()
    a.close()
"""
    errors = run_checker(source)
    # 'a' is closed, but 'b' is not; we expect one error for 'b'
    assert len(errors) == 1
    _, _, message, _ = errors[0]
    assert "IO100 unclosed IO object 'b' is not closed" in message
