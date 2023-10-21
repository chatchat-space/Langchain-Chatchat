'''
该功能是为了将关键词加入到embedding模型中，以便于在embedding模型中进行关键词的embedding
该功能的实现是通过修改embedding模型的tokenizer来实现的
该功能仅仅对EMBEDDING_MODEL参数对应的的模型有效，输出后的模型保存在原本模型
该功能的Idea由社区贡献，感谢@CharlesJu1

保存的模型的位置位于原本嵌入模型的目录下，模型的名称为原模型名称+Merge_Keywords_时间戳
'''
import sys

sys.path.append("..")
import os
from safetensors.torch import save_model
from sentence_transformers import SentenceTransformer
from datetime import datetime
from configs import (
    MODEL_PATH,
    EMBEDDING_MODEL,
    EMBEDDING_KEYWORD_FILE,
)


def add_keyword_to_model(model_name: str = EMBEDDING_MODEL, keyword_file: str = "", output_model_path: str = None):
    key_words = []
    with open(keyword_file, "r") as f:
        for line in f:
            key_words.append(line.strip())

    model = SentenceTransformer(model_name)
    word_embedding_model = model._first_module()
    tokenizer = word_embedding_model.tokenizer
    tokenizer.add_tokens(key_words)
    word_embedding_model.auto_model.resize_token_embeddings(len(tokenizer), pad_to_multiple_of=32)

    if output_model_path:
        os.makedirs(output_model_path, exist_ok=True)
        tokenizer.save_pretrained(output_model_path)
        model.save(output_model_path)
        safetensors_file = os.path.join(output_model_path, "model.safetensors")
        metadata = {'format': 'pt'}
        save_model(model, safetensors_file, metadata)

def add_keyword_to_embedding_model(path: str = EMBEDDING_KEYWORD_FILE):
    keyword_file = os.path.join(path)
    model_name = MODEL_PATH["embed_model"][EMBEDDING_MODEL]
    model_parent_directory = os.path.dirname(model_name)
    current_time = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_model_name = "{}_Merge_Keywords_{}".format(EMBEDDING_MODEL, current_time)
    output_model_path = os.path.join(model_parent_directory, output_model_name)
    add_keyword_to_model(model_name, keyword_file, output_model_path)
    print("save model to {}".format(output_model_path))


if __name__ == '__main__':
    add_keyword_to_embedding_model(EMBEDDING_KEYWORD_FILE)
