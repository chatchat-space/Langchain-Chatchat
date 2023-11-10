import sys
from pathlib import Path
root_path = Path(__file__).parent.parent.parent
sys.path.append(str(root_path))

from server.model_workers.baichuan import request_baichuan_api
from pprint import pprint


def test_qwen():
    messages = [{"role": "user", "content": "hello"}]

    for x in request_baichuan_api(messages):
        print(type(x))
        pprint(x)
        assert x["code"] == 0