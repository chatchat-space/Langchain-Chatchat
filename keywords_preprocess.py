import os

import torch
from safetensors.torch import save_model
from sentence_transformers import SentenceTransformer

def get_keyword_embedding(bert_model, tokenizer, key_words):
    tokenizer_output = tokenizer(key_words)
    input_ids = torch.tensor(tokenizer_output['input_ids'])[:, 1:-1]
    keyword_embedding = bert_model.embeddings.word_embeddings(input_ids)
    keyword_embedding = torch.mean(keyword_embedding, 1)
    return keyword_embedding


def add_keyword_to_model(model_name, key_words, output_model_path):
    st_model = SentenceTransformer(model_name)
    key_words_len = len(key_words)
    word_embedding_model = st_model._first_module()
    bert_model = word_embedding_model.auto_model
    tokenizer = word_embedding_model.tokenizer
    key_words_embedding = get_keyword_embedding(bert_model, tokenizer, key_words)
    # key_words_embedding = st_model.encode(key_words)

    embedding_weight = bert_model.embeddings.word_embeddings.weight
    embedding_weight_len = len(embedding_weight)
    tokenizer.add_tokens(key_words)
    bert_model.resize_token_embeddings(len(tokenizer), pad_to_multiple_of=32)

    # key_words_embedding_tensor = torch.from_numpy(key_words_embedding)
    embedding_weight = bert_model.embeddings.word_embeddings.weight
    with torch.no_grad():
        embedding_weight[embedding_weight_len:embedding_weight_len+key_words_len, :] = key_words_embedding

    if output_model_path:
        os.makedirs(output_model_path, exist_ok=True)
        word_embedding_model.save(output_model_path)
        safetensors_file = os.path.join(output_model_path, "model.safetensors")
        metadata = {'format': 'pt'}
        save_model(bert_model, safetensors_file, metadata)

def add_keyword_file_to_model(model_name, keyword_file, output_model_path):
    key_words = []
    with open(keyword_file, "r") as f:
        for line in f:
            key_words.append(line.strip())
    add_keyword_to_model(model_name, key_words, output_model_path)


if __name__ == '__main__':
    from configs import (
        MODEL_PATH,
        EMBEDDING_MODEL,
        EMBEDDING_KEYWORD_FILE,
        EMBEDDING_MODEL_OUTPUT_PATH
    )
    keyword_file = EMBEDDING_KEYWORD_FILE
    model_name = MODEL_PATH["embed_model"][EMBEDDING_MODEL]
    output_model_path = EMBEDDING_MODEL_OUTPUT_PATH

    add_keyword_file_to_model(model_name, keyword_file, output_model_path)

    # 以下为加入关键字前后tokenizer的测试用例对比
    def print_token_ids(output, tokenizer, sentences):
        for idx, ids in enumerate(output['input_ids']):
            print(f'sentence={sentences[idx]}')
            print(f'ids={ids}')
            for id in ids:
                decoded_id = tokenizer.decode(id)
                print(f'    {decoded_id}->{id}')

    # sentences = [
    #     '任务中国',
    #     '中石油',
    #     '指令提示技术'
    #     'Apple Watch Series 3 is good',
    #     'Apple Watch Series 8 is good',
    #     'Apple Watch Series is good',
    #     'Apple Watch is good',
    #     'iphone 13pro']
    sentences = [
        '指令提示技术',
        'Apple Watch Series 3'
    ]

    st_no_keywords = SentenceTransformer(model_name)
    tokenizer_without_keywords = st_no_keywords.tokenizer
    print("===== tokenizer with no keywords added =====")
    output = tokenizer_without_keywords(sentences)
    print_token_ids(output, tokenizer_without_keywords, sentences)
    print(f'-------- embedding with no keywords added -----')
    embeddings = st_no_keywords.encode(sentences)
    print(embeddings)

    st_with_keywords = SentenceTransformer(output_model_path)
    tokenizer_with_keywords = st_with_keywords.tokenizer
    print("===== tokenizer with keyword added =====")
    output = tokenizer_with_keywords(sentences)
    print_token_ids(output, tokenizer_with_keywords, sentences)

    print(f'-------- embedding with keywords added -----')
    embeddings = st_with_keywords.encode(sentences)
    print(embeddings)




