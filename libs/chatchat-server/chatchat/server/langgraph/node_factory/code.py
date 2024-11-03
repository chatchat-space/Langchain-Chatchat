from typing import Dict, Any
from .nodes_registry import regist_nodes
import requests
import json
import re
@regist_nodes(title="Code", description="代码执行器")
def code(*args: Any, **kwargs) -> Dict[str, Any]:
    # 加上try catch
    try:
        code=kwargs['code']
        print_code=f"{code}\nprint(main())"
        #然后将code从kwargs中删除
        del kwargs['code']
        #遍历kwargs，默认value为str类型，将value前后加上双引号，
        for key, value in kwargs.items():
            # escaped_value = re.sub(r'(\r\n|\r|\n)', r'\\1', value)
            kwargs[key] = repr(value)
        data = {
            "languageType": "python",
            "variables": kwargs,
            "code": print_code
        }
        headers = {}
        print("Request Data:")
        print(data)
        url="http://127.0.0.1:5000/runcode"
        
        response = requests.post(url, json=data, headers=headers)
        # response转为json
        response = response.json()
        output:str = response['output']
        #output中的单引号转为双引号
        output = output.replace("'", '"')
        #output转为Dict
        output = json.loads(output)
        print(output)
        return output
    except Exception as e:
        print(e)
        return {"error": str(e)}
    # 先将code从kwargs中取出

    
