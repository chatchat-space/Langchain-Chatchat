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
  --data-raw '{"model":"{\"version\":1,\"model_name\":\"autodl-tmp-glm-4-9b-chat\",\"model_description\":\"autodl-tmp-glm-4-9b-chat\",\"context_length\":2048,\"model_lang\":[\"en\",\"zh\"],\"model_ability\":[\"generate\",\"chat\"],\"model_family\":\"glm4-chat\",\"model_specs\":[{\"model_uri\":\"/root/autodl-tmp/glm-4-9b-chat\",\"model_size_in_billions\":9,\"model_format\":\"pytorch\",\"quantizations\":[\"none\"]}],\"prompt_style\":{\"style_name\":\"CHATGLM3\",\"system_prompt\":\"\",\"roles\":[\"user\",\"assistant\"],\"intra_message_sep\":\"\",\"inter_message_sep\":\"\",\"stop\":[\"<|endoftext|>\",\"<|user|>\",\"<|observation|>\"],\"stop_token_ids\":[151329,151336,151338]}}","persist":true}' ;
 