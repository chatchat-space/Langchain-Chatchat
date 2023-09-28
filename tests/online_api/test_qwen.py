import sys
from pathlib import Path
root_path = Path(__file__).parent.parent.parent
sys.path.append(str(root_path))

from server.model_workers.qwen import request_qwen_api
from pprint import pprint
import pytest


@pytest.mark.parametrize("version", ["qwen-turbo"])
def test_qwen(version):
    messages = [{"role": "user", "content": "hello"}]
    print("\n" + version + "\n")

    for x in request_qwen_api(messages, version=version):
        print(type(x))
        pprint(x)
        assert x["code"] == 200
