import streamlit as st
# from st_btn_select import st_btn_select
import tempfile
###### 从webui借用的代码 #####
######   做了少量修改    #####
import os
import shutil

from chains.local_doc_qa import LocalDocQA
from configs.model_config import *
import nltk
from models.base import (BaseAnswer,
                         AnswerResult,)
import models.shared as shared
from models.loader.args import parser
from models.loader import LoaderCheckPoint

nltk.data.path = [NLTK_DATA_PATH] + nltk.data.path


def get_vs_list():
    lst_default = ["新建知识库"]
    if not os.path.exists(KB_ROOT_PATH):
        return lst_default
    lst = os.listdir(KB_ROOT_PATH)
    if not lst:
        return lst_default
    lst.sort()
    return lst_default + lst


embedding_model_dict_list = list(embedding_model_dict.keys())
llm_model_dict_list = list(llm_model_dict.keys())
# flag_csv_logger = gr.CSVLogger()


def get_answer(query, vs_path, history, mode, score_threshold=VECTOR_SEARCH_SCORE_THRESHOLD,
               vector_search_top_k=VECTOR_SEARCH_TOP_K, chunk_conent: bool = True,
               chunk_size=CHUNK_SIZE, streaming: bool = STREAMING,):
    if mode == "Bing搜索问答":
        for resp, history in local_doc_qa.get_search_result_based_answer(
                query=query, chat_history=history, streaming=streaming):
            source = "\n\n"
            source += "".join(
                [f"""<details> <summary>出处 [{i + 1}] <a href="{doc.metadata["source"]}" target="_blank">{doc.metadata["source"]}</a> </summary>\n"""
                 f"""{doc.page_content}\n"""
                 f"""</details>"""
                 for i, doc in
                 enumerate(resp["source_documents"])])
            history[-1][-1] += source
            yield history, ""
    elif mode == "知识库问答" and vs_path is not None and os.path.exists(vs_path):
        for resp, history in local_doc_qa.get_knowledge_based_answer(
                query=query, vs_path=vs_path, chat_history=history, streaming=streaming):
            source = "\n\n"
            source += "".join(
                [f"""<details> <summary>出处 [{i + 1}] {os.path.split(doc.metadata["source"])[-1]}</summary>\n"""
                 f"""{doc.page_content}\n"""
                 f"""</details>"""
                 for i, doc in
                 enumerate(resp["source_documents"])])
            history[-1][-1] += source
            yield history, ""
    elif mode == "知识库测试":
        if os.path.exists(vs_path):
            resp, prompt = local_doc_qa.get_knowledge_based_conent_test(query=query, vs_path=vs_path,
                                                                        score_threshold=score_threshold,
                                                                        vector_search_top_k=vector_search_top_k,
                                                                        chunk_conent=chunk_conent,
                                                                        chunk_size=chunk_size)
            if not resp["source_documents"]:
                yield history + [[query,
                                  "根据您的设定，没有匹配到任何内容，请确认您设置的知识相关度 Score 阈值是否过小或其他参数是否正确。"]], ""
            else:
                source = "\n".join(
                    [
                        f"""<details open> <summary>【知识相关度 Score】：{doc.metadata["score"]} - 【出处{i + 1}】：  {os.path.split(doc.metadata["source"])[-1]} </summary>\n"""
                        f"""{doc.page_content}\n"""
                        f"""</details>"""
                        for i, doc in
                        enumerate(resp["source_documents"])])
                history.append([query, "以下内容为知识库中满足设置条件的匹配结果：\n\n" + source])
                yield history, ""
        else:
            yield history + [[query,
                              "请选择知识库后进行测试，当前未选择知识库。"]], ""
    else:
        for answer_result in local_doc_qa.llm.generatorAnswer(prompt=query, history=history,
                                                              streaming=streaming):

            resp = answer_result.llm_output["answer"]
            history = answer_result.history
            history[-1][-1] = resp + (
                "\n\n当前知识库为空，如需基于知识库进行问答，请先加载知识库后，再进行提问。" if mode == "知识库问答" else "")
            yield history, ""
    logger.info(f"flagging: username={FLAG_USER_NAME},query={query},vs_path={vs_path},mode={mode},history={history}")
    # flag_csv_logger.flag([query, vs_path, history, mode], username=FLAG_USER_NAME)


