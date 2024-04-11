# Base Image
FROM nvidia/cuda:12.1.1-cudnn8-devel-ubuntu22.04

# Labels
LABEL maintainer=chatchat

# Environment Variables
ENV llmname=chatglm3-6b

# Commands
WORKDIR /

RUN ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && \
    echo "Asia/Shanghai" > /etc/timezone && \
    apt-get update -y && \
    apt-get install -y --no-install-recommends python3.11 python3-pip curl libgl1 libglib2.0-0 && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    rm -f /usr/bin/python3 && \
    ln -s /usr/bin/python3.11 /usr/bin/python3 && \
    mkdir -p /chatchat/Langchain-Chatchat

# Copy the application files
#ADD chatglm3-6b.tar.gz /chatchat/
ADD bge-large-zh-v1.5.tar.gz /chatchat/
COPY ./* /chatchat/Langchain-Chatchat/

# Install dependencies from requirements.txt
RUN pip3 install -r /chatchat/Langchain-Chatchat/requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple && \
    python3 /chatchat/Langchain-Chatchat/init_database.py --recreate-vs && \
    python3 /chatchat/Langchain-Chatchat/copy_config_example.py && \
    sed -i 's|MODEL_ROOT_PATH = ""|MODEL_ROOT_PATH = "/chatchat"|' model_config.py

EXPOSE 22 7861 8501
WORKDIR /chatchat/Langchain-Chatchat/
ENTRYPOINT ["python3", "/chatchat/Langchain-Chatchat/startup.py", "-a"]