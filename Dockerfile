FROM nvidia/cuda:12.1.1-cudnn8-devel-ubuntu22.04
RUN apt-get update \ 
  && DEBIAN_FRONTEND="noninteractive" \ 
  apt-get install -y \
    git wget vim python3-pip python3-venv libopencv-dev git-lfs sudo build-essential zlib1g-dev libncurses5-dev libgdbm-dev libnss3-dev libssl-dev libreadline-dev libffi-dev libsqlite3-dev libbz2-dev liblzma-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /temp

# 下载python
 RUN wget https://www.python.org/ftp/python/3.10.13/Python-3.10.13.tgz && \
     tar -xvf Python-3.10.13.tgz

# 编译&安装python
 RUN cd Python-3.10.13 && \
     ./configure --enable-optimizations && \
     make && \
     make install

RUN rm -r /temp && \
    ln -s /usr/local/bin/python3 /usr/local/bin/python && \
    ln -s /usr/local/bin/pip3 /usr/local/bin/pip 

WORKDIR /Langchain-Chatchat  
RUN mkdir langchain-chatchat chatglm2-6b-32k m3e-large text2vec-bge-large-chinese tmp
RUN git clone https://github.com/chatchat-space/Langchain-Chatchat.git /Langchain-Chatchat-self
# RUN git clone https://huggingface.co/THUDM/chatglm2-6b-32k /chatglm2-6b-32k
# RUN git clone https://huggingface.co/moka-ai/m3e-large /m3e-large
# RUN git clone https://huggingface.co/BAAI/bge-large-zh-noinstruct /bge-large-zh-noinstruct

RUN python3 -m pip install --upgrade pip
RUN pip install --upgrade streamlit
# COPY /Langchain-Chatchat-self/requirements.txt /requirements.txt 
RUN pip install -r /Langchain-Chatchat-self/requirements.txt
# RUN rm -r /Langchain-Chatchat-self
EXPOSE 8501
EXPOSE 7861
EXPOSE 20001
EXPOSE 20002
EXPOSE 20003
EXPOSE 8888
EXPOSE 19530
ENTRYPOINT ["python3", "startup.py", "-a"]
# ENTRYPOINT ["-a"]
# CMD ["python3", "startup.py"]
# CMD ["python3", "python startup.py -a"]
# CMD ["python3", "python startup.py -a"]
# CMD ["python3", "server/llm_api.py", "streamlit run webui.py"]
