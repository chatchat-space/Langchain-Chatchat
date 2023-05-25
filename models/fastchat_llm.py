from abc import ABC
import requests
import json
from typing import Optional, List
from langchain.llms.base import LLM

from models.loader import LoaderCheckPoint
from models.base import (BaseAnswer,
                         AnswerResult)


class FastChatLLM(BaseAnswer, LLM, ABC):
    max_token: int = 2048
    temperature: float = 0
    top_p = 0.3
    checkPoint: LoaderCheckPoint = None
    # history = []
    history_len: int = 10

    def __init__(self, checkPoint: LoaderCheckPoint = None):
        super().__init__()
        self.checkPoint = checkPoint

    @property
    def _llm_type(self) -> str:
        return "FastChat"

    @property
    def _check_point(self) -> LoaderCheckPoint:
        return self.checkPoint

    @property
    def _history_len(self) -> int:
        return self.history_len

    def set_history_len(self, history_len: int = 10) -> None:
        self.history_len = history_len

    def _call(self, prompt: str, stop: Optional[List[str]] = None) -> str:
        pass

    def generatorAnswer(self, prompt: str,
                         history: List[List[str]] = [],
                         streaming: bool = False):


        host = "http://localhost:8000"
        data = {
              "model": "vicuna-7b-v1.1",
              "prompt": prompt,
              "max_tokens":512,
              "temperature": self.temperature,
              "stream": streaming
            }

        print(data)

        import time
        start = time.time()


        r = requests.post('%s/v1/completions' % host, json=data, stream=streaming)

        print("use time: %ss" % (time.time() - start))
        print("streaming %s" % streaming)

        if not streaming:
            resp = r.json()
            if not resp.get('choices'):
                response = str(resp)
            else:
                response = resp['choices'][0]['text']
            if history:
                history += [[prompt, response]]
            answer_result = AnswerResult()
            answer_result.history = history
            answer_result.llm_output = {"answer": response}

            yield answer_result
        else:
            for line in r.iter_lines(decode_unicode=True):
                if not line: continue
                over = "[DONE]" in line
                if not over:
                    resp = json.loads(line[6:])
                    if not resp.get('choices'):
                        response = str(resp)
                    else:
                        response = resp['choices'][0]['text']

                if not over and response:
                    if history:
                        history += [[prompt, response]]
                        answer_result.history = history
                    answer_result = AnswerResult()
                    answer_result.llm_output = {"answer": response}

                    yield answer_result

                history = []

                if over:
                    break
