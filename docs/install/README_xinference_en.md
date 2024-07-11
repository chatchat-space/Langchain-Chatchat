#### xinference Installation Guide

- init conda

```shell
$ wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
$ rm -rf ~/miniconda3/
$ bash Miniconda3-latest-Linux-x86_64.sh
$ conda config --remove channels  https://mirrors.ustc.edu.cn/anaconda/pkgs/main/
$ conda config --remove channels  https://mirrors.ustc.edu.cn/anaconda/pkgs/free/
$ conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/free
$ conda config --add channels  https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/main

```

- Create chatchat environment

```shell
$ conda create -p ~/miniconda3/envs/chatchat python=3.8
$ conda activate ~/miniconda3/envs/chatchat
$ pip install langchain-chatchat -U
$ pip install xinference_client faiss-gpu  "unstructured[pdf]"
```

- Create xinference environment

```shell
$ conda create -p ~/miniconda3/envs/xinference python=3.8
$ conda activate ~/miniconda3/envs/xinference
$ pip install xinference --force
$ pip install tiktoken  sentence-transformers
```

- Start the xinference service

```shell
$ conda activate ~/miniconda3/envs/xinference
$ xinference-local
```

- Edit the registration model script

```shell
$ vim model_registrations.sh
# Add the following content. The model path needs to be modified according to the actual situation
curl 'http://127.0.0.1:9997/v1/model_registrations/LLM' \
  -H 'Accept: */*' \
  -H 'Accept-Language: zh-CN,zh;q=0.9,en;q=0.8' \
  -H 'Connection: keep-alive' \
  -H 'Content-Type: application/json' \
  -H 'Cookie: token=no_auth' \
  -H 'Origin: http://127.0.0.1:9997' \
  -H 'Referer: http://127.0.0.1:9997/ui/' \
  -H 'Sec-Fetch-Dest: empty' \
  -H 'Sec-Fetch-Mode: cors' \
  -H 'Sec-Fetch-Site: same-origin' \
  -H 'User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36' \
  -H 'sec-ch-ua: "Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"' \
  -H 'sec-ch-ua-mobile: ?0' \
  -H 'sec-ch-ua-platform: "Linux"' \
  --data-raw '{"model":"{\"version\":1,\"model_name\":\"autodl-tmp-glm-4-9b-chat\",\"model_description\":\"autodl-tmp-glm-4-9b-chat\",\"context_length\":2048,\"model_lang\":[\"en\",\"zh\"],\"model_ability\":[\"generate\",\"chat\"],\"model_family\":\"glm4-chat\",\"model_specs\":[{\"model_uri\":\"/root/autodl-tmp/glm-4-9b-chat\",\"model_size_in_billions\":9,\"model_format\":\"pytorch\",\"quantizations\":[\"none\"]}],\"prompt_style\":{\"style_name\":\"CHATGLM3\",\"system_prompt\":\"\",\"roles\":[\"user\",\"assistant\"],\"intra_message_sep\":\"\",\"inter_message_sep\":\"\",\"stop\":[\"<|endoftext|>\",\"<|user|>\",\"<|observation|>\"],\"stop_token_ids\":[151329,151336,151338]}}","persist":true}' 
```  

- Edit and register embedding script

```shell
$ vim model_registrations_emb.sh
# 添加以下内容。模型路径需要根据实际情况修改
curl 'http://127.0.0.1:9997/v1/model_registrations/embedding' \
  -H 'Accept: */*' \
  -H 'Accept-Language: zh-CN,zh;q=0.9,en;q=0.8' \
  -H 'Connection: keep-alive' \
  -H 'Content-Type: application/json' \
  -H 'Cookie: token=no_auth' \
  -H 'Origin: http://127.0.0.1:9997' \
  -H 'Referer: http://127.0.0.1:9997/ui/' \
  -H 'Sec-Fetch-Dest: empty' \
  -H 'Sec-Fetch-Mode: cors' \
  -H 'Sec-Fetch-Site: same-origin' \
  -H 'User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36' \
  -H 'sec-ch-ua: "Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"' \
  -H 'sec-ch-ua-mobile: ?0' \
  -H 'sec-ch-ua-platform: "Linux"' \
  --data-raw '{"model":"{\"model_name\":\"autodl-tmp-bge-large-zh\",\"dimensions\":768,\"max_tokens\":512,\"model_uri\":\"/root/model/bge-large-zh\",\"language\":[\"en\",\"zh\"]}","persist":true}'
``` 

