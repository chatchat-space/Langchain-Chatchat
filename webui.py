# 运行方式：
# 1. 安装必要的包：pip install streamlit-option-menu streamlit-chatbox>=1.1.6
# 2. 运行本机fastchat服务：python server\llm_api.py 或者 运行对应的sh文件
# 3. 运行API服务器：python server/api.py。如果使用api = ApiRequest(no_remote_api=True)，该步可以跳过。
# 4. 运行WEB UI：streamlit run webui.py --server.port 7860

import streamlit as st
from webui_pages.utils import *
from streamlit_option_menu import option_menu
from webui_pages import *


api = ApiRequest(base_url="http://127.0.0.1:7861", no_remote_api=False)

if __name__ == "__main__":
    st.set_page_config("langchain-chatglm WebUI", layout="wide")

    if not chat_box.chat_inited:
        st.toast(f"欢迎使用 [`Langchain-Chatglm`](https://github.com/chatchat-space/langchain-chatglm) ! \n\n当前使用模型`{LLM_MODEL}`, 您可以开始提问了.")
        st.toast(" ")

    # pages = {"对话1": {"icon": "chat",
    #                   "func": dialogue_page,
    #                   },
    #          "对话2": {"icon": "chat",
    #                    "func": dialogue_page,
    #                    },
    #          "对话3": {"icon": "chat",
    #                    "func": dialogue_page,
    #                    },
    #          "新建对话": {"icon": "plus-circle",
    #                    "func": dialogue_page,
    #                    },
    #          "---": {"icon": None,
    #                  "func": None},
    #          "知识库管理": {"icon": "database-fill-gear",
    #                         "func": knowledge_base_page,
    #                         },
    #          "模型配置": {"icon": "gear",
    #                       "func": model_config_page,
    #                       }
    #          }

    pages = {"对话": {"icon": "chat",
                      "func": dialogue_page,
                      },
             "知识库管理": {"icon": "hdd-stack",
                            "func": knowledge_base_page,
                            },
             "模型配置": {"icon": "gear",
                          "func": model_config_page,
                          }
             }

    with st.sidebar:
        selected_page = option_menu("langchain-chatglm",
                                    options=list(pages.keys()),
                                    icons=[i["icon"] for i in pages.values()],
                                    menu_icon="chat-quote",
                                    default_index=0)

    pages[selected_page]["func"](api)
