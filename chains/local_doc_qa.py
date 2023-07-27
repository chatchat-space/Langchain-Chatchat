from langchain.vectorstores import Chroma
from langchain.prompts import PromptTemplate
from langchain.chains.question_answering import load_qa_chain
from langchain import LLMChain
from langchain.llms import OpenAI
from configs.model_config import *
from langchain.embeddings.huggingface import HuggingFaceEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.callbacks import StreamlitCallbackHandler

with open("../knowledge_base/samples/content/test.txt") as f:
    state_of_the_union = f.read()

# TODO: define params
# text_splitter = MyTextSplitter()
text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=200)
texts = text_splitter.split_text(state_of_the_union)

# TODO: define params
# embeddings = MyEmbeddings()
embeddings = HuggingFaceEmbeddings(model_name=embedding_model_dict[EMBEDDING_MODEL],
                                   model_kwargs={'device': EMBEDDING_DEVICE})

docsearch = Chroma.from_texts(
    texts,
    embeddings,
    metadatas=[{"source": str(i)} for i in range(len(texts))]
).as_retriever()

# test
query = "什么是Prompt工程"
docs = docsearch.get_relevant_documents(query)
# print(docs)

# prompt_template = PROMPT_TEMPLATE

llm = OpenAI(model_name=LLM_MODEL,
             openai_api_key=llm_model_dict[LLM_MODEL]["api_key"],
             openai_api_base=llm_model_dict[LLM_MODEL]["api_base_url"],
             streaming=True)

# print(PROMPT)
prompt = PromptTemplate(input_variables=["input"], template="{input}")
chain = LLMChain(prompt=prompt, llm=llm)
resp = chain("你好")
for x in resp:
    print(x)

PROMPT = PromptTemplate(
    template=PROMPT_TEMPLATE,
    input_variables=["context", "question"]
)
chain = load_qa_chain(llm, chain_type="stuff", prompt=PROMPT)
response = chain({"input_documents": docs, "question": query}, return_only_outputs=False)
for x in response:
    print(response["output_text"])