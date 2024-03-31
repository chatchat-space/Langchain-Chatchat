import base64
import uuid
import os
import re
import time
from typing import List, Dict

import streamlit as st
from streamlit_antd_components.utils import ParseItems

import openai
from streamlit_chatbox import *
from streamlit_modal import Modal
from datetime import datetime

from chatchat.configs import (LLM_MODEL_CONFIG, SUPPORT_AGENT_MODELS, MODEL_PLATFORMS)
from chatchat.server.callback_handler.agent_callback_handler import AgentStatus
from chatchat.server.utils import MsgType, get_config_models
from chatchat.server.utils import get_tool_config
from chatchat.webui_pages.utils import *
from chatchat.webui_pages.dialogue.utils import process_files


img_dir = (Path(__file__).absolute().parent.parent.parent)

chat_box = ChatBox(
    assistant_avatar=os.path.join(
        img_dir,
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

    # 弹出自定义命令帮助信息
    modal = Modal("自定义命令", key="cmd_help", max_width="500")
    if modal.is_open():
        with modal.container():
            cmds = [x for x in parse_command.__doc__.split("\n") if x.strip().startswith("/")]
            st.write("\n\n".join(cmds))

    with st.sidebar:
        tab1, tab2 = st.tabs(["对话设置", "模型设置"])

        with tab1:
            use_agent = st.checkbox("启用Agent", True, help="请确保选择的模型具备Agent能力")
            # 选择工具
            tools = api.list_tools()
            if use_agent:
                selected_tools = st.multiselect("选择工具", list(tools), format_func=lambda x: tools[x]["title"])
            else:
                selected_tool = st.selectbox("选择工具", list(tools), format_func=lambda x: tools[x]["title"])
                selected_tools = [selected_tool]
            selected_tool_configs = {name: tool["config"] for name, tool in tools.items() if name in selected_tools}

            # 当不启用Agent时，手动生成工具参数
            # TODO: 需要更精细的控制控件
            tool_input = {}
            if not use_agent and len(selected_tools) == 1:
                with st.expander("工具参数", True):
                    for k, v in tools[selected_tools[0]]["args"].items():
                        if choices := v.get("choices", v.get("enum")):
                            tool_input[k] = st.selectbox(v["title"], choices)
                        else:
                            if v["type"] == "integer":
                                tool_input[k] = st.slider(v["title"], value=v.get("default"))
                            elif v["type"] == "number":
                                tool_input[k] = st.slider(v["title"], value=v.get("default"), step=0.1)
                            else:
                                tool_input[k] = st.text_input(v["title"], v.get("default"))


            uploaded_file = st.file_uploader("上传附件", accept_multiple_files=False)
            files_upload = process_files(files=[uploaded_file]) if uploaded_file else None
        
        with tab2:
            # 会话
            conv_names = list(st.session_state["conversation_ids"].keys())
            index = 0
            if st.session_state.get("cur_conv_name") in conv_names:
                index = conv_names.index(st.session_state.get("cur_conv_name"))
            conversation_name = st.selectbox("当前会话", conv_names, index=index)
            chat_box.use_chat_name(conversation_name)
            conversation_id = st.session_state["conversation_ids"][conversation_name]

            # 模型
            platforms = ["所有"] + [x["platform_name"] for x in MODEL_PLATFORMS]
            platform = st.selectbox("选择模型平台", platforms)
            llm_models = list(get_config_models(model_type="llm", platform_name=None if platform=="所有" else platform))
            llm_model = st.selectbox("选择LLM模型", llm_models)

            #  传入后端的内容
            chat_model_config = {key: {} for key in LLM_MODEL_CONFIG.keys()}
            for key in LLM_MODEL_CONFIG:
                if LLM_MODEL_CONFIG[key]:
                    first_key = next(iter(LLM_MODEL_CONFIG[key]))
                    chat_model_config[key][first_key] = LLM_MODEL_CONFIG[key][first_key]

            if llm_model is not None:
                chat_model_config['llm_model'][llm_model] = LLM_MODEL_CONFIG['llm_model'].get(llm_model, {})

    # Display chat messages from history on app rerun
    chat_box.output_messages()
    chat_input_placeholder = "请输入对话内容，换行请使用Shift+Enter。输入/help查看自定义命令 "

    # def on_feedback(
    #         feedback,
    #         message_id: str = "",
    #         history_index: int = -1,
    # ):

    #     reason = feedback["text"]
    #     score_int = chat_box.set_feedback(feedback=feedback, history_index=history_index)
    #     api.chat_feedback(message_id=message_id,
    #                       score=score_int,
    #                       reason=reason)
    #     st.session_state["need_rerun"] = True

    # feedback_kwargs = {
    #     "feedback_type": "thumbs",
    #     "optional_text_label": "欢迎反馈您打分的理由",
    # }

    if prompt := st.chat_input(chat_input_placeholder, key="prompt"):
        if parse_command(text=prompt, modal=modal):
            st.rerun()
        else:
            history = get_messages_history(
                chat_model_config["llm_model"].get(next(iter(chat_model_config["llm_model"])), {}).get("history_len", 1)
            )
            chat_box.user_say(prompt)
            if files_upload:
                if files_upload["images"]:
                    st.markdown(f'<img src="data:image/jpeg;base64,{files_upload["images"][0]}" width="300">',
                                unsafe_allow_html=True)
                elif files_upload["videos"]:
                    st.markdown(
                        f'<video width="400" height="300" controls><source src="data:video/mp4;base64,{files_upload["videos"][0]}" type="video/mp4"></video>',
                        unsafe_allow_html=True)
                elif files_upload["audios"]:
                    st.markdown(
                        f'<audio controls><source src="data:audio/wav;base64,{files_upload["audios"][0]}" type="audio/wav"></audio>',
                        unsafe_allow_html=True)

            chat_box.ai_say("正在思考...")
            text = ""
            started = False

            client = openai.Client(base_url=f"{api_address()}/chat", api_key="NONE")
            messages = history + [{"role": "user", "content": prompt}]
            tools = list(selected_tool_configs)
            if len(selected_tools) == 1:
                tool_choice = selected_tools[0]
            else:
                tool_choice = None
            # 如果 tool_input 中有空的字段，设为用户输入
            for k in tool_input:
                if tool_input[k] in [None, ""]:
                    tool_input[k] = prompt

            extra_body = dict(
                            metadata=files_upload,
                            chat_model_config=chat_model_config,
                            conversation_id=conversation_id,
                            tool_input = tool_input,
                            )
            for d in client.chat.completions.create(
                    messages=messages,
                    model=llm_model,
                    stream=True,
                    tools=tools,
                    tool_choice=tool_choice,
                    extra_body=extra_body,
                ):
                # print("\n\n", d.status, "\n", d, "\n\n")
                message_id = d.message_id
                metadata = {
                    "message_id": message_id,
                }

                # clear initial message
                if not started:
                    chat_box.update_msg("", streaming=False)
                    started = True

                if d.status == AgentStatus.error:
                    st.error(d.choices[0].delta.content)
                elif d.status == AgentStatus.llm_start:
                    chat_box.insert_msg("正在解读工具输出结果...")
                    text = d.choices[0].delta.content or ""
                elif d.status == AgentStatus.llm_new_token:
                    text += d.choices[0].delta.content or ""
                    chat_box.update_msg(text.replace("\n", "\n\n"), streaming=True, metadata=metadata)
                elif d.status == AgentStatus.llm_end:
                    text += d.choices[0].delta.content or ""
                    chat_box.update_msg(text.replace("\n", "\n\n"), streaming=False, metadata=metadata)
                # tool 的输出与 llm 输出重复了
                # elif d.status == AgentStatus.tool_start:
                #     formatted_data = {
                #         "Function": d.choices[0].delta.tool_calls[0].function.name,
                #         "function_input": d.choices[0].delta.tool_calls[0].function.arguments,
                #     }
                #     formatted_json = json.dumps(formatted_data, indent=2, ensure_ascii=False)
                #     text = """\n```{}\n```\n""".format(formatted_json)
                #     chat_box.insert_msg( # TODO: insert text directly not shown
                #         Markdown(text, title="Function call", in_expander=True, expanded=True, state="running"))
                # elif d.status == AgentStatus.tool_end:
                #     tool_output = d.choices[0].delta.tool_calls[0].tool_output
                #     if d.message_type == MsgType.IMAGE:
                #         for url in json.loads(tool_output).get("images", []):
                #             url = f"{api.base_url}/media/{url}"
                #             chat_box.insert_msg(Image(url))
                #         chat_box.update_msg(expanded=False, state="complete")
                #     else:
                #         text += """\n```\nObservation:\n{}\n```\n""".format(tool_output)
                #         chat_box.update_msg(text, streaming=False, expanded=False, state="complete")
                elif d.status == AgentStatus.agent_finish:
                    text = d.choices[0].delta.content or ""
                    chat_box.update_msg(text.replace("\n", "\n\n"))
                elif d.status == None: # not agent chat
                    if getattr(d, "is_ref", False):
                        chat_box.insert_msg(Markdown(d.choices[0].delta.content or "", in_expander=True, state="complete", title="参考资料"))
                        chat_box.insert_msg("")
                    else:
                        text += d.choices[0].delta.content or ""
                        chat_box.update_msg(text.replace("\n", "\n\n"), streaming=True, metadata=metadata)
            chat_box.update_msg(text, streaming=False, metadata=metadata)

            if os.path.exists("tmp/image.jpg"):
                with open("tmp/image.jpg", "rb") as image_file:
                    encoded_string = base64.b64encode(image_file.read()).decode()
                    img_tag = f'<img src="data:image/jpeg;base64,{encoded_string}" width="300">'
                    st.markdown(img_tag, unsafe_allow_html=True)
                os.remove("tmp/image.jpg")
            # chat_box.show_feedback(**feedback_kwargs,
            #                        key=message_id,
            #                        on_submit=on_feedback,
            #                        kwargs={"message_id": message_id, "history_index": len(chat_box.history) - 1})

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
    with tab1:
        cols = st.columns(2)
        export_btn = cols[0]
        if cols[1].button(
                "清空对话",
                use_container_width=True,
        ):
            chat_box.reset_history()
            st.rerun()

        warning_placeholder = st.empty()

    export_btn.download_button(
        "导出记录",
        "".join(chat_box.export2md()),
        file_name=f"{now:%Y-%m-%d %H.%M}_对话记录.md",
        mime="text/markdown",
        use_container_width=True,
    )

    # st.write(chat_box.history)
