# Base Image
FROM python:3.11
LABEL maintainer=chatchat
WORKDIR /root
# Environment Variables
ENV CHATCHAT_ROOT=/root/chatchat_data

# Init Environment
RUN ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && \
    echo "Asia/Shanghai" > /etc/timezone
RUN apt-get update -y && \
    apt-get install -y git && \
    apt-get install -y --no-install-recommends libgl1 libglib2.0-0 && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install Chatchat
RUN git clone https://github.com/chatchat-space/Langchain-Chatchat.git
RUN pip install --upgrade pip setuptools
RUN pip install --index-url https://pypi.python.org/simple/ pipx && pipx install poetry
# Add poetry to PATH
ENV PATH="/root/.local/bin:${PATH}"

WORKDIR /root/Langchain-Chatchat/libs/chatchat-server

# 设置官方源
RUN poetry config virtualenvs.create false && \
    poetry config repositories.pypi.url https://pypi.org/simple/

# 安装依赖
RUN poetry install --with lint,test -E xinference
RUN pip install --index-url https://pypi.python.org/simple/ openpyxl networkx faiss-cpu  \
    jq unstructured[pdf] opencv-python rapidocr-onnxruntime PyMuPDF rank_bm25 youtube_search \
    python-docx

# Install Chatchat
RUN pip install --index-url https://pypi.python.org/simple/ langchain-chatchat -U

# 初始化配置
RUN python cli.py init

# Install ModelProvider
#RUN pip install xinference-client

# 将监听 IP 从 localhost 统一改为 0.0.0.0
#RUN chatchat-config server --default_bind_host=0.0.0.0 && \
#    chatchat-config model --default_llm_model qwen2-instruct \
RUN sed -i 's/127.0.0.1/0.0.0.0/g' $CHATCHAT_ROOT/basic_settings.yaml

# 初始化知识库文件
ADD /docker/data.tar.gz $CHATCHAT_ROOT/

WORKDIR $CHATCHAT_ROOT

EXPOSE 7861 8501

#ENTRYPOINT ["chatchat", "-a"]
ENTRYPOINT ["python", "cli.py", "start", "-a"]