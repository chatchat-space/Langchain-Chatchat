import streamlit as st

from webui_pages.dialogue.utils import process_files
from webui_pages.utils import *
from streamlit_chatbox import *
from streamlit_modal import Modal
from datetime import datetime
import os
import re
import time
from configs import (TOOL_CONFIG, LLM_MODEL_CONFIG)
from server.knowledge_base.utils import LOADER_DICT
import uuid
from typing import List, Dict

chat_box = ChatBox(
    assistant_avatar=os.path.join(
        "img",
        "chatchat_icon_blue_square_v2.png"
    )
)


def get_messages_history(history_len: int, content_in_expander: bool = False) -> List[Dict]:
    '''
    返回消息历史。
    content_in_expander控制是否返回expander元素中的内容，一般导出的时候可以选上，传入LLM的history不需要
    '''

    def filter(msg):
        content = [x for x in msg["elements"] if x._output_method in ["markdown", "text"]]
        if not content_in_expander:
            content = [x for x in content if not x._in_expander]
        content = [x.content for x in content]

        return {
            "role": msg["role"],
            "content": "\n\n".join(content),
        }

    return chat_box.filter_history(history_len=history_len, filter=filter)


@st.cache_data
def upload_temp_docs(files, _api: ApiRequest) -> str:
    '''
    将文件上传到临时目录，用于文件对话
    返回临时向量库ID
    '''
    return _api.upload_temp_docs(files).get("data", {}).get("id")


def parse_command(text: str, modal: Modal) -> bool:
    '''
    检查用户是否输入了自定义命令，当前支持：
    /new {session_name}。如果未提供名称，默认为“会话X”
    /del {session_name}。如果未提供名称，在会话数量>1的情况下，删除当前会话。
    /clear {session_name}。如果未提供名称，默认清除当前会话
    /stop {session_name}。如果未提供名称，默认停止当前会话
    /help。查看命令帮助
    返回值：输入的是命令返回True，否则返回False
    '''
    if m := re.match(r"/([^\s]+)\s*(.*)", text):
        cmd, name = m.groups()
        name = name.strip()
        conv_names = chat_box.get_chat_names()
        if cmd == "help":
            modal.open()
        elif cmd == "new":
            if not name:
                i = 1
                while True:
                    name = f"会话{i}"
                    if name not in conv_names:
                        break
                    i += 1
            if name in st.session_state["conversation_ids"]:
                st.error(f"该会话名称 “{name}” 已存在")
                time.sleep(1)
            else:
                st.session_state["conversation_ids"][name] = uuid.uuid4().hex
                st.session_state["cur_conv_name"] = name
        elif cmd == "del":
            name = name or st.session_state.get("cur_conv_name")
            if len(conv_names) == 1:
                st.error("这是最后一个会话，无法删除")
                time.sleep(1)
            elif not name or name not in st.session_state["conversation_ids"]:
                st.error(f"无效的会话名称：“{name}”")
                time.sleep(1)
            else:
                st.session_state["conversation_ids"].pop(name, None)
                chat_box.del_chat_name(name)
                st.session_state["cur_conv_name"] = ""
        elif cmd == "clear":
            chat_box.reset_history(name=name or None)
        return True
    return False


