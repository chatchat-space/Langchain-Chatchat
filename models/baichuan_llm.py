from abc import ABC
from langchain.llms.base import LLM
from typing import Optional, List
from models.loader import LoaderCheckPoint
from models.base import (BaseAnswer,
                         AnswerResult)

class BaichuanLLMChain(BaseAnswer, LLM, ABC):
    max_token: int = 10000
    temperature: float = 0.01
    top_p = 0.9
    checkPoint: LoaderCheckPoint = None
    # history = []
    history_len: int = 10

    def __init__(self, checkPoint: LoaderCheckPoint = None):
        super().__init__()
        self.checkPoint = checkPoint

    @property
    def _llm_type(self) -> str:
        return "BaichuanLLMChain"

    @property
    def _check_point(self) -> LoaderCheckPoint:
        return self.checkPoint

    @property
    def _history_len(self) -> int:
        return self.history_len

    def set_history_len(self, history_len: int = 10) -> None:
        self.history_len = history_len

    def _call(self, prompt: str, stop: Optional[List[str]] = None) -> str:
        print(f"__call:{prompt}")
        response, _ = self.checkPoint.model.chat(
            self.checkPoint.tokenizer,
            prompt,
            # history=[],
            # max_length=self.max_token,
            # temperature=self.temperature
        )
        print(f"response:{response}")
        print(f"+++++++++++++++++++++++++++++++++++")
        return response

    def _generate_answer(self, prompt: str,
                         history: List[List[str]] = [],
                         streaming: bool = False):
        messages = []
        messages.append({"role": "user", "content": prompt})
        if streaming:
            for inum, stream_resp in enumerate(self.checkPoint.model.chat(
                    self.checkPoint.tokenizer,
                    messages,
                    stream=True
            )):
                self.checkPoint.clear_torch_cache()
                answer_result = AnswerResult()
                answer_result.llm_output = {"answer": stream_resp}
                yield answer_result
        else:
            response = self.checkPoint.model.chat(
                self.checkPoint.tokenizer,
                messages
            )
            self.checkPoint.clear_torch_cache()
            answer_result = AnswerResult()
            answer_result.llm_output = {"answer": response}
            yield answer_result