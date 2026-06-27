"""Regression tests for #5482: _get_file_path must not allow a crafted
(base64) file_id to escape the openai_files directory.

Run (with chatchat-server installed):
    pytest test_openai_files_path_traversal.py -v
"""
import base64

import pytest
from fastapi import HTTPException

from chatchat.settings import Settings
from chatchat.server.api_server.openai_routes import _get_file_path


def _b64(s: str) -> str:
    return base64.urlsafe_b64encode(s.encode()).decode()


@pytest.fixture
def temp_base(tmp_path, monkeypatch):
    monkeypatch.setattr(Settings.basic_settings, "BASE_TEMP_DIR", str(tmp_path))
    return tmp_path


@pytest.mark.parametrize(
    "evil",
    [
        "/etc/passwd",                       # absolute -> os.path.join drops the base dir
        "../../../../etc/passwd",            # parent traversal
        "assistants/../../../../etc/shadow", # traversal after a valid-looking prefix
    ],
)
def test_traversal_file_id_rejected(temp_base, evil):
    with pytest.raises(HTTPException):
        _get_file_path(_b64(evil))


def test_legit_file_id_resolves_inside_root(temp_base):
    root = (temp_base / "openai_files").resolve()
    path = _get_file_path(_b64("assistants/2026-06-27/report.txt"))
    assert str(root) == str(root) and str(path).startswith(str(root))
    assert path.endswith("report.txt")
