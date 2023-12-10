from transformers import LlamaTokenizer, AutoModelForCausalLM, AutoTokenizer
from configs import TOOL_CONFIG
import torch


class ModelContainer:
    def __init__(self):
        self.model = None
        self.metadata = None

        self.metadata_response = None

        self.vision_model = None
        self.vision_tokenizer = None
        self.audio_tokenizer = None
        self.audio_model = None

        if TOOL_CONFIG["vqa_processor"]["use"]:
            self.vision_tokenizer = LlamaTokenizer.from_pretrained(
                TOOL_CONFIG["vqa_processor"]["tokenizer_path"],
                trust_remote_code=True)
            self.vision_model = AutoModelForCausalLM.from_pretrained(
                pretrained_model_name_or_path=TOOL_CONFIG["vqa_processor"]["model_path"],
                torch_dtype=torch.bfloat16,
                low_cpu_mem_usage=True,
                trust_remote_code=True
            ).to(TOOL_CONFIG["vqa_processor"]["device"]).eval()

        if TOOL_CONFIG["aqa_processor"]["use"]:
            self.audio_tokenizer = AutoTokenizer.from_pretrained(
                TOOL_CONFIG["aqa_processor"]["tokenizer_path"],
                trust_remote_code=True)
            self.audio_model = AutoModelForCausalLM.from_pretrained(
                pretrained_model_name_or_path=TOOL_CONFIG["aqa_processor"]["model_path"],
                torch_dtype=torch.bfloat16,
                low_cpu_mem_usage=True,
                trust_remote_code=True).to(TOOL_CONFIG["aqa_processor"]["device"]).eval()


container = ModelContainer()