def init_model(llm_model: str = 'chat-glm-6b', embedding_model: str = 'text2vec'):
    local_doc_qa = LocalDocQA()
    # 初始化消息
    args = parser.parse_args()
    args_dict = vars(args)
    args_dict.update(model=llm_model)
    shared.loaderCheckPoint = LoaderCheckPoint(args_dict)
    llm_model_ins = shared.loaderLLM()
    llm_model_ins.set_history_len(LLM_HISTORY_LEN)

    try:
        local_doc_qa.init_cfg(llm_model=llm_model_ins,
                              embedding_model=embedding_model)
        generator = local_doc_qa.llm.generatorAnswer("你好")
        for answer_result in generator:
            print(answer_result.llm_output)
        reply = """模型已成功加载，可以开始对话，或从右侧选择模式后开始对话"""
        logger.info(reply)
    except Exception as e:
        logger.error(e)
        reply = """模型未成功加载，请到页面左上角"模型配置"选项卡中重新选择后点击"加载模型"按钮"""
        if str(e) == "Unknown platform: darwin":
            logger.info("该报错可能因为您使用的是 macOS 操作系统，需先下载模型至本地后执行 Web UI，具体方法请参考项目 README 中本地部署方法及常见问题："
                        " https://github.com/imClumsyPanda/langchain-ChatGLM")
        else:
            logger.info(reply)
    return local_doc_qa


# 暂未使用到，先保留
# def reinit_model(llm_model, embedding_model, llm_history_len, no_remote_model, use_ptuning_v2, use_lora, top_k, history):
#     try:
#         llm_model_ins = shared.loaderLLM(llm_model, no_remote_model, use_ptuning_v2)
#         llm_model_ins.history_len = llm_history_len
#         local_doc_qa.init_cfg(llm_model=llm_model_ins,
#                               embedding_model=embedding_model,
#                               top_k=top_k)
#         model_status = """模型已成功重新加载，可以开始对话，或从右侧选择模式后开始对话"""
#         logger.info(model_status)
#     except Exception as e:
#         logger.error(e)
#         model_status = """模型未成功重新加载，请到页面左上角"模型配置"选项卡中重新选择后点击"加载模型"按钮"""
#         logger.info(model_status)
#     return history + [[None, model_status]]


def get_vector_store(vs_id, files, sentence_size, history, one_conent, one_content_segmentation):
    vs_path = os.path.join(KB_ROOT_PATH, vs_id, "vector_store")
    filelist = []
    if not os.path.exists(os.path.join(KB_ROOT_PATH, vs_id, "content")):
        os.makedirs(os.path.join(KB_ROOT_PATH, vs_id, "content"))
    if local_doc_qa.llm and local_doc_qa.embeddings:
        if isinstance(files, list):
            for file in files:
                filename = os.path.split(file.name)[-1]
                shutil.move(file.name, os.path.join(
                    KB_ROOT_PATH, vs_id, "content", filename))
                filelist.append(os.path.join(
                    KB_ROOT_PATH, vs_id, "content", filename))
            vs_path, loaded_files = local_doc_qa.init_knowledge_vector_store(
                filelist, vs_path, sentence_size)
        else:
            vs_path, loaded_files = local_doc_qa.one_knowledge_add(vs_path, files, one_conent, one_content_segmentation,
                                                                   sentence_size)
        if len(loaded_files):
            file_status = f"已添加 {'、'.join([os.path.split(i)[-1] for i in loaded_files if i])} 内容至知识库，并已加载知识库，请开始提问"
        else:
            file_status = "文件未成功加载，请重新上传文件"
    else:
        file_status = "模型未完成加载，请先在加载模型后再导入文件"
        vs_path = None
    logger.info(file_status)
    return vs_path, None, history + [[None, file_status]]


