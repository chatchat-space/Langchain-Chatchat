import json
from langchain.llms.base import LLM
from typing import List, Dict, Optional,Tuple
from transformers import AutoTokenizer, AutoModel, AutoConfig,AutoModelForCausalLM
import torch
from configs.model_config import *
from utils import torch_gc
import torch
from transformers import StoppingCriteria, StoppingCriteriaList

DEVICE_ = LLM_DEVICE
DEVICE_ID = "0" if torch.cuda.is_available() else None
DEVICE = f"{DEVICE_}:{DEVICE_ID}" if DEVICE_ID else DEVICE_

class StoppingCriteriaSub(StoppingCriteria):
    def __init__(self, ):
        super().__init__()

    def __call__(self, input_ids: torch.LongTensor, scores: torch.FloatTensor, stops=[]):

        if input_ids[0][-1] == 13:
            return True

        return False

def chat(model, tokenizer, query: str, history: List[Tuple[str, str]] = None, max_length: int = 2048,device = 'cuda',
             do_sample=True, top_p=0.7, temperature=0.95, **kwargs):
        if history is None:
            history = []
        
        prompt = "A dialog, where User interacts with AI. AI is helpful, kind, obedient, honest, and knows its own limits.\nUser: Hello, AI.\nAI: Hello! How can I assist you today?\n"
        if not history:
            for i, (old_query, response) in enumerate(history):
                prompt += "User:{}\nAI:{}\n".format(old_query, response)
        prompt += "User:{}\nAI:".format(query)
        inputs = tokenizer(prompt, return_tensors="pt")
        inputs = inputs.to(device)
        #if logits_processor is None:
        #    logits_processor = LogitsProcessorList()
        #logits_processor.append(InvalidScoreLogitsProcessor())
        gen_kwargs = {"max_length": max_length,  "do_sample": do_sample, "top_p": top_p,
                      "temperature": temperature, 
                      #"logits_processor": logits_processor, 
                      **kwargs}
        outputs = model.generate(inputs.input_ids, stopping_criteria=StoppingCriteriaList([StoppingCriteriaSub()]), **gen_kwargs)
        #print(outputs)
        outputs = outputs.tolist()[0][len(inputs["input_ids"][0]):]
        #print(outputs)
        response = tokenizer.batch_decode([outputs,], skip_special_tokens=True, clean_up_tokenization_spaces=False)[0]
        #print(response)
        #response = process_response(response)
        history = history + [(query, response)]
        return response, history

def auto_configure_device_map_for_llama(num_gpus: int,) -> Dict[str, int]:
    # transformer.word_embeddings 占用1层
    # transformer.final_layernorm 和 lm_head 占用1层
    # transformer.layers 占用 28 层
    # 总共30层分配到num_gpus张卡上
    num_trans_layers = 32
    per_gpu_layers = 34 / num_gpus

    # bugfix: 在linux中调用torch.embedding传入的weight,input不在同一device上,导致RuntimeError
    # windows下 model.device 会被设置成 transformer.word_embeddings.device
    # linux下 model.device 会被设置成 lm_head.device
    # 在调用chat或者stream_chat时,input_ids会被放到model.device上
    # 如果transformer.word_embeddings.device和model.device不同,则会导致RuntimeError
    # 因此这里将transformer.word_embeddings,transformer.final_layernorm,lm_head都放到第一张卡上
    device_map = {'model.embed_tokens': 0,
                  'model.norm': 0, 'lm_head': 0}

    used = 2
    gpu_target = 0
    for i in range(num_trans_layers):
        if used >= per_gpu_layers:
            gpu_target += 1
            used = 0
        assert gpu_target < num_gpus
        device_map[f'model.layers.{i}'] = gpu_target
        used += 1

    return device_map


