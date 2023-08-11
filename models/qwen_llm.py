from typing import Any, Dict, List, Optional, Generator
from langchain.callbacks.manager import CallbackManagerForChainRun
from models.loader import LoaderCheckPoint
from models.chatglm_llm import ChatGLMLLMChain
from models.base import (AnswerResult,
                         AnswerResultStream,
                         AnswerResultQueueSentinelTokenListenerQueue)
# import torch
import transformers
import traceback


class QWenLLMChain(ChatGLMLLMChain):
    max_token: int = 10000
    temperature: float = 0.01
    # 相关度
    top_p = 0.4
    # 候选词数量
    top_k = 10
    checkPoint: LoaderCheckPoint = None
    # history = []
    history_len: int = 10
    streaming_key: str = "streaming"  #: :meta private:
    history_key: str = "history"  #: :meta private:
    prompt_key: str = "prompt"  #: :meta private:
    output_key: str = "answer_result_stream"  #: :meta private:

    def __init__(self, checkPoint: LoaderCheckPoint = None):
        super().__init__()
        self.checkPoint = checkPoint

    @property
    def _chain_type(self) -> str:
        return "QWenLLMChain"

    def _call(
            self,
            inputs: Dict[str, Any],
            run_manager: Optional[CallbackManagerForChainRun] = None,
    ) -> Dict[str, Generator]:
        generator = self.generatorAnswer(inputs=inputs, run_manager=run_manager)
        return {self.output_key: generator}

    def _warp_history(self, history):
        history = history[-self.history_len:-1] if self.history_len > 0 else []
        history = [[str(x), y] for x, y in history]
        return history

    def _generate_answer(self,
                         inputs: Dict[str, Any],
                         run_manager: Optional[CallbackManagerForChainRun] = None,
                         generate_with_callback: AnswerResultStream = None) -> None:

        try:
            history = inputs[self.history_key]
            streaming = inputs[self.streaming_key]
            prompt = inputs[self.prompt_key]
            if streaming:
                history += [[]]
                for inum, response in enumerate(self.checkPoint.model.chat_stream(
                        self.checkPoint.tokenizer,
                        prompt,
                        history=self._warp_history(history),
                )):
                    history[-1] = [prompt, response]
                    answer_result = AnswerResult()
                    answer_result.history = history
                    answer_result.llm_output = {"answer": response}
                    generate_with_callback(answer_result)
                self.checkPoint.clear_torch_cache()

            else:
                response, _ = self.checkPoint.model.chat(
                    self.checkPoint.tokenizer,
                    prompt,
                    history=self._warp_history(history),
                )
                self.checkPoint.clear_torch_cache()
                history += [[prompt, response]]
                answer_result = AnswerResult()
                answer_result.history = history
                answer_result.llm_output = {"answer": response}
                generate_with_callback(answer_result)
                self.checkPoint.clear_torch_cache()
        except Exception:
            traceback.print_exc()
