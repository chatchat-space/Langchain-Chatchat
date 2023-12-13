from langchain.retrievers.document_compressors import CohereRerank
from llama_index.postprocessor import SentenceTransformerRerank
from sentence_transformers import SentenceTransformer,CrossEncoder

model_path = "/root/autodl-tmp/models/bge-reranker-large/"
instruction = "为这个句子生成表示以用于检索相关文章："
reranker = SentenceTransformerRerank(
    top_n=5,
    model="local:"+model_path,
)

reranker_model = SentenceTransformer(model_name_or_path=model_path,device="cuda")

reranker_ce = CrossEncoder(model_name=model_path,device="cuda",max_length=1024)

reranker_ce.predict([[],[]])

print("Load reranker")

