import streamlit as st
from webui_pages.utils import *
from streamlit_chatbox import *
from datetime import datetime
from server.chat.search_engine_chat import SEARCH_ENGINES
import os
from configs import LLM_MODEL, TEMPERATURE
from server.utils import get_model_worker_config
from typing import List, Dict

chat_box = ChatBox(
    assistant_avatar=os.path.join(
        "img",
        "chatchat_icon_blue_square_v2.png"
    )
)
Questions_prompt="""
Please extract the questions from the meeting text that investors asked the founders.
meeting text:'''{record}'''
===
formation instruction:
1.Returns a stric format comma-separated questions in markdown
2.Each answer only needs to start with 'Q:...' when returned,eg:
Q:-put questions detail string here-,\n\n
Q:-put questions detail string here-,\n\n
... 
===
requirement:
1.	You are only allowed to return a maximum of 3 questions, and you can decide the number \
of questions to return based on the quality of the questions;
2.	make full use of contextual information to supplement \
The returned content needs to be logical, non-repetitive and rigorously organized\
the description of the problem, and the length of the problem must be within 30-80 words
3.Use explicit names instead of pronouns(such as 'they','we','you'), \
Please make it clear that the pronoun refers to the content\
4.all answers must be returned in English
"""
questions = [
    # industry
    '公司产品的市场规模，并总结对应的市场规模测算逻辑',
    '市场增速以及背后的驱动力',
    '上游的供应链情况',
    '公司的上游原材料是哪些',
    '主要供货商是谁',
    '公司和供货商是怎么合作的，或者是如何管理供应链的',
    '下游客户情况',
    '公司的产品直接卖给谁',
    '他们一般都在什么规模、利润率多少',
    '公司产品的应用场景有哪些',
    
    # product
    '产品描述：公司主要提供哪些产品或者服务，如果有多个产品/服务，单独列出来',
    '产品价值；用户原来用的是什么产品/服务，相比于原来的产品/服务，公司产品的核心优势是什么，解决了客户什么问题，给客户带来了多大的价值',
    '该产品的技术细节是什么，主要亮点是什么',
    '产品壁垒在哪里，可以是技术壁垒，也可以是行业认知等',
    '产品开发的进展',
    '如果还没有量产，哪些现在研发到什么阶段了,是还在研发，还是已经有demo，还是在客户测试阶段，以及何时能够正式商业化，按时间线总结',
    '如果已经量产，那么具体出货量/产能/营收/客户数是多少，在客户那边的使用情况如何',
    '公司提供的是标准化的产品/服务，还是定制化的项目',
    '如果是定制化的项目，请总结项目周期一般要多长，要配置多少人，一个项目的成本多大',
    '对标公司：公司对标的是哪些国外公司，或者国内头部的公司，这些对标公司的特点是什么',
    '竞争情况：国内有哪些人或者公司在做类似的事情，例如再做类似研究的教授，或者一些做类似业务的公司，具体一点，把提到做类似事情的所有公司或者团队都列出来，这点非常重要',
    '这些竞争对手，他们提供的产品/技术，和公司的产品/技术有什么区别',

    # company
    '销售：公司的销售模式是什么，销售多少人，主要的销售流程是怎么样的（从初次接触客户到签单，每一步的环节/以及所需要的时间，对接的是客户什么部门）',
    '管理: 包括对公司员工、工厂、运营的管理',
    '研发：公司现在研发团队多少人，有什么特点，主要在研发什么方向',

    # finance
    '近三年的合同额情况、确认收入情况，以及每年的增长率',
    '今年预计多少合同额/收入，有哪些比较大的潜在订单（客户是谁、金额多少），截止到现在公司做了多少合同/收入，目前正在和哪些合作方在合作',
    '毛利率在多少，主要的成本项是哪些，公司每年的净利率（或者净利润）是多少',
    '公司现在的现金流和回款情况',

    # strategy
    '公司创立的时间，在发展过程中经历了什么重大事件，以及有哪些重大策略的变化',
    '未来几年公司发展的策略是什么',

    # team
    '主要的合伙人的介绍：包括学历背景、工作经历，以及是怎么认识的',
    '创始人为什么想去创业，以及为什么要选择这个方向',
    '各个合伙人之间的分工',

    # financing
    '公司目前的股权结构是怎样',
    '公司的融资计划（这轮想融多少，估值多少），之前的融资历史（每轮融了多少，谁投的，估值多少）',
    '上市计划，计划在哪里上市，现在做了哪些准备'
]




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


