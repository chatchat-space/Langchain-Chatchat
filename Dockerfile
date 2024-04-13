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
    apt-get install -y --no-install-recommends python3.11 python3-pip curl libgl1 libglib2.0-0 && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    rm -f /usr/bin/python3 && \
    ln -s /usr/bin/python3.11 /usr/bin/python3 && \
    mkdir -p $HOME/Langchain-Chatchat

# Copy the application files
COPY bge-large-zh-v1.5 $HOME/
#COPY chatglm3-6b $HOME/
COPY . $HOME/Langchain-Chatchat/

RUN ls $HOME/bge-large-zh-v1.5
#RUN ls $HOME/chatglm3-6b
RUN ls $HOME/Langchain-Chatchat/

# Install dependencies from requirements.txt
#RUN pip3 install -r $HOME/Langchain-Chatchat/requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple && \
#    python3 $HOME/Langchain-Chatchat/init_database.py --recreate-vs && \
#    python3 $HOME/Langchain-Chatchat/copy_config_example.py && \
#    sed -i 's|MODEL_ROOT_PATH = ""|MODEL_ROOT_PATH = "/chatchat"|' $HOME/Langchain-Chatchat/model_config.py
WORKDIR $HOME/Langchain-Chatchat

#RUN pip3 install torch==2.1.2 torchvision==0.16.2 -i https://pypi.org/simple
RUN pip3 install -r requirements.txt -i https://pypi.org/simple && \
    python3 copy_config_example.py && \
    sed -i 's|MODEL_ROOT_PATH = ""|MODEL_ROOT_PATH = "/chatchat"|' configs/model_config.py && \
    python3 init_database.py --recreate-vs

EXPOSE 22 7861 8501
ENTRYPOINT ["python3", "startup.py", "-a"]