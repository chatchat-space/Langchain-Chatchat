import streamlit as st
from streamlit_chatbox import *
from webui_utils import *
from streamlit_option_menu import option_menu


api = ApiRequest()

def dialogue_page():
    with st.sidebar:
        dialogue_mode = st.radio("请选择对话模式",
                                 ["LLM 对话",
                                  "知识库问答",
                                  "Bing 搜索问答"])
        history_len = st.slider("历史对话轮数：", 1, 10, 1)
        if dialogue_mode == "知识库问答":
            selected_kb = st.selectbox("请选择知识库：", get_kb_list())
            with st.expander(f"{selected_kb} 中已存储文件"):
                st.write(get_kb_files(selected_kb))

    # Display chat messages from history on app rerun
    chat_box.output_messages()

    if prompt := st.chat_input("请输入对话内容，换行请使用Ctrl+Enter"):
        chat_box.user_say(prompt)
        chat_box.ai_say("正在思考...")
        # with api.chat_fastchat([{"role": "user", "content": "prompt"}], stream=streaming) as r: # todo: support history len
        text = ""
        r = api.chat_chat(prompt, no_remote_api=True)
        for t in r:
            text += t
            chat_box.update_msg(text)
        chat_box.update_msg(text, streaming=False)
        # with  api.chat_chat(prompt) as r:
        #     for t in r.iter_text(None):
        #         text += t
        #         chat_box.update_msg(text)
        #     chat_box.update_msg(text, streaming=False)

def knowledge_base_edit_page():
    pass


def config_page():
    pass


if __name__ == "__main__":
    st.set_page_config("langchain-chatglm WebUI")

    chat_box = ChatBox()

    pages = {"对话": {"icon": "chat",
                      "func": dialogue_page,
                      },
             "知识库管理": {"icon": "database-fill-gear",
                            "func": knowledge_base_edit_page,
                            },
             "模型配置": {"icon": "gear",
                          "func": config_page,
                          }
             }

    with st.sidebar:
        selected_page = option_menu("langchain-chatglm",
                                    options=list(pages.keys()),
                                    icons=[i["icon"] for i in pages.values()],
                                    menu_icon="chat-quote",
                                    default_index=0)

    pages[selected_page]["func"]()