def dialogue_page(api: ApiRequest):
    chat_box.init_session()

    with st.sidebar:
        # TODO: 对话模型与会话绑定
        def on_mode_change():
            mode = st.session_state.dialogue_mode
            text = f"已切换到 {mode} 模式。"
            if mode == "知识库问答" or mode == "默认知识库总结" or mode == "GPT知识库总结":
                cur_kb = st.session_state.get("selected_kb")
                if cur_kb:
                    text = f"{text} 当前知识库： `{cur_kb}`。"
            st.toast(text)
            # sac.alert(text, description="descp", type="success", closable=True, banner=True)
        dialogue_mode = st.selectbox("请选择对话模式：",
                                     ["LLM 对话",
                                      "知识库问答",
                                      "搜索引擎问答",
                                      "自定义Agent问答",
                                      "默认知识库总结",
                                      "GPT知识库总结"
                                      ],
                                     index=1,
                                     on_change=on_mode_change,
                                     key="dialogue_mode",
                                     )

        def on_llm_change():
            config = get_model_worker_config(llm_model)
            if not config.get("online_api"):  # 只有本地model_worker可以切换模型
                st.session_state["prev_llm_model"] = llm_model
            st.session_state["cur_llm_model"] = st.session_state.llm_model

        def llm_model_format_func(x):
            if x in running_models:
                return f"{x} (Running)"
            return x

        running_models = api.list_running_models()
        available_models = []
        config_models = api.list_config_models()
        for models in config_models.values():
            for m in models:
                if m not in running_models:
                    available_models.append(m)
        llm_models = running_models + available_models
        index = llm_models.index(st.session_state.get("cur_llm_model", LLM_MODEL))
        llm_model = st.selectbox("选择LLM模型：",
                                 llm_models,
                                 index,
                                 format_func=llm_model_format_func,
                                 on_change=on_llm_change,
                                 key="llm_model",
                                 )
        if (st.session_state.get("prev_llm_model") != llm_model
                and not get_model_worker_config(llm_model).get("online_api")
                and llm_model not in running_models):
            with st.spinner(f"正在加载模型： {llm_model}，请勿进行操作或刷新页面"):
                prev_model = st.session_state.get("prev_llm_model")
                r = api.change_llm_model(prev_model, llm_model)
                if msg := check_error_msg(r):
                    st.error(msg)
                elif msg := check_success_msg(r):
                    st.success(msg)
                    st.session_state["prev_llm_model"] = llm_model

        temperature = st.slider("Temperature：", 0.0, 1.0, TEMPERATURE, 0.01)

        ## 部分模型可以超过10抡对话
        history_len = st.number_input("历史对话轮数：", 0, 20, HISTORY_LEN)

        def on_kb_change():
            st.toast(f"已加载知识库： {st.session_state.selected_kb}")

        if dialogue_mode == "知识库问答" or dialogue_mode == "默认知识库总结" or dialogue_mode == "GPT知识库总结":
            with st.expander("知识库配置", True):
                kb_list = api.list_knowledge_bases(no_remote_api=True)
                selected_kb = st.selectbox(
                    "请选择知识库：",
                    kb_list,
                    on_change=on_kb_change,
                    key="selected_kb",
                )
                kb_top_k = st.number_input("匹配知识条数：", 1, 20, VECTOR_SEARCH_TOP_K)

                ## Bge 模型会超过1
                score_threshold = st.slider("知识匹配分数阈值：", 0.0, 1.0, float(SCORE_THRESHOLD), 0.01)

                # chunk_content = st.checkbox("关联上下文", False, disabled=True)
                # chunk_size = st.slider("关联长度：", 0, 500, 250, disabled=True)
        elif dialogue_mode == "搜索引擎问答":
            search_engine_list = list(SEARCH_ENGINES.keys())
            with st.expander("搜索引擎配置", True):
                search_engine = st.selectbox(
                    label="请选择搜索引擎",
                    options=search_engine_list,
                    index=search_engine_list.index("duckduckgo") if "duckduckgo" in search_engine_list else 0,
                )
                se_top_k = st.number_input("匹配搜索结果条数：", 1, 20, SEARCH_ENGINE_TOP_K)

    # Display chat messages from history on app rerun

    chat_box.output_messages()

    chat_input_placeholder = "请输入对话内容，换行请使用Shift+Enter，总结板块发送“/summary”即可展开"

    if prompt := st.chat_input(chat_input_placeholder, key="prompt"):
        history = get_messages_history(history_len)
        chat_box.user_say(prompt)
        if dialogue_mode == "LLM 对话":
            chat_box.ai_say("正在思考...")
            text = ""
            r = api.chat_chat(prompt, history=history, model=llm_model, temperature=temperature)
            for t in r:
                if error_msg := check_error_msg(t):  # check whether error occured
                    st.error(error_msg)
                    break
                text += t
                chat_box.update_msg(text)
            chat_box.update_msg(text, streaming=False)  # 更新最终的字符串，去除光标


        elif dialogue_mode == "自定义Agent问答":
            chat_box.ai_say([
                f"正在思考和寻找工具 ...",])
            text = ""
            element_index = 0
            for d in api.agent_chat(prompt,
                                    history=history,
                                    model=llm_model,
                                    temperature=temperature):
                try:
                    d = json.loads(d)
                except:
                    pass
                if error_msg := check_error_msg(d):  # check whether error occured
                    st.error(error_msg)

                elif chunk := d.get("answer"):
                    text += chunk
                    chat_box.update_msg(text, element_index=0)
                elif chunk := d.get("tools"):
                    element_index += 1
                    chat_box.insert_msg(Markdown("...", in_expander=True, title="使用工具...", state="complete"))
                    chat_box.update_msg("\n\n".join(d.get("tools", [])), element_index=element_index, streaming=False)
            chat_box.update_msg(text, element_index=0, streaming=False)
        elif dialogue_mode == "知识库问答":
            chat_box.ai_say([
                f"正在查询知识库 `{selected_kb}` ...",
                Markdown("...", in_expander=True, title="知识库匹配结果", state="complete"),
            ])
            text = ""
            for d in api.knowledge_base_chat(prompt,
                                             knowledge_base_name=selected_kb,
                                             top_k=kb_top_k,
                                             score_threshold=score_threshold,
                                             history=history,
                                             model=llm_model,
                                             temperature=temperature):
                if error_msg := check_error_msg(d):  # check whether error occured
                    st.error(error_msg)
                elif chunk := d.get("answer"):
                    text += chunk
                    chat_box.update_msg(text, element_index=0)
            chat_box.update_msg(text, element_index=0, streaming=False)
            chat_box.update_msg("\n\n".join(d.get("docs", [])), element_index=1, streaming=False)
        elif dialogue_mode == "搜索引擎问答":
            chat_box.ai_say([
                f"正在执行 `{search_engine}` 搜索...",
                Markdown("...", in_expander=True, title="网络搜索结果", state="complete"),
            ])
            text = ""
            for d in api.search_engine_chat(prompt,
                                            search_engine_name=search_engine,
                                            top_k=se_top_k,
                                            history=history,
                                            model=llm_model,
                                            temperature=temperature):
                if error_msg := check_error_msg(d):  # check whether error occured
                    st.error(error_msg)
                elif chunk := d.get("answer"):
                    text += chunk
                    chat_box.update_msg(text, element_index=0)
            chat_box.update_msg(text, element_index=0, streaming=False)
            chat_box.update_msg("\n\n".join(d.get("docs", [])), element_index=1, streaming=False)
        elif dialogue_mode == "默认知识库总结":
            if prompt != '/summary':
                chat_box.ai_say([
                    f"正在查询知识库 `{selected_kb}` ...",
                    Markdown("...", in_expander=True, title="知识库匹配结果", state="complete"),
                ])
                text = ""
                for d in api.knowledge_base_chat(prompt,
                                                knowledge_base_name=selected_kb,
                                                top_k=kb_top_k,
                                                score_threshold=score_threshold,
                                                history=history,
                                                model=llm_model,
                                                temperature=temperature):
                    if error_msg := check_error_msg(d):  # check whether error occured
                        st.error(error_msg)
                    elif chunk := d.get("answer"):
                        text += chunk
                        chat_box.update_msg(text, element_index=0)
                chat_box.update_msg(text, element_index=0, streaming=False)
                chat_box.update_msg("\n\n".join(d.get("docs", [])), element_index=1, streaming=False)
            else:
                chat_box.ai_say([
                    f"正在查询知识库 `{selected_kb}` ...",
                    Markdown("...", in_expander=True, title="知识库匹配结果", state="complete"),
                ])
                text = ""
                answers = []
                for question in questions:
                    answer_text = ""
                    for d in api.knowledge_base_chat(question,
                                                    knowledge_base_name=selected_kb,
                                                    top_k=kb_top_k,
                                                    score_threshold=score_threshold,
                                                    history=history,
                                                    model=llm_model,
                                                    temperature=temperature):
                        if error_msg := check_error_msg(d):  # check whether error occured
                            st.error(error_msg)
                        elif chunk := d.get("answer"):
                            answer_text += chunk
                            # 如果chunk包含子串“无法回答该问题”则跳过
                    answers.append({"question": question, "answer": answer_text})
                output = ""
                for d in answers:
                    question = d["question"]
                    text = d["answer"]
                    output += "Question: "+question+"\n\nAnswer: "+text+"\n\n"
                chat_box.update_msg(output, element_index=0, streaming=False)
                chat_box.update_msg("", streaming=False)  # 更新最终的字符串，去除光标
        elif dialogue_mode == "GPT知识库总结":
            if prompt != '/summary':
                chat_box.ai_say([
                    f"正在查询知识库 `{selected_kb}` ...",
                    Markdown("...", in_expander=True, title="知识库匹配结果", state="complete"),
                ])
                text = ""
                for d in api.knowledge_base_chat(prompt,
                                                knowledge_base_name=selected_kb,
                                                top_k=kb_top_k,
                                                score_threshold=score_threshold,
                                                history=history,
                                                model=llm_model,
                                                temperature=temperature):
                    if error_msg := check_error_msg(d):  # check whether error occured
                        st.error(error_msg)
                    elif chunk := d.get("answer"):
                        text += chunk
                        chat_box.update_msg(text, element_index=0)
                chat_box.update_msg(text, element_index=0, streaming=False)
                chat_box.update_msg("\n\n".join(d.get("docs", [])), element_index=1, streaming=False)
            else:
                chat_box.ai_say([
                    f"正在查询知识库 `{selected_kb}` ...",
                    Markdown("...", in_expander=True, title="知识库匹配结果", state="complete"),
                ])
                text = ""
                answers = []
                for question in questions:
                    answer_text = ""
                    for d in api.knowledge_base_chat(question,
                                                    knowledge_base_name=selected_kb,
                                                    top_k=kb_top_k,
                                                    score_threshold=score_threshold,
                                                    history=history,
                                                    model=llm_model,
                                                    temperature=temperature):
                        if error_msg := check_error_msg(d):  # check whether error occured
                            st.error(error_msg)
                        elif chunk := d.get("answer"):
                            answer_text += chunk
                            # 如果chunk包含子串“无法回答该问题”则跳过
                    answers.append({"question": question, "answer": answer_text})
                output = ""
                for d in answers:
                    question = d["question"]
                    text = d["answer"]
                    output += "Question: "+question+"\n\nAnswer: "+text+"\n\n"
                chat_box.update_msg(output, element_index=0, streaming=False)
                chat_box.update_msg("", streaming=False)  # 更新最终的字符串，去除光标

    now = datetime.now()
    with st.sidebar:

        cols = st.columns(2)
        export_btn = cols[0]
        if cols[1].button(
                "清空对话",
                use_container_width=True,
        ):
            chat_box.reset_history()
            st.experimental_rerun()

    export_btn.download_button(
        "导出记录",
        "".join(chat_box.export2md()),
        file_name=f"{now:%Y-%m-%d %H.%M}_对话记录.md",
        mime="text/markdown",
        use_container_width=True,
    )
