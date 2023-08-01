import streamlit as st
from webui_pages.utils import *
from streamlit_option_menu import option_menu
from webui_pages import *

api = ApiRequest()

if __name__ == "__main__":
    st.set_page_config("langchain-chatglm WebUI")

    pages = {"对话": {"icon": "chat",
                      "func": dialogue_page,
                      },
             "知识库管理": {"icon": "database-fill-gear",
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

    pages[selected_page]["func"]()
