import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))

from pprint import pprint

import requests

from chatchat.server.utils import api_address

api_base_url = f"{api_address()}/tools"


def test_tool_list():
    resp = requests.get(api_base_url)
    assert resp.status_code == 200
    data = resp.json()["data"]
    pprint(data)
    assert "calculate" in data


def test_tool_call():
    data = {
        "name": "calculate",
        "kwargs": {"a": 1, "b": 2, "operator": "+"},
    }
    resp = requests.post(f"{api_base_url}/call", json=data)
    assert resp.status_code == 200
    data = resp.json()["data"]
    pprint(data)
    assert data == 3
