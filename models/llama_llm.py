
from abc import ABC
from langchain.chains.base import Chain
from typing import Any, Dict, List, Optional, Generator, Union
from langchain.callbacks.manager import CallbackManagerForChainRun
from transformers.generation.logits_process import LogitsProcessor
from transformers.generation.utils import LogitsProcessorList, StoppingCriteriaList
from models.loader import LoaderCheckPoint
from models.base import (BaseAnswer,
                         AnswerResult,
                         AnswerResultStream,
                         AnswerResultQueueSentinelTokenListenerQueue)
import torch
import transformers


class InvalidScoreLogitsProcessor(LogitsProcessor):
    def __call__(self, input_ids: Union[torch.LongTensor, list],
                 scores: Union[torch.FloatTensor, list]) -> torch.FloatTensor:
        # llama-cpp模型返回的是list,为兼容性考虑，需要判断input_ids和scores的类型，将list转换为torch.Tensor
        input_ids = torch.tensor(input_ids) if isinstance(input_ids, list) else input_ids
        scores = torch.tensor(scores) if isinstance(scores, list) else scores
        if torch.isnan(scores).any() or torch.isinf(scores).any():
            scores.zero_()
            scores[..., 5] = 5e4
        return scores


class LLamaLLMChain(BaseAnswer, Chain, ABC):
    checkPoint: LoaderCheckPoint = None
    # history = []
    history_len: int = 3
    max_new_tokens: int = 500
    num_beams: int = 1
    temperature: float = 0.5
    top_p: float = 0.4
    top_k: int = 10
    repetition_penalty: float = 1.2
    encoder_repetition_penalty: int = 1
    min_length: int = 0
    logits_processor: LogitsProcessorList = None
    stopping_criteria: Optional[StoppingCriteriaList] = None
    streaming_key: str = "streaming"  #: :meta private:
    history_key: str = "history"  #: :meta private:
    prompt_key: str = "prompt"  #: :meta private:
    output_key: str = "answer_result_stream"  #: :meta private:

    def __init__(self, checkPoint: LoaderCheckPoint = None):
        super().__init__()
        self.checkPoint = checkPoint

    @property
    def _chain_type(self) -> str:
        return "LLamaLLMChain"

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

    def encode(self, prompt, add_special_tokens=True, add_bos_token=True, truncation_length=None):
        input_ids = self.checkPoint.tokenizer.encode(str(prompt), return_tensors='pt',
                                                     add_special_tokens=add_special_tokens)
        # This is a hack for making replies more creative.
        if not add_bos_token and input_ids[0][0] == self.checkPoint.tokenizer.bos_token_id:
            input_ids = input_ids[:, 1:]

        # Llama adds this extra token when the first character is '\n', and this
        # compromises the stopping criteria, so we just remove it
        if type(self.checkPoint.tokenizer) is transformers.LlamaTokenizer and input_ids[0][0] == 29871:
            input_ids = input_ids[:, 1:]

        # Handling truncation
        if truncation_length is not None:
            input_ids = input_ids[:, -truncation_length:]

        return input_ids.cuda()

    def decode(self, output_ids):
        reply = self.checkPoint.tokenizer.decode(output_ids, skip_special_tokens=True)
        return reply

    # 将历史对话数组转换为文本格式
    def history_to_text(self, query, history):
        """
        历史对话软提示
            这段代码首先定义了一个名为 history_to_text 的函数，用于将 self.history
            数组转换为所需的文本格式。然后，我们将格式化后的历史文本
            再用 self.encode 将其转换为向量表示。最后，将历史对话向量与当前输入的对话向量拼接在一起。
        :return:
        """
        formatted_history = ''
        history = history[-self.history_len:] if self.history_len > 0 else []
        if len(history) > 0:
            for i, (old_query, response) in enumerate(history):
                formatted_history += "### Human：{}\n### Assistant：{}\n".format(old_query, response)
        formatted_history += "### Human：{}\n### Assistant：".format(query)
        return formatted_history

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

        # Create the StoppingCriteriaList with the stopping strings
        self.stopping_criteria = transformers.StoppingCriteriaList()
        # 定义模型stopping_criteria 队列，在每次响应时将 torch.LongTensor, torch.FloatTensor同步到AnswerResult
        listenerQueue = AnswerResultQueueSentinelTokenListenerQueue()
        self.stopping_criteria.append(listenerQueue)
        # TODO 需要实现chat对话模块和注意力模型，目前_call为langchain的LLM拓展的api，默认为无提示词模式，如果需要操作注意力模型，可以参考chat_glm的实现
        soft_prompt = self.history_to_text(query=prompt, history=history)
        if self.logits_processor is None:
            self.logits_processor = LogitsProcessorList()
        self.logits_processor.append(InvalidScoreLogitsProcessor())

        gen_kwargs = {
            "max_new_tokens": self.max_new_tokens,
            "num_beams": self.num_beams,
            "top_p": self.top_p,
            "do_sample": True,
            "top_k": self.top_k,
            "repetition_penalty": self.repetition_penalty,
            "encoder_repetition_penalty": self.encoder_repetition_penalty,
            "min_length": self.min_length,
            "temperature": self.temperature,
            "eos_token_id": self.checkPoint.tokenizer.eos_token_id,
            "logits_processor": self.logits_processor}

        #  向量转换
        input_ids = self.encode(soft_prompt, add_bos_token=self.checkPoint.tokenizer.add_bos_token,
                                truncation_length=self.max_new_tokens)

        gen_kwargs.update({'inputs': input_ids})
        # 观测输出
        gen_kwargs.update({'stopping_criteria': self.stopping_criteria})
        # llama-cpp模型的参数与transformers的参数字段有较大差异，直接调用会返回不支持的字段错误
        # 因此需要先判断模型是否是llama-cpp模型，然后取gen_kwargs与模型generate方法字段的交集
        # 仅将交集字段传给模型以保证兼容性
        # todo llama-cpp模型在本框架下兼容性较差，后续可以考虑重写一个llama_cpp_llm.py模块
        if "llama_cpp" in self.checkPoint.model.__str__():
            import inspect

            common_kwargs_keys = set(inspect.getfullargspec(self.checkPoint.model.generate).args) & set(
                gen_kwargs.keys())
            common_kwargs = {key: gen_kwargs[key] for key in common_kwargs_keys}
            # ? llama-cpp模型的generate方法似乎只接受.cpu类型的输入，响应很慢，慢到哭泣
            # ?为什么会不支持GPU呢，不应该啊？
            output_ids = torch.tensor(
                [list(self.checkPoint.model.generate(input_id_i.cpu(), **common_kwargs)) for input_id_i in input_ids])

        else:
            output_ids = self.checkPoint.model.generate(**gen_kwargs)
        new_tokens = len(output_ids[0]) - len(input_ids[0])
        reply = self.decode(output_ids[0][-new_tokens:])
        print(f"response:{reply}")
        print(f"+++++++++++++++++++++++++++++++++++")

        answer_result = AnswerResult()
        history += [[prompt, reply]]
        answer_result.history = history
        answer_result.llm_output = {"answer": reply}
        generate_with_callback(answer_result)
