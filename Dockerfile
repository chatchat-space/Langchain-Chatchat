# Base Image
FROM nvidia/cuda:12.1.1-cudnn8-devel-ubuntu22.04

# Labels
LABEL maintainer=chatchat

# Environment Variables
ENV HOME=/chatchat

# Commands
WORKDIR /

RUN ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && \
    echo "Asia/Shanghai" > /etc/timezone && \
#    apt-get update -y && \
#    apt-get install -y --no-install-recommends python3.11 python3-pip curl libgl1 libglib2.0-0 && \
    apt-get install -y --no-install-recommends python3.11 python3-pip && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
#    rm -f /usr/bin/python3 && \
#    ln -s /usr/bin/python3.11 /usr/bin/python3 && \
    mkdir -p $HOME/Langchain-Chatchat

# Copy the application files
#COPY bge-large-zh-v1.5 $HOME/
#COPY chatglm3-6b $HOME/
#RUN rm -rf bge-large-zh-v1.5 chatglm3-6b
COPY ./* $HOME/Langchain-Chatchat/

# Install dependencies from requirements.txt
RUN pip3 install -r $HOME/Langchain-Chatchat/requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple && \
    python3 $HOME/Langchain-Chatchat/init_database.py --recreate-vs && \
    python3 $HOME/Langchain-Chatchat/copy_config_example.py && \
    sed -i 's|MODEL_ROOT_PATH = ""|MODEL_ROOT_PATH = "/chatchat"|' $HOME/Langchain-Chatchat/model_config.py

EXPOSE 22 7861 8501
WORKDIR $HOME/Langchain-Chatchat/
ENTRYPOINT ["python3", "$HOME/Langchain-Chatchat/startup.py", "-a"]