class LLAMA(LLM):
    max_token: int = 2048
    temperature: float = 0.8
    top_p = 0.9
    # history = []
    tokenizer: object = None
    model: object = None
    history_len: int = 10

    def __init__(self):

        super().__init__()
        

    @property
    def _llm_type(self) -> str:
        return "LLAMA"

    def _call(self,
              prompt: str,
              history: List[List[str]] = [],
              #max_length:int = MAX_LENGTH,
              #temperature: float = TEMPERATURE,
              #top_p:float = TOP_P,
              streaming: bool = STREAMING,
              **kwargs
              ):  # -> Tuple[str, List[List[str]]]:
        if history:
            history = [i for i in history if i[0] is not None]

        
        response, _ = chat(
                self.model, 
                self.tokenizer, 
                prompt, 
                history=history[-self.history_len:] if self.history_len > 0 else [],
                max_length=kwargs.get('max_length') if kwargs.get('max_length') else self.max_token,
                temperature=kwargs.get('temperature') if kwargs.get('temperature') else self.temperature,
                top_p=kwargs.get('top_p') if kwargs.get('top_p') else self.top_p,
                device=DEVICE)  
            
        torch_gc()
        history += [[prompt, response]]
        yield response, history
        torch_gc()

    # def chat(self,
    #          prompt: str) -> str:
    #     response, _ = self.model.chat(
    #         self.tokenizer,
    #         prompt,
    #         history=self.history[-self.history_len:] if self.history_len > 0 else [],
    #         max_length=self.max_token,
    #         temperature=self.temperature,
    #     )
    #     torch_gc()
    #     self.history = self.history + [[None, response]]
    #     return response

    def load_model(self,
                   model_name_or_path: str = "chavinlo/alpaca-native",
                   llm_device=LLM_DEVICE,
                   use_ptuning_v2=False,
                   use_lora=False,
                   device_map: Optional[Dict[str, int]] = None,
                   **kwargs):
        self.tokenizer = AutoTokenizer.from_pretrained(
            model_name_or_path,
            trust_remote_code=True
        )
        #self.is_llama = 'alpaca' in model_name_or_path or 'llama' in model_name_or_path
        model_config = AutoConfig.from_pretrained(model_name_or_path, trust_remote_code=True)

        if use_ptuning_v2:
            try:
                prefix_encoder_file = open('ptuning-v2/config.json', 'r')
                prefix_encoder_config = json.loads(prefix_encoder_file.read())
                prefix_encoder_file.close()
                model_config.pre_seq_len = prefix_encoder_config['pre_seq_len']
                model_config.prefix_projection = prefix_encoder_config['prefix_projection']
            except Exception as e:                
                logger.error(f"fail to load PrefixEncoder config.json: {e}")
        
        self.model = AutoModelForCausalLM.from_pretrained(model_name_or_path, config=model_config, trust_remote_code=True,
                                               **kwargs)
        
        if LLM_LORA_PATH and use_lora:
            from peft import PeftModel
            self.model = PeftModel.from_pretrained(self.model, LLM_LORA_PATH)

        if torch.cuda.is_available() and llm_device.lower().startswith("cuda"):
            # 根据当前设备GPU数量决定是否进行多卡部署
            num_gpus = torch.cuda.device_count()
            if num_gpus < 2 and device_map is None:
                self.model = self.model.half().cuda()
            else:
                from accelerate import dispatch_model,infer_auto_device_map
   
                
                model = AutoModelForCausalLM.from_pretrained(model_name_or_path, config=model_config, trust_remote_code=True,
                                            **kwargs)

                
                if LLM_LORA_PATH and use_lora:
                    from peft import PeftModel
                    model = PeftModel.from_pretrained(self.model, LLM_LORA_PATH)
                # 可传入device_map自定义每张卡的部署情况
                if device_map is None:
                    device_map = auto_configure_device_map_for_llama(num_gpus)

                self.model = dispatch_model(self.model.half(), device_map=device_map)
        else:
            self.model = self.model.float().to(llm_device)

        if use_ptuning_v2:
            try:
                prefix_state_dict = torch.load('ptuning-v2/pytorch_model.bin')
                new_prefix_state_dict = {}
                for k, v in prefix_state_dict.items():
                    if k.startswith("transformer.prefix_encoder."):
                        new_prefix_state_dict[k[len("transformer.prefix_encoder."):]] = v
                self.model.transformer.prefix_encoder.load_state_dict(new_prefix_state_dict)
                self.model.transformer.prefix_encoder.float()
            except Exception as e:              
                logger.error(f"fail to load PrefixEncoder weights:{e}")

        self.model = self.model.eval()


if __name__ == "__main__":
    llm = LLAMA()
    llm.load_model(model_name_or_path=llm_model_dict[LLM_MODEL],
                   llm_device=LLM_DEVICE, )
    last_print_len = 0
    for resp, history in llm._call("你好", streaming=False):
        logger.info(resp)
    pass
