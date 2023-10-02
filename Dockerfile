FROM nvidia/cuda:12.1.1-cudnn8-devel-ubuntu22.04
RUN apt-get update \ 
  && DEBIAN_FRONTEND="noninteractive" \ 
  apt-get install -y \
    git wget vim python3.10 python3-pip python3-venv libopencv-dev git-lfs sudo build-essential zlib1g-dev libncurses5-dev libgdbm-dev libnss3-dev libssl-dev libreadline-dev libffi-dev libsqlite3-dev libbz2-dev liblzma-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# WORKDIR /temp

# 下载python
# RUN wget https://www.python.org/ftp/python/3.10.13/Python-3.10.13.tgz && \
#     tar -xvf Python-3.10.13.tgz

# 编译&安装python
# RUN cd Python-3.10.13 && \
#     ./configure --enable-optimizations && \
#     make && \
#     make install

# RUN rm -r /temp && \
#     ln -s /usr/local/bin/python3 /usr/local/bin/python && \
#     ln -s /usr/local/bin/pip3 /usr/local/bin/pip 

RUN ln -s /usr/local/bin/python3 /usr/local/bin/python && \
    ln -s /usr/local/bin/pip3 /usr/local/bin/pip 


WORKDIR /Langchain-Chatchat  
# RUN mkdir langchain-chatchat tmp

# 安装Langchain-Chatchat主程序
RUN git clone https://github.com/tommyvinny/docker-for-Chatchat.git /Langchain-Chatchat
# 安装embed_model
RUN git clone https://huggingface.co/nghuyong/ernie-3.0-nano-zh /ernie-3.0-nano-zh
RUN git clone https://huggingface.co/nghuyong/ernie-3.0-base-zh /ernie-3.0-base-zh
RUN git clone https://huggingface.co/shibing624/text2vec-base-chinese /text2vec-base-chinese
RUN git clone https://huggingface.co/GanymedeNil/text2vec-large-chinese /text2vec-large-chinese
RUN git clone https://huggingface.co/shibing624/text2vec-base-chinese-paraphrase /text2vec-base-chinese-paraphrase
RUN git clone https://huggingface.co/shibing624/text2vec-base-chinese-sentence /text2vec-base-chinese-sentence
RUN git clone https://huggingface.co/shibing624/text2vec-base-multilingual /text2vec-base-multilingual
RUN git clone https://huggingface.co/shibing624/text2vec-bge-large-chinese /text2vec-bge-large-chinese
RUN git clone https://huggingface.co/moka-ai/m3e-small /m3e-small
RUN git clone https://huggingface.co/moka-ai/m3e-base /m3e-base
RUN git clone https://huggingface.co/moka-ai/m3e-large /m3e-large
RUN git clone https://huggingface.co/BAAI/bge-small-zh /bge-small-zh
RUN git clone https://huggingface.co/BAAI/bge-base-zh /bge-base-zh
RUN git clone https://huggingface.co/BAAI/bge-large-zh /bge-large-zh
RUN git clone https://huggingface.co/BAAI/bge-large-zh-noinstruct /bge-large-zh-noinstruct
RUN git clone https://huggingface.co/BAAI/bge-base-zh-v1.5 /bge-base-zh-v1.5
RUN git clone https://huggingface.co/BAAI/bge-large-zh-v1.5 /bge-large-zh-v1.5
RUN git clone https://huggingface.co/sensenova/piccolo-base-zh /piccolo-base-zh
RUN git clone https://huggingface.co/sensenova/piccolo-large-zh /piccolo-large-zh
        
# 安装llm_model
RUN git clone https://huggingface.co/THUDM/chatglm2-6b /chatglm2-6b
RUN git clone https://huggingface.co/THUDM/chatglm2-6b-32k /chatglm2-6b-32k
RUN git clone https://huggingface.co/baichuan-inc/Baichuan-13B-Chat /Baichuan-13B-Chat
RUN git clone https://huggingface.co/baichuan-inc/Baichuan2-7B-Chat /Baichuan2-7B-Chat
RUN git clone https://huggingface.co/meta-llama/Llama-2-13b-hf /Llama-2-13b-hf 
RUN git clone https://huggingface.co/Qwen/Qwen-7B /Qwen-7B
RUN git clone https://huggingface.co/Qwen/Qwen-14B /Qwen-14B
RUN git clone https://huggingface.co/Qwen/Qwen-7B-Chat /Qwen-7B-Chat
RUN git clone https://huggingface.co/Qwen/Qwen-14B-Chat /Qwen-14B-Chat

RUN python3 -m pip install --upgrade pip
RUN pip install --upgrade streamlit
# COPY /Langchain-Chatchat/requirements.txt /requirements.txt 
RUN pip install -r /Langchain-Chatchat/requirements.txt
# RUN rm -r /Langchain-Chatchat
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