knowledge_base_test_mode_info = ("【注意】\n\n"
                                 "1. 您已进入知识库测试模式，您输入的任何对话内容都将用于进行知识库查询，"
                                 "并仅输出知识库匹配出的内容及相似度分值和及输入的文本源路径，查询的内容并不会进入模型查询。\n\n"
                                 "2. 知识相关度 Score 经测试，建议设置为 500 或更低，具体设置情况请结合实际使用调整。"
                                 """3. 使用"添加单条数据"添加文本至知识库时，内容如未分段，则内容越多越会稀释各查询内容与之关联的score阈值。\n\n"""
                                 "4. 单条内容长度建议设置在100-150左右。\n\n"
                                 "5. 本界面用于知识入库及知识匹配相关参数设定，但当前版本中，"
                                 "本界面中修改的参数并不会直接修改对话界面中参数，仍需前往`configs/model_config.py`修改后生效。"
                                 "相关参数将在后续版本中支持本界面直接修改。")


webui_title = """
# 🎉langchain-ChatGLM WebUI🎉
👍 [https://github.com/imClumsyPanda/langchain-ChatGLM](https://github.com/imClumsyPanda/langchain-ChatGLM)
"""
######                   #####


###### todo #####
# 1. streamlit运行方式与一般web服务器不同，使用模块是无法实现单例模式的，所以shared和local_doc_qa都需要进行全局化处理。
#   目前已经实现了local_doc_qa的全局化，后面要考虑shared。
# 2. 当前local_doc_qa是一个全局变量，一方面：任何一个session对其做出修改，都会影响所有session的对话;另一方面，如何处理所有session的请求竞争也是问题。
#   这个暂时无法避免，在配置普通的机器上暂时也无需考虑。
# 3. 目前只包含了get_answer对应的参数，以后可以添加其他参数，如temperature。
######      #####


###### 配置项 #####
class ST_CONFIG:
    user_bg_color = '#77ff77'
    user_icon = 'https://tse2-mm.cn.bing.net/th/id/OIP-C.LTTKrxNWDr_k74wz6jKqBgHaHa?w=203&h=203&c=7&r=0&o=5&pid=1.7'
    robot_bg_color = '#ccccee'
    robot_icon = 'https://ts1.cn.mm.bing.net/th/id/R-C.5302e2cc6f5c7c4933ebb3394e0c41bc?rik=z4u%2b7efba5Mgxw&riu=http%3a%2f%2fcomic-cons.xyz%2fwp-content%2fuploads%2fStar-Wars-avatar-icon-C3PO.png&ehk=kBBvCvpJMHPVpdfpw1GaH%2brbOaIoHjY5Ua9PKcIs%2bAc%3d&risl=&pid=ImgRaw&r=0'
    default_mode = '知识库问答'
    defalut_kb = ''
######        #####


class MsgType:
    '''
    目前仅支持文本类型的输入输出，为以后多模态模型预留图像、视频、音频支持。
    '''
    TEXT = 1
    IMAGE = 2
    VIDEO = 3
    AUDIO = 4


class TempFile:
    '''
    为保持与get_vector_store的兼容性，需要将streamlit上传文件转化为其可以接受的方式
    '''

    def __init__(self, path):
        self.name = path


def init_session():
    st.session_state.setdefault('history', [])


# def get_query_params():
#     '''
#     可以用url参数传递配置参数：llm_model, embedding_model, kb, mode。
#     该参数将覆盖model_config中的配置。处于安全考虑，目前只支持kb和mode
#     方便将固定的配置分享给特定的人。
#     '''
#     params = st.experimental_get_query_params()
#     return {k: v[0] for k, v in params.items() if v}


def robot_say(msg, kb=''):
    st.session_state['history'].append(
        {'is_user': False, 'type': MsgType.TEXT, 'content': msg, 'kb': kb})


def user_say(msg):
    st.session_state['history'].append(
        {'is_user': True, 'type': MsgType.TEXT, 'content': msg})


def format_md(msg, is_user=False, bg_color='', margin='10%'):
    '''
    将文本消息格式化为markdown文本
    '''
    if is_user:
        bg_color = bg_color or ST_CONFIG.user_bg_color
        text = f'''
                <div style="background:{bg_color};
                        margin-left:{margin};
                        word-break:break-all;
                        float:right;
                        padding:2%;
                        border-radius:2%;">
                {msg}
                </div>
                '''
    else:
        bg_color = bg_color or ST_CONFIG.robot_bg_color
        text = f'''
                <div style="background:{bg_color};
                        margin-right:{margin};
                        word-break:break-all;
                        padding:2%;
                        border-radius:2%;">
                {msg}
                </div>
                '''
    return text


