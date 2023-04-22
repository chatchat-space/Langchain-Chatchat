from configs.model_config import *
from chains.local_doc_qa import LocalDocQA
import os
import nltk

import uvicorn
from fastapi import FastAPI, File, UploadFile
from pydantic import BaseModel
from starlette.responses import RedirectResponse

app = FastAPI()

global local_doc_qa, vs_path

nltk.data.path = [os.path.join(os.path.dirname(__file__), "nltk_data")] + nltk.data.path

# return top-k text chunk from vector store
VECTOR_SEARCH_TOP_K = 10

# LLM input history length
LLM_HISTORY_LEN = 3

# Show reply with source text from input document
REPLY_WITH_SOURCE = False

class Query(BaseModel):
    query: str

@app.get('/')
async def document():
    return RedirectResponse(url="/docs")

@app.on_event("startup")
async def get_local_doc_qa():
    global local_doc_qa
    local_doc_qa = LocalDocQA()
    local_doc_qa.init_cfg(llm_model=LLM_MODEL,
                          embedding_model=EMBEDDING_MODEL,
                          embedding_device=EMBEDDING_DEVICE,
                          llm_history_len=LLM_HISTORY_LEN,
                          top_k=VECTOR_SEARCH_TOP_K)
    

@app.post("/file")
async def upload_file(UserFile: UploadFile=File(...),):
    global vs_path
    response = {
        "msg": None,
        "status": 0
    }
    try:
        filepath = './content/' + UserFile.filename
        content = await UserFile.read()
        # print(UserFile.filename)
        with open(filepath, 'wb') as f:
            f.write(content)
        vs_path, files = local_doc_qa.init_knowledge_vector_store(filepath)
        response = {
            'msg': 'seccess' if len(files)>0 else 'fail',
            'status': 1 if len(files)>0 else 0,
            'loaded_files': files
        }
        
    except Exception as err:
        response["message"] = err
        
    return response 

@app.post("/qa")
async def get_answer(query: str = ""):
    response = {
        "status": 0,
        "message": "",
        "answer": None
    }
    global vs_path
    history = []
    try:
        resp, history = local_doc_qa.get_knowledge_based_answer(query=query,
                                                                vs_path=vs_path,
                                                                chat_history=history)
        if REPLY_WITH_SOURCE:
            response["answer"] = resp
        else:
            response['answer'] = resp["result"]
        
        response["message"] = 'successful'
        response["status"] = 1

    except Exception as err:
        response["message"] = err
        
    return response


if __name__ == "__main__":
    uvicorn.run(
        app=app,
        host='0.0.0.0', 
        port=8100,
        reload=True,
        )

