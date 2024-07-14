import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))

import openai
import requests

from chatchat.server.utils import api_address, get_default_llm, get_default_embedding

api_base_url = f"{api_address()}/v1"
client = openai.Client(
    api_key="EMPTY",
    base_url=api_base_url,
)


def test_chat():
    resp = client.chat.completions.create(
        messages=[{"role": "user", "content": "你是谁"}],
        model=get_default_llm(),
    )
    print(resp)
    assert hasattr(resp, "choices") and len(resp.choices) > 0


def test_embeddings():
    resp = client.embeddings.create(input="你是谁", model=get_default_embedding())
    print(resp)
    assert hasattr(resp, "data") and len(resp.data) > 0