def message(msg,
            is_user=False,
            msg_type=MsgType.TEXT,
            icon='',
            bg_color='',
            margin='10%',
            kb='',
            ):
    '''
    渲染单条消息。目前仅支持文本
    '''
    cols = st.columns([1, 10, 1])
    empty = cols[1].empty()
    if is_user:
        icon = icon or ST_CONFIG.user_icon
        bg_color = bg_color or ST_CONFIG.user_bg_color
        cols[2].image(icon, width=40)
        if msg_type == MsgType.TEXT:
            text = format_md(msg, is_user, bg_color, margin)
            empty.markdown(text, unsafe_allow_html=True)
        else:
            raise RuntimeError('only support text message now.')
    else:
        icon = icon or ST_CONFIG.robot_icon
        bg_color = bg_color or ST_CONFIG.robot_bg_color
        cols[0].image(icon, width=40)
        if kb:
            cols[0].write(f'({kb})')
        if msg_type == MsgType.TEXT:
            text = format_md(msg, is_user, bg_color, margin)
            empty.markdown(text, unsafe_allow_html=True)
        else:
            raise RuntimeError('only support text message now.')
    return empty


def output_messages(
    user_bg_color='',
    robot_bg_color='',
    user_icon='',
    robot_icon='',
):
    with chat_box.container():
        last_response = None
        for msg in st.session_state['history']:
            bg_color = user_bg_color if msg['is_user'] else robot_bg_color
            icon = user_icon if msg['is_user'] else robot_icon
            empty = message(msg['content'],
                            is_user=msg['is_user'],
                            icon=icon,
                            msg_type=msg['type'],
                            bg_color=bg_color,
                            kb=msg.get('kb', '')
                            )
            if not msg['is_user']:
                last_response = empty
    return last_response


@st.cache_resource(show_spinner=False, max_entries=1)
def load_model(llm_model: str, embedding_model: str):
    '''
    对应init_model，利用streamlit cache避免模型重复加载
    '''
    local_doc_qa = init_model(llm_model, embedding_model)
    robot_say('模型已成功加载，可以开始对话，或从左侧选择模式后开始对话。\n请尽量不要刷新页面，以免模型出错或重复加载。')
    return local_doc_qa


# @st.cache_data
def answer(query, vs_path='', history=[], mode='', score_threshold=0,
           vector_search_top_k=5, chunk_conent=True, chunk_size=100, qa=None
           ):
    '''
    对应get_answer，--利用streamlit cache缓存相同问题的答案--
    '''
    return get_answer(query, vs_path, history, mode, score_threshold,
                      vector_search_top_k, chunk_conent, chunk_size)


def load_vector_store(
    vs_id,
    files,
    sentence_size=100,
    history=[],
    one_conent=None,
    one_content_segmentation=None,
):
    return get_vector_store(
        local_doc_qa,
        vs_id,
        files,
        sentence_size,
        history,
        one_conent,
        one_content_segmentation,
    )


# main ui
st.set_page_config(webui_title, layout='wide')
init_session()
# params = get_query_params()
# llm_model = params.get('llm_model', LLM_MODEL)
# embedding_model = params.get('embedding_model', EMBEDDING_MODEL)

with st.spinner(f'正在加载模型({LLM_MODEL} + {EMBEDDING_MODEL})，请耐心等候...'):
    local_doc_qa = load_model(LLM_MODEL, EMBEDDING_MODEL)


def use_kb_mode(m):
    return m in ['知识库问答', '知识库测试']


