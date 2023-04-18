import sys

sys.path.append("..")  # 将父目录放入系统路径中

from fastapi import FastAPI, Request, UploadFile, File
from fastapi.responses import StreamingResponse
import uvicorn, json, datetime, time
from langchain.vectorstores import FAISS
from starlette.middleware.cors import CORSMiddleware
from langchain.embeddings.huggingface import HuggingFaceEmbeddings
from langchain.vectorstores import Pinecone
from langchain.chains import RetrievalQA
from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain.document_loaders import UnstructuredFileLoader
# pip install pinecone-client,记得换源
import pinecone
import sentence_transformers
from models import *

# 写到 import torch前面，否则多显卡情况有异常
import os

os.environ['CUDA_VISIBLE_DEVICES'] = "0"

app = FastAPI()

# 解决跨域问题
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


# post请求，流式输出
@app.post("/stream")
async def create_stream_item(request: Request):
    json_post_raw = await request.json()
    json_post = json.dumps(json_post_raw)
    json_post_list = json.loads(json_post)
    query = json_post_list.get('prompt')
    history = json_post_list.get('history')
    vs_path = json_post_list.get('vs_path')

    print("chat_history========================================", history)
    print("开始查询========================================")
    # max_length = json_post_list.get('max_length')
    # top_p = json_post_list.get('top_p')
    # temperature = json_post_list.get('temperature')
    chatglm.history = history
    chatglm.chat_mode = ModelType.stream_chat
    knowledge_chain({"query": query})
    now = datetime.datetime.now()
    time_stamp = now.strftime("%Y-%m-%d %H:%M:%S")
    if vs_path is None or vs_path == "":
        answer = {
            "response": {"vs_path参数不能为空"},
            "status": 200,
            "time": time_stamp
        }
        return StreamingResponse(json.dumps(answer, ensure_ascii=False) + "\n",
                                 status_code=200, media_type="application/json")
    else:
        return StreamingResponse(chatglm.start_stream_chat(query, vs_path),
                                 status_code=200, media_type="application/json")


@app.post("/uploadfile")
async def create_upload_file(file: UploadFile = File(...)):
    # 指定文件保存路径
    file_path = model_config.UPLOAD_LOCAL_PATH + file.filename
    with open(file_path, "wb") as f:
        # 读取上传的文件内容并保存到指定路径
        f.write(file.file.read())
    f.close()
    try:
        loader = UnstructuredFileLoader(file_path, mode="elements")
        docs = loader.load()
        print(f"{file} 已成功加载")
    except:
        print(f"{file} 未能成功加载")

    vector_store = FAISS.from_documents(docs, embeddings)

    vs_path = f"""./vector_store/{os.path.splitext(file)[0]}_FAISS_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}"""
    vector_store.save_local(vs_path)
    now = datetime.datetime.now()
    time_stamp = now.strftime("%Y-%m-%d %H:%M:%S")
    response = {"filename": file.filename, "local_vs_path": vs_path}
    answer = {
        "response": response,
        "status": 200,
        "time": time_stamp
    }
    return answer


# post请求
@app.post("/")
async def create_item(request: Request):
    start_time = time.perf_counter()
    json_post_raw = await request.json()
    json_post = json.dumps(json_post_raw)
    json_post_list = json.loads(json_post)
    query = json_post_list.get('prompt')
    history = json_post_list.get('history')
    vs_path = json_post_list.get('vs_path')

    print("chat_history========================================", history)
    print("开始查询========================================")
    # max_length = json_post_list.get('max_length')
    # top_p = json_post_list.get('top_p')
    # temperature = json_post_list.get('temperature')
    chatglm.history = history
    chatglm.is_stream_chat = 0
    vector_store = init_vector_store(vs_path)
    system_template = """基于以下内容，简洁和专业的来回答用户的问题。
        如果无法从中得到答案，请说 "不知道" 或 "没有足够的相关信息"，不要试图编造答案，答案只要中文。
        ----------------
        {context}
        ----------------
        """
    messages = [
        SystemMessagePromptTemplate.from_template(system_template),
        HumanMessagePromptTemplate.from_template("{question}"),
    ]
    prompt = ChatPromptTemplate.from_messages(messages)
    knowledge_chain = RetrievalQA.from_llm(
        llm=chatglm,
        retriever=vector_store.as_retriever(search_kwargs={"k": model_config.VECTOR_SEARCH_TOP_K}),
        prompt=prompt
    )
    knowledge_chain.return_source_documents = False
    response = knowledge_chain({"query": query})
    # chatglm.history[-1][0] = query
    end_time = time.perf_counter()
    # 计算操作耗时
    elapsed_time = end_time - start_time
    # 输出耗时时间
    print("问答操作耗时: {:.6f} 秒".format(elapsed_time))

    now = datetime.datetime.now()
    time_stamp = now.strftime("%Y-%m-%d %H:%M:%S")

    answer = {
        "response": response,
        "history": [],
        "status": 200,
        "time": time_stamp
    }
    log = "[" + time_stamp + "] " + '", response:"' + repr(response) + '"'
    print(log)
    chatglm.torch_gc()
    print("answer=====>", answer)
    return answer


def init_embedding():
    print("加载embeding模型......")
    embeddings = HuggingFaceEmbeddings(model_name=model_config.embedding_model_dict[model_config.EMBEDDING_MODEL])
    embeddings.client = sentence_transformers.SentenceTransformer(embeddings.model_name,
                                                                  device=model_config.EMBEDDING_DEVICE)
    print("加载embeding模型完成......")


def init_vector_store(vs_path):
    start_time = time.perf_counter()
    if model_config.IS_LOCAL_STORAGE:
        vector_store = FAISS.load_local(vs_path, embeddings)
    else:
        # 去Pinecone官网免费注册获得：api_key、environment、index_name
        pinecone.init(api_key="", environment="")
        index_name = ""
        vector_store = Pinecone.from_existing_index(index_name=index_name, embedding=embeddings)
    end_time = time.perf_counter()
    # 计算操作耗时
    elapsed_time = end_time - start_time
    # 输出耗时时间
    print("init_vector_store===操作耗时: {:.6f} 秒".format(elapsed_time))
    return vector_store

def init_cfg():
    global chatglm, embeddings, vector_store
    print("预加载模型......")
    start_time = time.perf_counter()
    print("加载GLM模型......")
    chatglm = ChatGLM()
    chatglm.load_model(model_name_or_path=model_config.llm_model_dict[model_config.LLM_MODEL])
    chatglm.history_len = model_config.LLM_HISTORY_LEN
    print("模型加载完成!!!")
    end_time = time.perf_counter()
    # 计算操作耗时
    elapsed_time = end_time - start_time
    # 输出耗时时间
    print("模型预加载耗时: {:.6f} 秒".format(elapsed_time))


if __name__ == '__main__':
    init_embedding()
    init_cfg()
    # 外网访问地址，记得端口在安全组、防火墙开放
    # uvicorn.run(app, host='0.0.0.0', port=8899, log_level="info")
    uvicorn.run(app, host='127.0.0.1', port=8899, log_level="info")