- Edit the startup model script

```shell
$ vim start_models.sh
# 添加以下内容。模型路径需要根据实际情况修改
curl 'http://127.0.0.1:9997/v1/models' \
  -H 'Accept: */*' \
  -H 'Accept-Language: zh-CN,zh;q=0.9,en;q=0.8' \
  -H 'Connection: keep-alive' \
  -H 'Content-Type: application/json' \
  -H 'Cookie: token=no_auth' \
  -H 'Origin: http://127.0.0.1:9997' \
  -H 'Referer: http://127.0.0.1:9997/ui/' \
  -H 'Sec-Fetch-Dest: empty' \
  -H 'Sec-Fetch-Mode: cors' \
  -H 'Sec-Fetch-Site: same-origin' \
  -H 'User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36' \
  -H 'sec-ch-ua: "Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"' \
  -H 'sec-ch-ua-mobile: ?0' \
  -H 'sec-ch-ua-platform: "Linux"' \
  --data-raw '{"model_uid":null,"model_name":"autodl-tmp-glm-4-9b-chat","model_type":"LLM","model_engine":"Transformers","model_format":"pytorch","model_size_in_billions":9,"quantization":"none","n_gpu":"auto","replica":1,"request_limits":null,"worker_ip":null,"gpu_idx":null}'
```

- Edit and start embedding script

```shell
$ vim start_models_emb.sh
# 添加以下内容。模型路径需要根据实际情况修改
curl 'http://127.0.0.1:9997/v1/models' \
  -H 'Accept: */*' \
  -H 'Accept-Language: zh-CN,zh;q=0.9,en;q=0.8' \
  -H 'Connection: keep-alive' \
  -H 'Content-Type: application/json' \
  -H 'Cookie: token=no_auth' \
  -H 'Origin: http://127.0.0.1:9997' \
  -H 'Referer: http://127.0.0.1:9997/ui/' \
  -H 'Sec-Fetch-Dest: empty' \
  -H 'Sec-Fetch-Mode: cors' \
  -H 'Sec-Fetch-Site: same-origin' \
  -H 'User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36' \
  -H 'sec-ch-ua: "Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"' \
  -H 'sec-ch-ua-mobile: ?0' \
  -H 'sec-ch-ua-platform: "Linux"' \
  --data-raw '{"model_uid":"bge-large-zh-v1.5","model_name":"autodl-tmp-bge-large-zh","model_type":"embedding","replica":1,"n_gpu":"auto","worker_ip":null,"gpu_idx":null}'
```

- Start the model

```shell
$ bash ./model_registrations.sh
$ bash ./model_registrations_emb.sh
$ bash ./start_models.sh
$ bash ./start_models_emb.sh

```

- Initialize chatchat configuration

```shell
$ conda activate ~/miniconda3/envs/chatchat
$ chatchat-config basic --verbose true
$ chatchat-config basic --data ~/chatchat-data
```

- Set up the model

```shell
$ chatchat-config model --set_model_platforms "[{
    \"platform_name\": \"xinference\",
    \"platform_type\": \"xinference\",
    \"api_base_url\": \"http://127.0.0.1:9997/v1\",
    \"api_key\": \"EMPT\",
    \"api_concurrencies\": 5,
    \"llm_models\": [
        \"autodl-tmp-glm-4-9b-chat\"
    ],
    \"embed_models\": [
        \"bge-large-zh-v1.5\"
    ],
    \"image_models\": [],
    \"reranking_models\": [],
    \"speech2text_models\": [],
    \"tts_models\": []
}]"

```

- Initialize knowledge base

```shell
$ conda activate ~/miniconda3/envs/chatchat
$ chatchat-kb -r

```

- Start chatchat

```shell
$ conda activate ~/miniconda3/envs/chatchat
$ chatchat -a

```
