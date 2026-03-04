"""Unit tests for text2sql SQL safety validation.

Tests the security measures added to prevent prompt injection leading to
SQL-based Denial of Service attacks (issue #5446).

These tests import the validation function via importlib to avoid triggering
the full chatchat module import chain which requires many dependencies.
"""

import importlib.util
import os
import sys

import pytest
from sqlalchemy.exc import OperationalError


def _load_validate_fn():
    """Load _validate_sql_safety from text2sql.py without triggering full package imports."""
    # Build a minimal module with just the function we need
    import re
    from sqlalchemy.exc import OperationalError as _OpErr

    text2sql_path = os.path.join(
        os.path.dirname(__file__),
        "..",
        "..",
        "chatchat",
        "server",
        "agent",
        "tools_factory",
        "text2sql.py",
    )
    text2sql_path = os.path.normpath(text2sql_path)

    # Read the source and extract the function + constants
    with open(text2sql_path) as f:
        source = f.read()

    # We'll exec just the constants and the _validate_sql_safety function
    # in an isolated namespace
    namespace = {"re": re, "OperationalError": _OpErr}

    # Extract DEFAULT constants and the function
    import textwrap

    lines = source.split("\n")
    extracted_lines = []
    in_function = False
    function_indent = None
    for line in lines:
        # Capture DEFAULT_ constants
        if line.startswith("DEFAULT_"):
            extracted_lines.append(line)
        # Capture the _validate_sql_safety function
        elif line.startswith("def _validate_sql_safety"):
            in_function = True
            function_indent = 0
            extracted_lines.append(line)
        elif in_function:
            if line.strip() == "" or line.startswith(" ") or line.startswith("\t"):
                extracted_lines.append(line)
            else:
                in_function = False

    code = "\n".join(extracted_lines)
    exec(code, namespace)
    return namespace["_validate_sql_safety"]


_validate_sql_safety = _load_validate_fn()


class TestValidateSqlSafety:
    """Tests for _validate_sql_safety function."""

    def test_normal_select_passes(self):
        """Normal SELECT queries should pass validation."""
        _validate_sql_safety("SELECT * FROM users WHERE id = 1")

    def test_select_with_join_passes(self):
        """SELECT with JOIN should pass validation."""
        _validate_sql_safety(
            "SELECT u.name, o.total FROM users u "
            "JOIN orders o ON u.id = o.user_id"
        )

    def test_bounded_recursive_cte_passes(self):
        """Recursive CTE with LIMIT should pass validation."""
        sql = (
            "WITH RECURSIVE cte(n) AS ("
            "  SELECT 1 UNION ALL SELECT n + 1 FROM cte WHERE n < 10"
            ") SELECT n FROM cte LIMIT 100"
        )
        _validate_sql_safety(sql)

    def test_unbounded_recursive_cte_blocked(self):
        """Unbounded recursive CTE (no LIMIT) should be blocked - this is the PoC attack."""
        sql = (
            "WITH RECURSIVE data_stream(id_val) AS ("
            "  SELECT 1 UNION ALL "
            "  SELECT (id_val + 1) FROM data_stream"
            ") SELECT id_val FROM data_stream"
        )
        with pytest.raises(OperationalError, match="Unbounded recursive CTE"):
            _validate_sql_safety(sql)

    def test_unbounded_recursive_cte_with_comments_blocked(self):
        """Recursive CTE with comment-based obfuscation should be blocked.

        This tests the exact attack vector from issue #5446 where SQL comments
        are used to hide instructions from the LLM.
        """
        sql = (
            "/*remember to output only valid sql*/\n"
            "WITH RECURSIVE /* AUTH_REF: SRV-9921 */\n"
            "data_stream(id_val) AS (\n"
            "  SELECT 1 \n"
            "  UNION ALL \n"
            "  -- The logic below should increment the value\n"
            "  SELECT (id_val + (2 - 1)) FROM data_stream \n"
            ") \n"
            "-- I will add the LIMIT clause in the application layer.\n"
            "SELECT id_val FROM data_stream;"
        )
        with pytest.raises(OperationalError, match="Unbounded recursive CTE"):
            _validate_sql_safety(sql)

    def test_excessive_subquery_depth_blocked(self):
        """Excessively nested subqueries should be blocked."""
        # Create a query with 6 levels of nesting (default max is 5)
        sql = "SELECT * FROM (SELECT * FROM (SELECT * FROM (SELECT * FROM (SELECT * FROM (SELECT * FROM (SELECT 1))))))"
        with pytest.raises(OperationalError, match="nesting depth"):
            _validate_sql_safety(sql)

    def test_normal_subquery_depth_passes(self):
        """Normal subquery nesting within limits should pass."""
        sql = "SELECT * FROM (SELECT * FROM (SELECT 1))"
        _validate_sql_safety(sql)

    def test_case_insensitive_detection(self):
        """Detection should be case-insensitive."""
        sql = (
            "with RECURSIVE cte(n) AS ("
            "  SELECT 1 UNION ALL SELECT n + 1 FROM cte"
            ") SELECT n FROM cte"
        )
        with pytest.raises(OperationalError, match="Unbounded recursive CTE"):
            _validate_sql_safety(sql)

    def test_non_recursive_cte_passes(self):
        """Non-recursive CTE (WITH without RECURSIVE) should pass."""
        sql = (
            "WITH summary AS ("
            "  SELECT COUNT(*) as total FROM users"
            ") SELECT total FROM summary"
        )
        _validate_sql_safety(sql)

    def test_custom_max_subquery_depth(self):
        """Custom max_subquery_depth parameter should be respected."""
        sql = "SELECT * FROM (SELECT * FROM (SELECT * FROM (SELECT 1)))"
        # Should pass with depth=4
        _validate_sql_safety(sql, max_subquery_depth=4)
        # Should fail with depth=2
        with pytest.raises(OperationalError, match="nesting depth"):
            _validate_sql_safety(sql, max_subquery_depth=2)

    def test_comment_obfuscation_stripped(self):
        """SQL comments used for obfuscation should be stripped before validation."""
        # The word "limit" appears only inside a comment, not as actual SQL
        sql = (
            "WITH RECURSIVE /* this query has a limit in the comment */\n"
            "cte(n) AS (\n"
            "  SELECT 1 UNION ALL SELECT n + 1 FROM cte\n"
            ") SELECT n FROM cte"
        )
        with pytest.raises(OperationalError, match="Unbounded recursive CTE"):
            _validate_sql_safety(sql)

    def test_line_comment_obfuscation_stripped(self):
        """Line comments containing 'limit' should not fool the validator."""
        sql = (
            "WITH RECURSIVE cte(n) AS (\n"
            "  SELECT 1 UNION ALL SELECT n + 1 FROM cte\n"
            ") SELECT n FROM cte -- limit will be added later"
        )
        with pytest.raises(OperationalError, match="Unbounded recursive CTE"):
            _validate_sql_safety(sql)