def dialogue_page(api: ApiRequest, is_lite: bool = False):
    st.session_state.setdefault("conversation_ids", {})
    st.session_state["conversation_ids"].setdefault(chat_box.cur_chat_name, uuid.uuid4().hex)
    st.session_state.setdefault("file_chat_id", None)
    default_model = api.get_default_llm_model()[0]

    if not chat_box.chat_inited:
        st.toast(
            f"欢迎使用 [`Langchain-Chatchat`](https://github.com/chatchat-space/Langchain-Chatchat) ! \n\n"
            f"当前运行的模型`{default_model}`, 您可以开始提问了."
        )
        chat_box.init_session()

    # 弹出自定义命令帮助信息
    modal = Modal("自定义命令", key="cmd_help", max_width="500")
    if modal.is_open():
        with modal.container():
            cmds = [x for x in parse_command.__doc__.split("\n") if x.strip().startswith("/")]
            st.write("\n\n".join(cmds))

    with st.sidebar:
        conv_names = list(st.session_state["conversation_ids"].keys())
        index = 0

        tools = list(TOOL_CONFIG.keys())
        selected_tool_configs = {}

        with st.expander("工具栏"):
            for tool in tools:
                is_selected = st.checkbox(tool, value=TOOL_CONFIG[tool]["use"], key=tool)
                if is_selected:
                    selected_tool_configs[tool] = TOOL_CONFIG[tool]

        if st.session_state.get("cur_conv_name") in conv_names:
            index = conv_names.index(st.session_state.get("cur_conv_name"))
        conversation_name = st.selectbox("当前会话", conv_names, index=index)
        chat_box.use_chat_name(conversation_name)
        conversation_id = st.session_state["conversation_ids"][conversation_name]

        # def on_mode_change():
        #     mode = st.session_state.dialogue_mode
        #     text = f"已切换到 {mode} 模式。"
        #     st.toast(text)

        # dialogue_modes = ["智能对话",
        #                   "文件对话",
        #                   ]
        # dialogue_mode = st.selectbox("请选择对话模式：",
        #                              dialogue_modes,
        #                              index=0,
        #                              on_change=on_mode_change,
        #                              key="dialogue_mode",
        #                              )

        def on_llm_change():
            if llm_model:
                config = api.get_model_config(llm_model)
                if not config.get("online_api"):  # 只有本地model_worker可以切换模型
                    st.session_state["prev_llm_model"] = llm_model
                st.session_state["cur_llm_model"] = st.session_state.llm_model

        def llm_model_format_func(x):
            if x in running_models:
                return f"{x} (Running)"
            return x

        running_models = list(api.list_running_models())
        available_models = []
        config_models = api.list_config_models()
        if not is_lite:
            for k, v in config_models.get("local", {}).items():  # 列出配置了有效本地路径的模型
                if (v.get("model_path_exists")
                        and k not in running_models):
                    available_models.append(k)
        for k, v in config_models.get("online", {}).items():
            if not v.get("provider") and k not in running_models and k in LLM_MODELS:
                available_models.append(k)
        llm_models = running_models + available_models + ["openai-api"]
        cur_llm_model = st.session_state.get("cur_llm_model", default_model)
        if cur_llm_model in llm_models:
            index = llm_models.index(cur_llm_model)
        else:
            index = 0
        llm_model = st.selectbox("选择LLM模型",
                                 llm_models,
                                 index,
                                 format_func=llm_model_format_func,
                                 on_change=on_llm_change,
                                 key="llm_model",
                                 )

        #  传入后端的内容
        model_config = {key: {} for key in LLM_MODEL_CONFIG.keys()}

        for key in LLM_MODEL_CONFIG:
            if key == 'llm_model':
                continue
            if LLM_MODEL_CONFIG[key]:
                first_key = next(iter(LLM_MODEL_CONFIG[key]))
                model_config[key][first_key] = LLM_MODEL_CONFIG[key][first_key]

        if llm_model is not None:
            model_config['llm_model'][llm_model] = LLM_MODEL_CONFIG['llm_model'][llm_model]

        files = st.file_uploader("上传附件",
                                 type=[i for ls in LOADER_DICT.values() for i in ls],
                                 accept_multiple_files=True)
        files_upload = process_files(files=files) if files else None
        print(len(files_upload)) if files_upload else None

        # if dialogue_mode == "文件对话":
        #     with st.expander("文件对话配置", True):
        #         files = st.file_uploader("上传知识文件：",
        #                                  [i for ls in LOADER_DICT.values() for i in ls],
        #                                  accept_multiple_files=True,
        #                                  )
        #         kb_top_k = st.number_input("匹配知识条数：", 1, 20, VECTOR_SEARCH_TOP_K)
        #         score_threshold = st.slider("知识匹配分数阈值：", 0.0, 2.0, float(SCORE_THRESHOLD), 0.01)
        #         if st.button("开始上传", disabled=len(files) == 0):
        #             st.session_state["file_chat_id"] = upload_temp_docs(files, api)
    # Display chat messages from history on app rerun

    chat_box.output_messages()
    chat_input_placeholder = "请输入对话内容，换行请使用Shift+Enter。输入/help查看自定义命令 "

    def on_feedback(
            feedback,
            message_id: str = "",
            history_index: int = -1,
    ):

        reason = feedback["text"]
        score_int = chat_box.set_feedback(feedback=feedback, history_index=history_index)
        api.chat_feedback(message_id=message_id,
                          score=score_int,
                          reason=reason)
        st.session_state["need_rerun"] = True

    feedback_kwargs = {
        "feedback_type": "thumbs",
        "optional_text_label": "欢迎反馈您打分的理由",
    }

    if prompt := st.chat_input(chat_input_placeholder, key="prompt"):
        if parse_command(text=prompt, modal=modal):  # 用户输入自定义命令
            st.rerun()
        else:
            history = get_messages_history(
                model_config["llm_model"][next(iter(model_config["llm_model"]))]["history_len"])
            chat_box.user_say(prompt)

            chat_box.ai_say("正在思考...")
            text = ""
            message_id = ""
            element_index = 0
            for d in api.chat_chat(query=prompt,
                                   metadata=files_upload,
                                   history=history,
                                   model_config=model_config,
                                   conversation_id=conversation_id,
                                   tool_config=selected_tool_configs,
                                   ):
                try:
                    d = json.loads(d)
                except:
                    pass
                message_id = d.get("message_id", "")
                metadata = {
                    "message_id": message_id,
                }
                if error_msg := check_error_msg(d):
                    st.error(error_msg)
                if chunk := d.get("agent_action"):
                    chat_box.insert_msg(Markdown("...", in_expander=True, title="Tools", state="complete"))
                    element_index = 1
                    formatted_data = {
                        "action": chunk["tool_name"],
                        "action_input": chunk["tool_input"]
                    }
                    formatted_json = json.dumps(formatted_data, indent=2, ensure_ascii=False)
                    text += f"\n```\nInput Params:\n" + formatted_json + f"\n```\n"
                    chat_box.update_msg(text, element_index=element_index, metadata=metadata)
                if chunk := d.get("text"):
                    text += chunk
                    chat_box.update_msg(text, element_index=element_index, metadata=metadata)
                if chunk := d.get("agent_finish"):
                    element_index = 0
                    text = chunk
                chat_box.update_msg(text, streaming=False, element_index=element_index, metadata=metadata)
            chat_box.show_feedback(**feedback_kwargs,
                                   key=message_id,
                                   on_submit=on_feedback,
                                   kwargs={"message_id": message_id, "history_index": len(chat_box.history) - 1})

            # elif dialogue_mode == "文件对话":
            #     if st.session_state["file_chat_id"] is None:
            #         st.error("请先上传文件再进行对话")
            #         st.stop()
            #     chat_box.ai_say([
            #         f"正在查询文件 `{st.session_state['file_chat_id']}` ...",
            #         Markdown("...", in_expander=True, title="文件匹配结果", state="complete"),
            #     ])
            #     text = ""
            #     for d in api.file_chat(prompt,
            #                            knowledge_id=st.session_state["file_chat_id"],
            #                            top_k=kb_top_k,
            #                            score_threshold=score_threshold,
            #                            history=history,
            #                            model=llm_model,
            #                            prompt_name=prompt_template_name,
            #                            temperature=temperature):
            #         if error_msg := check_error_msg(d):
            #             st.error(error_msg)
            #         elif chunk := d.get("answer"):
            #             text += chunk
            #             chat_box.update_msg(text, element_index=0)
            #     chat_box.update_msg(text, element_index=0, streaming=False)
            #     chat_box.update_msg("\n\n".join(d.get("docs", [])), element_index=1, streaming=False)
    if st.session_state.get("need_rerun"):
        st.session_state["need_rerun"] = False
        st.rerun()

    now = datetime.now()
    with st.sidebar:

        cols = st.columns(2)
        export_btn = cols[0]
        if cols[1].button(
                "清空对话",
                use_container_width=True,
        ):
            chat_box.reset_history()
            st.rerun()

    export_btn.download_button(
        "导出记录",
        "".join(chat_box.export2md()),
        file_name=f"{now:%Y-%m-%d %H.%M}_对话记录.md",
        mime="text/markdown",
        use_container_width=True,
    )
