import os
from safetensors.torch import save_model
from sentence_transformers import SentenceTransformer

def add_keyword_to_model(model_name, key_words, output_model_path):
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


def add_keyword_file_to_model(model_name, keyword_file, output_model_path):
    key_words = []
    with open(keyword_file, "r") as f:
        for line in f:
            key_words.append(line.strip())
    add_keyword_to_model(model_name, key_words, output_model_path)


if __name__ == '__main__':

    def print_token_ids(output, tokenizer, sentences):
        for idx, ids in enumerate(output['input_ids']):
            print(f'\nsentence={sentences[idx]}')
            print(f'ids={ids}')
            for id in ids:
                decoded_id = tokenizer.decode(id)
                print(f'    {decoded_id}->{id}')

    model_name = '/Users/cju/ml/m3e-base'
    output_model_path = os.path.join(os.path.dirname(__file__), 'output')

    key_words = ['iphone13pro', '13pro', '中石油']
    add_keyword_to_model(model_name, key_words, output_model_path)

    # keyword_file = 'keywords.txt'
    # add_keyword_file_to_model(model_name, keyword_file, output_model_path)

    tokenizer_without_keywords = SentenceTransformer(model_name).tokenizer
    tokenizer_with_keywords = SentenceTransformer(output_model_path).tokenizer
    sentences = [
        '任务中国',
        '中石油',
        'iphone13pro is good',
        'iphone13pro',
        'iphone 13 pro',
        'iphone 13pro']

    output = tokenizer_without_keywords(sentences)
    print("===== tokenizer with keyword =====")
    print_token_ids(output, tokenizer_without_keywords, sentences)

    output = tokenizer_with_keywords(sentences)
    print("===== tokenizer with keyword =====")
    print_token_ids(output, tokenizer_with_keywords, sentences)

