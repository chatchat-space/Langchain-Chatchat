import logging

from chatchat.server.utils import get_tool_config

logger = logging.getLogger(__name__)


class ModelContainer:
    def __init__(self):
        self.model = None
        self.metadata = None

        self.vision_model = None
        self.vision_tokenizer = None
        self.audio_tokenizer = None
        self.audio_model = None

        vqa_config = get_tool_config("vqa_processor")
        if vqa_config["use"]:
            try:
                import torch
                from transformers import (
                    AutoModelForCausalLM,
                    AutoTokenizer,
                    LlamaTokenizer,
                )

                self.vision_tokenizer = LlamaTokenizer.from_pretrained(
                    vqa_config["tokenizer_path"], trust_remote_code=True
                )
                self.vision_model = (
                    AutoModelForCausalLM.from_pretrained(
                        pretrained_model_name_or_path=vqa_config["model_path"],
                        torch_dtype=torch.bfloat16,
                        low_cpu_mem_usage=True,
                        trust_remote_code=True,
                    )
                    .to(vqa_config["device"])
                    .eval()
                )
            except Exception as e:
                logger.error(e, exc_info=True)

        aqa_config = get_tool_config("vqa_processor")
        if aqa_config["use"]:
            try:
                import torch
                from transformers import (
                    AutoModelForCausalLM,
                    AutoTokenizer,
                    LlamaTokenizer,
                )

                self.audio_tokenizer = AutoTokenizer.from_pretrained(
                    aqa_config["tokenizer_path"], trust_remote_code=True
                )
                self.audio_model = (
                    AutoModelForCausalLM.from_pretrained(
                        pretrained_model_name_or_path=aqa_config["model_path"],
                        torch_dtype=torch.bfloat16,
                        low_cpu_mem_usage=True,
                        trust_remote_code=True,
                    )
                    .to(aqa_config["device"])
                    .eval()
                )
            except Exception as e:
                logger.error(e, exc_info=True)


container = ModelContainer()