# sidebar
modes = ['LLM 对话', '知识库问答', 'Bing搜索问答', '知识库测试']
with st.sidebar:
    def on_mode_change():
        m = st.session_state.mode
        robot_say(f'已切换到"{m}"模式')
        if m == '知识库测试':
            robot_say(knowledge_base_test_mode_info)

    index = 0
    try:
        index = modes.index(ST_CONFIG.default_mode)
    except:
        pass
    mode = st.selectbox('对话模式', modes, index,
                        on_change=on_mode_change, key='mode')

    with st.expander('模型配置', '知识' not in mode):
        with st.form('model_config'):
            index = 0
            try:
                index = llm_model_dict_list.index(LLM_MODEL)
            except:
                pass
            llm_model = st.selectbox('LLM模型', llm_model_dict_list, index)

            no_remote_model = st.checkbox('加载本地模型', False)
            use_ptuning_v2 = st.checkbox('使用p-tuning-v2微调过的模型', False)
            use_lora = st.checkbox('使用lora微调的权重', False)
            try:
                index = embedding_model_dict_list.index(EMBEDDING_MODEL)
            except:
                pass
            embedding_model = st.selectbox(
                'Embedding模型', embedding_model_dict_list, index)

            btn_load_model = st.form_submit_button('重新加载模型')
            if btn_load_model:
                local_doc_qa = load_model(llm_model, embedding_model)

    if mode in ['知识库问答', '知识库测试']:
        vs_list = get_vs_list()
        vs_list.remove('新建知识库')

        def on_new_kb():
            name = st.session_state.kb_name
            if name in vs_list:
                st.error(f'名为“{name}”的知识库已存在。')
            else:
                vs_list.append(name)
                st.session_state.vs_path = name

        def on_vs_change():
            robot_say(f'已加载知识库： {st.session_state.vs_path}')
        with st.expander('知识库配置', True):
            cols = st.columns([12, 10])
            kb_name = cols[0].text_input(
                '新知识库名称', placeholder='新知识库名称', label_visibility='collapsed')
            cols[1].button('新建知识库', on_click=on_new_kb)
            vs_path = st.selectbox(
                '选择知识库', vs_list, on_change=on_vs_change, key='vs_path')

            st.text('')

            score_threshold = st.slider(
                '知识相关度阈值', 0, 1000, VECTOR_SEARCH_SCORE_THRESHOLD)
            top_k = st.slider('向量匹配数量', 1, 20, VECTOR_SEARCH_TOP_K)
            history_len = st.slider(
                'LLM对话轮数', 1, 50, LLM_HISTORY_LEN)  # 也许要跟知识库分开设置
            local_doc_qa.llm.set_history_len(history_len)
            chunk_conent = st.checkbox('启用上下文关联', False)
            st.text('')
            # chunk_conent = st.checkbox('分割文本', True) # 知识库文本分割入库
            chunk_size = st.slider('上下文关联长度', 1, 1000, CHUNK_SIZE)
            sentence_size = st.slider('文本入库分句长度限制', 1, 1000, SENTENCE_SIZE)
            files = st.file_uploader('上传知识文件',
                                     ['docx', 'txt', 'md', 'csv', 'xlsx', 'pdf'],
                                     accept_multiple_files=True)
            if st.button('添加文件到知识库'):
                temp_dir = tempfile.mkdtemp()
                file_list = []
                for f in files:
                    file = os.path.join(temp_dir, f.name)
                    with open(file, 'wb') as fp:
                        fp.write(f.getvalue())
                    file_list.append(TempFile(file))
                _, _, history = load_vector_store(
                    vs_path, file_list, sentence_size, [], None, None)
                st.session_state.files = []


# main body
chat_box = st.empty()

with st.form('my_form', clear_on_submit=True):
    cols = st.columns([8, 1])
    question = cols[0].text_input(
        'temp', key='input_question', label_visibility='collapsed')

    def on_send():
        q = st.session_state.input_question
        if q:
            user_say(q)

            if mode == 'LLM 对话':
                robot_say('正在思考...')
                last_response = output_messages()
                for history, _ in answer(q,
                                         history=[],
                                         mode=mode):
                    last_response.markdown(
                        format_md(history[-1][-1], False),
                        unsafe_allow_html=True
                    )
            elif use_kb_mode(mode):
                robot_say('正在思考...', vs_path)
                last_response = output_messages()
                for history, _ in answer(q,
                                         vs_path=os.path.join(
                                             KB_ROOT_PATH, vs_path, "vector_store"),
                                         history=[],
                                         mode=mode,
                                         score_threshold=score_threshold,
                                         vector_search_top_k=top_k,
                                         chunk_conent=chunk_conent,
                                         chunk_size=chunk_size):
                    last_response.markdown(
                        format_md(history[-1][-1], False, 'ligreen'),
                        unsafe_allow_html=True
                    )
            else:
                robot_say('正在思考...')
                last_response = output_messages()
            st.session_state['history'][-1]['content'] = history[-1][-1]
    submit = cols[1].form_submit_button('发送', on_click=on_send)

output_messages()

# st.write(st.session_state['history'])
