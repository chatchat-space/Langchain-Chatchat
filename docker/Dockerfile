# Base Image
FROM python:3.11
# Labels
LABEL maintainer=chatchat
# Environment Variables
ENV HOME=/usr/local/lib/python3.11/site-packages/chatchat
# Init Environment
RUN ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && \
    echo "Asia/Shanghai" > /etc/timezone
# Install Dependencies
RUN apt-get update -y && \
    apt-get install -y --no-install-recommends libgl1 libglib2.0-0 && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*
RUN pip install openpyxl networkx faiss-cpu jq unstructured[pdf] \
    opencv-python rapidocr-onnxruntime PyMuPDF rank_bm25 youtube_search python-docx
# Install Chatchat
RUN pip install --index-url https://pypi.python.org/simple/ langchain-chatchat -U
# Install ModelProvider
RUN pip install xinference-client
# Make Custom Settings
RUN chatchat-config server --default_bind_host=0.0.0.0 && \
    chatchat-config model --default_llm_model qwen2-instruct
# Copy Data
ADD /docker/data.tar.gz $HOME/
WORKDIR $HOME
EXPOSE 7861 8501
ENTRYPOINT ["chatchat", "-a"]
