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
    mkdir -p /data/model/Langchain-Chatchat

# Copy the application files
#COPY /mnt/chatglm3-6b /data/model/chatglm3-6b
ADD /mnt/chatglm3-6b.tar.gz /data/model/
#COPY /mnt/bge-large-zh-v1.5 /data/model/bge-large-zh-v1.5
ADD /mnt/bge-large-zh-v1.5.tar.gz /data/model/
COPY ./* /data/model/Langchain-Chatchat/

# Install dependencies from requirements.txt
RUN pip3 install -r /data/model/Langchain-Chatchat/requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

RUN python3 /data/model/Langchain-Chatchat/init_database.py --recreate-vs
EXPOSE 22 7861 8501
WORKDIR /data/model/Langchain-Chatchat
ENTRYPOINT ["python3", "/data/model/Langchain-Chatchat/startup.py", "-a"]