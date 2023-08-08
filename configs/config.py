SQLALCHEMY_DATABASE_URI = "sqlite:///./langchain_chat_glm.db"
kbs_config = {
    "faiss": {
    },
    "milvus": {
        "host": "127.0.0.1",
        "port": "19530",
        "user": "",
        "password": "",
        "secure": False,
    }
}
