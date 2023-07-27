import streamlit as st
from streamlit_option_menu import option_menu
import openai

def dialogue_page():
    with st.sidebar:
        dialogue_mode = st.radio("请选择对话模式",
                                 ["LLM 对话",
                                  "知识库问答",
                                  "Bing 搜索问答"])
        if dialogue_mode == "知识库问答":
            selected_kb = st.selectbox("请选择知识库：", ["知识库1", "知识库2"])
            with st.expander(f"{selected_kb} 中已存储文件"):
                st.write("123")

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("What is up?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            for response in openai.ChatCompletion.create(
                    model=OPENAI_MODEL,
                    messages=[
                        {"role": m["role"], "content": m["content"]}
                        for m in st.session_state.messages
                    ],
                    stream=True,
            ):
                full_response += response.choices[0].delta.get("content", "")
                message_placeholder.markdown(full_response + "▌")
            message_placeholder.markdown(full_response)
        st.session_state.messages.append({"role": "assistant", "content": full_response})


def knowledge_base_edit_page():
    pass


def config_page():
    pass


if __name__ == "__main__":
    st.set_page_config("langchain-chatglm WebUI")

    if "messages" not in st.session_state:
        st.session_state.messages = []

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
