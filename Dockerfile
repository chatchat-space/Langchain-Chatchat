# Base Image
#FROM nvidia/cuda:12.1.1-cudnn8-devel-ubuntu22.04
FROM nvidia/cuda:12.1.1-cudnn8-runtime-ubuntu22.04

# Labels
LABEL maintainer=chatchat
# Environment Variables
ENV HOME=/chatchat
# Commands
WORKDIR /

RUN ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && \
    echo "Asia/Shanghai" > /etc/timezone && \
    apt-get update -y && \
    apt-get install -y --no-install-recommends python3.11 python3-pip curl libgl1 libglib2.0-0 jq && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    rm -f /usr/bin/python3 && \
    ln -s /usr/bin/python3.11 /usr/bin/python3 && \
    mkdir -p $HOME/Langchain-Chatchat $HOME/bge-large-zh-v1.5 $HOME/chatglm3-6b

# Copy the application files
COPY bge-large-zh-v1.5 $HOME/bge-large-zh-v1.5
COPY chatglm3-6b $HOME/chatglm3-6b
RUN rm -rf bge-large-zh-v1.5 chatglm3-6b
COPY . $HOME/Langchain-Chatchat/

RUN ls /chatchat
RUN du -sh /chatchat/*
RUN ls /chatchat/bge-large-zh-v1.5
RUN du -sh /chatchat/bge-large-zh-v1.5/*
RUN ls $HOME/chatglm3-6b
RUN du -sh /chatchat/Langchain-Chatchat/*

WORKDIR $HOME/Langchain-Chatchat

# Install dependencies from requirements.txt
RUN pip3 install -r requirements.txt -i https://pypi.org/simple && \
    python3 copy_config_example.py && \
    sed -i 's|MODEL_ROOT_PATH = ""|MODEL_ROOT_PATH = "/chatchat"|' configs/model_config.py && \
    python3 init_database.py --recreate-vs

EXPOSE 22 7861 8501
ENTRYPOINT ["python3", "startup.py", "-a"]