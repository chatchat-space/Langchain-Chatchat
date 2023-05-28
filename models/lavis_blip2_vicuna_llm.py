from abc import ABC

from langchain.llms.base import LLM
import torch

from typing import Optional, List, Dict, Any
from models.loader import LoaderCheckPoint
from models.base import (LavisBlip2Multimodal,
                         AnswerResult)


class LavisBlip2VicunaLLM(LavisBlip2Multimodal, LLM, ABC):
    checkPoint: LoaderCheckPoint = None
    model: Any = None
    vis_processors: dict = None
    image_path: str = None
    history = []
    history_len: int = 3

    def __init__(self, checkPoint: LoaderCheckPoint):
        super().__init__()
        self.checkPoint = checkPoint
        try:
            from lavis.models import load_model_and_preprocess
        except ImportError as exc:
            raise ValueError(
                "Could not import depend python package "
                "Please install it with `pip install salesforce-lavis`."
            ) from exc

        # loads InstructBLIP model
        self.model, self.vis_processors, _ = load_model_and_preprocess(name="blip2_vicuna_instruct",
                                                             model_type="vicuna7b",
                                                             is_eval=True, device=self.checkPoint.llm_device)

    @property
    def _llm_type(self) -> str:
        return "Blip2VicunaLLM"

    @property
    def _check_point(self) -> LoaderCheckPoint:
        return self.checkPoint

    def _blip2_instruct(self):
        return self.model

    def _image_blip2_vis_processors(self):
        return self.vis_processors

    def set_image_path(self, image_path: str):
        self.image_path = image_path

    @property
    def _history_len(self) -> int:
        return self.history_len

    def set_history_len(self, history_len: int = 10) -> None:
        self.history_len = history_len

    def prepare_image_vis_processors(self) -> torch.Tensor:
        """
        创建图片矢量
        :return:
        """
        from PIL import Image
        raw_image = Image.open(self.image_path).convert('RGB')
        image_tensor = self.vis_processors["eval"](raw_image).unsqueeze(0).to(self.checkPoint.llm_device)
        return image_tensor

    # 将历史对话数组转换为文本格式
    def history_to_prompt(self, query):
        formatted_history = ''
        history = self.history[-self.history_len:] if self.history_len > 0 else []
        for i, (old_query, response) in enumerate(history):
            formatted_history += "[Round {}]\nQuestion：{}\nAnswer：{}\n".format(i, old_query, response)
        formatted_history += "[Round {}]\nQuestion：{}\nAnswer：".format(len(history), query)
        return formatted_history

    def _call(self, prompt: str, stop: Optional[List[str]] = None) -> str:
        pass

    def generatorAnswer(self, prompt: str,
                        history: List[List[str]] = [],
                        streaming: bool = False):
        image_tensor = self.prepare_image_vis_processors()
        # 处理历史对话
        self.history = history
        prompt = self.history_to_prompt(prompt)
        print(prompt)
        response = self.model.generate(
            {
                "image": image_tensor,
                "prompt": prompt
            },
        )

        answer_result = AnswerResult()
        answer_result.history = self.history
        answer_result.llm_output = {"answer": " ".join([response[i] for i in range(len(response))])}
        yield answer_result
