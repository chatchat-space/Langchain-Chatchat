
from abc import ABC
from typing import Any, Dict, Generator, List, Optional, Union

import torch
import transformers
from langchain.callbacks.manager import CallbackManagerForChainRun
from langchain.chains.base import Chain
from transformers.generation.logits_process import LogitsProcessor
from transformers.generation.utils import (LogitsProcessorList,
                                           StoppingCriteriaList)

from models.base import (AnswerResult,
                         AnswerResultStream, BaseAnswer)
from models.loader import LoaderCheckPoint


class ChatGLMCppLLMChain(BaseAnswer, Chain, ABC):
    checkPoint: LoaderCheckPoint = None
    streaming_key: str = "streaming"  #: :meta private:
    history_key: str = "history"  #: :meta private:
    prompt_key: str = "prompt"  #: :meta private:
    output_key: str = "answer_result_stream"  #: :meta private:

    max_length = 2048
    max_context_length = 512
    do_sample = True
    top_k = 0
    top_p = 0.7
    temperature = 0.95
    num_threads = 0

    def __init__(self, checkPoint: LoaderCheckPoint = None):
        super().__init__()
        self.checkPoint = checkPoint

    @property
    def _chain_type(self) -> str:
        return "ChatglmCppLLMChain"

    @property
    def input_keys(self) -> List[str]:
        """Will be whatever keys the prompt expects.

        :meta private:
        """
        return [self.prompt_key]

    @property
    def output_keys(self) -> List[str]:
        """Will always return text key.

        :meta private:
        """
        return [self.output_key]

    @property
    def _check_point(self) -> LoaderCheckPoint:
        return self.checkPoint

    def encode(self, prompt, truncation_length=None):
        input_ids = self.checkPoint.tokenizer.encode(str(prompt))
        return input_ids

    def decode(self, output_ids):
        reply = self.checkPoint.tokenizer.decode(output_ids)
        return reply

    def _call(
            self,
            inputs: Dict[str, Any],
            run_manager: Optional[CallbackManagerForChainRun] = None,
    ) -> Dict[str, Generator]:
        generator = self.generatorAnswer(inputs=inputs, run_manager=run_manager)
        return {self.output_key: generator}

    def _generate_answer(self,
                         inputs: Dict[str, Any],
                         run_manager: Optional[CallbackManagerForChainRun] = None,
                         generate_with_callback: AnswerResultStream = None) -> None:

        history = inputs[self.history_key] 
        streaming = inputs[self.streaming_key]
        prompt = inputs[self.prompt_key]
        print(f"__call:{prompt}")

        if prompt == "clear":
            history=[]
        
        local_history = []

        if not history:
            history =[]

        for k,v in history:
            if k:
                local_history.append(k)
                local_history.append(v)

        local_history.append(prompt)
        
        if streaming:
            history += [[]]
            pieces = []
            print(f"++++++++++++++Stream++++++++++++++++++++")
            for piece in self.checkPoint.model.stream_chat(
                local_history,
                max_length=self.max_length,
                max_context_length=self.max_context_length,
                do_sample=self.temperature > 0,
                top_k=self.top_k,
                top_p=self.top_p,
                temperature=self.temperature,
            ):  
                pieces.append(piece)
                reply = ''.join(pieces)
                print(f"{piece}",end='')

                answer_result = AnswerResult()
                history[-1] = [prompt, reply]
                answer_result.history = history
                answer_result.llm_output = {"answer": reply}
                generate_with_callback(answer_result)
            print("")
        else :
            reply = self.checkPoint.model.chat(
                local_history,
                max_length=self.max_length,
                max_context_length=self.max_context_length,
                do_sample=self.temperature > 0,
                top_k=self.top_k,
                top_p=self.top_p,
                temperature=self.temperature,
            )
            
            print(f"response:{reply}")
            print(f"+++++++++++++++++++++++++++++++++++")

            answer_result = AnswerResult()
            history.append([prompt, reply])
            answer_result.history = history
            answer_result.llm_output = {"answer": reply}
            generate_with_callback(answer_result)
