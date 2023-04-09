import warnings
from types import MethodType
from typing import Optional, Tuple, List

from langchain.embeddings.base import Embeddings
from peft import PrefixTuningConfig, TaskType, get_peft_model
import torch
from torch.utils.data import DataLoader
from transformers import AutoTokenizer

from chatglm_llm import model,tokenizer

Embedding_prefix = "./adapter_model.bin"

embedding_tokenizer = AutoTokenizer.from_pretrained(
    "THUDM/chatglm-6b",
    trust_remote_code=True,
    truncation_side="left"
)

def embedding_forward(
        self,
        input_ids: Optional[torch.Tensor] = None,
        position_ids: Optional[torch.Tensor] = None,
        attention_mask: Optional[torch.Tensor] = None,
        past_key_values: Optional[Tuple[torch.FloatTensor]] = None,
        inputs_embeds: Optional[torch.Tensor] = None,
        labels: Optional[torch.Tensor] = None,
        use_cache: Optional[bool] = None,
        output_attentions: Optional[bool] = None,
        output_hidden_states: Optional[bool] = None,
        return_dict: Optional[bool] = None,
):
    use_cache = use_cache if use_cache is not None else self.config.use_cache
    return_dict = return_dict if return_dict is not None else self.config.use_return_dict

    MASK, gMASK = self.config.mask_token_id, self.config.gmask_token_id
    mask_token = gMASK if gMASK in input_ids else MASK
    use_gmask = True if gMASK in input_ids else False
    seqs = input_ids.tolist()
    mask_positions = [seq.index(mask_token) for seq in seqs]

    position_ids = self.get_position_ids(
        input_ids,
        mask_positions = mask_positions,
        device=input_ids.device,
    )

    past_key_values = [torch.permute(i,(0,3,1,2,4)) for i in past_key_values]

    transformer_outputs = self.transformer(
        input_ids=input_ids,
        position_ids=position_ids,
        attention_mask=attention_mask,
        past_key_values=past_key_values,
        inputs_embeds=inputs_embeds,
        use_cache=use_cache,
        output_attentions=output_attentions,
        output_hidden_states=output_hidden_states,
        return_dict=return_dict,
    )

    hidden_states = transformer_outputs.last_hidden_state[-1]

    return hidden_states

def peft_forward(
    self,
    input_ids=None,
    attention_mask=None,
    inputs_embeds=None,
    labels=None,
    output_attentions=None,
    output_hidden_states=None,
    return_dict=None,
    **kwargs,
):
    batch_size = input_ids.shape[0]
    if attention_mask is not None:
        # concat prompt attention mask
        prefix_attention_mask = torch.ones(batch_size, self.peft_config.num_virtual_tokens).to(self.device)
        attention_mask = torch.cat((prefix_attention_mask, attention_mask), dim=1)

    if kwargs.get("position_ids", None) is not None:
        warnings.warn("Position ids are not supported for parameter efficient tuning. Ignoring position ids.")
        kwargs["position_ids"] = None
    if kwargs.get("token_type_ids", None) is not None:
        warnings.warn("Token type ids are not supported for parameter efficient tuning. Ignoring token type ids")
        kwargs["token_type_ids"] = None
    kwargs.update(
        {
            "attention_mask": attention_mask,
            "labels": labels,
            "output_attentions": output_attentions,
            "output_hidden_states": output_hidden_states,
            "return_dict": return_dict,
        }
    )

    past_key_values = self.get_prompt(batch_size)
    return embedding_forward(self.base_model,input_ids=input_ids, past_key_values=past_key_values, **kwargs) # self.base_model(input_ids=input_ids, past_key_values=past_key_values, **kwargs)

model = model.eval()

# setup peft
peft_config = PrefixTuningConfig(
    task_type=TaskType.CAUSAL_LM,
    num_virtual_tokens=8,
    prefix_projection=False
)

base_model_prepare_inputs_for_generation = model.prepare_inputs_for_generation

embedding_model = get_peft_model(model, peft_config).half().cuda()

model.prepare_inputs_for_generation = base_model_prepare_inputs_for_generation
embedding_model.forward = MethodType(peft_forward,embedding_model)

embedding_model.load_state_dict(torch.load(Embedding_prefix),strict=False)

class ChatGLM_Embedding(Embeddings):
    max_length = 1024
    batch_size = 2

    def embed_query(self, text: str) -> List[float]:
        tokenized = \
        embedding_tokenizer([text + '[MASK]'], return_tensors="pt", padding='max_length', truncation='longest_first', max_length=self.max_length)[
            'input_ids'].to(embedding_model.device)
        with torch.no_grad():
            outputs = embedding_model(tokenized)
        return outputs[0].tolist()

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        batches = [texts[i:i + self.batch_size] for i in range(0, len(texts), self.batch_size)]
        embeddings = []
        for batch in batches:
            embeddings.extend(self._embed_documents(batch))
        return embeddings

    def _embed_documents(self, texts: List[str]) -> List[List[float]]:
        tokenized = embedding_tokenizer([text + '[MASK]' for text in texts], return_tensors="pt",padding='max_length', truncation='longest_first', max_length=self.max_length)['input_ids'].to(embedding_model.device)
        with torch.no_grad():
            outputs = embedding_model(tokenized)
        return outputs.tolist()