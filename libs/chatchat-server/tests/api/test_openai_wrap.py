import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

import requests

import openai

from chatchat.configs import DEFAULT_LLM_MODEL, DEFAULT_EMBEDDING_MODEL
from chatchat.server.utils import api_address


api_base_url = f"{api_address()}/v1"
client = openai.Client(
    api_key="EMPTY",
    base_url=api_base_url,
)

def test_chat():
    resp = client.chat.completions.create(
        messages=[{"role": "user", "content": "你是谁"}],
        model=DEFAULT_LLM_MODEL,
    )
    print(resp)
    assert hasattr(resp, "choices") and len(resp.choices) > 0


def test_embeddings():
    resp = client.embeddings.create(input="你是谁", model=DEFAULT_EMBEDDING_MODEL)
    print(resp)
    assert hasattr(resp, "data") and len(resp.data) > 0
