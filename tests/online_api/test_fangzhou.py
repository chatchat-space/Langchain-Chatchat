import sys
from pathlib import Path
root_path = Path(__file__).parent.parent.parent
sys.path.append(str(root_path))

from server.model_workers.fangzhou import request_volc_api
from pprint import pprint
import pytest


@pytest.mark.parametrize("version", ["chatglm-6b-model"])
def test_qianfan(version):
    messages = [{"role": "user", "content": "hello"}]
    print("\n" + version + "\n")
    i = 1
    for x in request_volc_api(messages, version=version):
        print(type(x))
        pprint(x)
        if chunk := x.choice.message.content:
            print(chunk)
        assert x.choice.message
        i += 1
