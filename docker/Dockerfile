# Base Image
FROM python:3.11
# Labels
LABEL maintainer=chatchat
# Environment Variables
ENV HOME=/usr/local/lib/python3.11/site-packages/chatchat
# Init Environment
RUN ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && \
    echo "Asia/Shanghai" > /etc/timezone && \
    apt-get update -y && \
    apt-get install -y --no-install-recommends libgl1 libglib2.0-0 && \
    apt-get clean && \
    pip install openpyxl networkx faiss-cpu jq unstructured[pdf] opencv-python rapidocr-onnxruntime PyMuPDF rank_bm25 \
    youtube_search && \
    pip install streamlit-chatbox==1.1.12.post4 && \
    rm -rf /var/lib/apt/lists/*
# Install Chatchat
RUN pip install langchain-chatchat -U
# Install ModelProvider
RUN pip install xinference-client
# Make Custom Settings
RUN chatchat-config server --default_bind_host=0.0.0.0 && \
    chatchat-config model --default_llm_model qwen2-instruct
# Copy Data
COPY /libs/chatchat-server/chatchat/configs/model_providers.yaml $HOME/configs/model_providers.yaml
ADD /docker/data.tar.gz $HOME/
WORKDIR $HOME
EXPOSE 7861 8501
ENTRYPOINT ["chatchat", "-a"]