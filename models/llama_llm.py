from abc import ABC

from langchain.llms.base import LLM
import random
import torch
import transformers
from transformers.generation.logits_process import LogitsProcessor
from transformers.generation.utils import LogitsProcessorList, StoppingCriteriaList
from typing import Optional, List, Dict, Any
from models.loader import LoaderCheckPoint
from models.base import (BaseAnswer,
                         AnswerResult)


class InvalidScoreLogitsProcessor(LogitsProcessor):
    def __call__(self, input_ids: torch.LongTensor, scores: torch.FloatTensor) -> torch.FloatTensor:
        if torch.isnan(scores).any() or torch.isinf(scores).any():
            scores.zero_()
            scores[..., 5] = 5e4
        return scores


class LLamaLLM(BaseAnswer, LLM, ABC):
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
    eos_token_id: Optional[int] = [2]

    state: object = {'max_new_tokens': 50,
                     'seed': 1,
                     'temperature': 0, 'top_p': 0.1,
                     'top_k': 40, 'typical_p': 1,
                     'repetition_penalty': 1.2,
                     'encoder_repetition_penalty': 1,
                     'no_repeat_ngram_size': 0,
                     'min_length': 0,
                     'penalty_alpha': 0,
                     'num_beams': 1,
                     'length_penalty': 1,
                     'early_stopping': False, 'add_bos_token': True, 'ban_eos_token': False,
                     'truncation_length': 2048, 'custom_stopping_strings': '',
                     'cpu_memory': 0, 'auto_devices': False, 'disk': False, 'cpu': False, 'bf16': False,
                     'load_in_8bit': False, 'wbits': 'None', 'groupsize': 'None', 'model_type': 'None',
                     'pre_layer': 0, 'gpu_memory_0': 0}

    def __init__(self, checkPoint: LoaderCheckPoint = None):
        super().__init__()
        self.checkPoint = checkPoint

    @property
    def _llm_type(self) -> str:
        return "LLamaLLM"

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

    def prepare_inputs_for_generation(self,
                                      input_ids: torch.LongTensor):
        """
        预生成注意力掩码和 输入序列中每个位置的索引的张量
        # TODO 没有思路
        :return:
        """

        mask_positions = torch.zeros((1, input_ids.shape[1]), dtype=input_ids.dtype).to(self.checkPoint.model.device)

        attention_mask = self.get_masks(input_ids, input_ids.device)

        position_ids = self.get_position_ids(
            input_ids,
            device=input_ids.device,
            mask_positions=mask_positions
        )

        return input_ids, position_ids, attention_mask

    @property
    def _history_len(self) -> int:
        return self.history_len

    def set_history_len(self, history_len: int = 10) -> None:
        self.history_len = history_len

    def _call(self, prompt: str, stop: Optional[List[str]] = None) -> str:
        print(f"__call:{prompt}")
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
        input_ids = self.encode(prompt, add_bos_token=self.state['add_bos_token'], truncation_length=self.max_new_tokens)
        # input_ids, position_ids, attention_mask = self.prepare_inputs_for_generation(input_ids=filler_input_ids)


        gen_kwargs.update({'inputs': input_ids})
        # 注意力掩码
        # gen_kwargs.update({'attention_mask': attention_mask})
        # gen_kwargs.update({'position_ids': position_ids})
        if self.stopping_criteria is None:
            self.stopping_criteria = transformers.StoppingCriteriaList()
        # 观测输出
        gen_kwargs.update({'stopping_criteria': self.stopping_criteria})

        output_ids = self.checkPoint.model.generate(**gen_kwargs)
        new_tokens = len(output_ids[0]) - len(input_ids[0])
        reply = self.decode(output_ids[0][-new_tokens:])
        print(f"response:{reply}")
        print(f"+++++++++++++++++++++++++++++++++++")
        return reply

    def generatorAnswer(self, prompt: str,
                         history: List[List[str]] = [],
                         streaming: bool = False):

        # TODO 需要实现chat对话模块和注意力模型，目前_call为langchain的LLM拓展的api，默认为无提示词模式，如果需要操作注意力模型，可以参考chat_glm的实现
        softprompt = self.history_to_text(prompt,history=history)
        response = self._call(prompt=softprompt, stop=['\n###'])

        answer_result = AnswerResult()
        answer_result.history = history + [[prompt, response]]
        answer_result.llm_output = {"answer": response}
        yield answer_result
