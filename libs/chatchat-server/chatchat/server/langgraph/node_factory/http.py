from typing import Dict, Any
from .nodes_registry import regist_nodes
import requests
import json
import re
@regist_nodes(title="Http", description="发送GET/POST网络请求")
def http(**kwargs) -> Dict[str, Any]:
    method = kwargs.pop("method", "GET")
    url = kwargs.pop("url", "")
    content_type = kwargs.pop("content_type", "application/x-www-form-urlencoded")
    headers={}
    # 检查请求方法是否合法
    try:  
        if method.upper() == 'GET':  
            response = requests.get(url, headers=headers, params=kwargs)  
        elif method.upper() == 'POST':  
            if content_type == 'application/json':
                response = requests.post(url, headers=headers, json=kwargs)  
            elif content_type == 'application/x-www-form-urlencoded':
                response = requests.post(url, headers=headers, data=kwargs)  
        # 你可以根据需要添加更多的HTTP方法，比如PUT, DELETE等  
        else:  
            raise ValueError(f"Unsupported method: {method}")  
  
        # 检查响应状态码  
        response.raise_for_status()  # 如果响应状态码不是200，会引发HTTPError异常  
        
        # 尝试获取正确的编码，这里默认使用utf-8  
        # 如果响应头中有charset信息，应该优先使用该信息  
        charset = response.headers.get('content-type', '').split('charset=')[-1] if 'charset=' in response.headers.get('content-type', '') else 'utf-8'  
        try:  
            # 使用正确的编码解码响应内容  
            response_text = response.content.decode(charset)  
        except UnicodeDecodeError:  
            # 如果解码失败，尝试使用utf-8作为回退  
            response_text = response.content.decode('utf-8')  
  
        return {"response": response_text}
  
    except requests.exceptions.RequestException as e:  
        print(f"Request failed: {e}")  
        return None

    
