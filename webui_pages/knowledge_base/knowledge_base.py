import streamlit as st
from webui_pages.utils import *
from st_aggrid import AgGrid, JsCode
from st_aggrid.grid_options_builder import GridOptionsBuilder
import pandas as pd
from server.knowledge_base.utils import get_file_path, LOADER_DICT
from server.knowledge_base.kb_service.base import get_kb_details, get_kb_file_details
from typing import Literal, Dict, Tuple
from configs import (kbs_config,
                    EMBEDDING_MODEL, DEFAULT_VS_TYPE,
                    CHUNK_SIZE, OVERLAP_SIZE, ZH_TITLE_ENHANCE, PROMPT_TEMPLATES)
from configs import LOG_PATH, IMPORT_FILE_PATH
from configs.kb_config import KB_ROOT_PATH
from configs.basic_config import logger
from server.utils import list_embed_models
import os
import time


# SENTENCE_SIZE = 100
import shutil
import tika
import tika.parser
tika.TikaServerClasspath = os.path.join(LOG_PATH, 'tika')
tika.TikaJarPath = os.path.join(LOG_PATH, 'tika')

cell_renderer = JsCode("""function(params) {if(params.value==true){return '✓'}else{return '×'}}""")


def config_aggrid(
        df: pd.DataFrame,
        columns: Dict[Tuple[str, str], Dict] = {},
        selection_mode: Literal["single", "multiple", "disabled"] = "single",
        use_checkbox: bool = False,
) -> GridOptionsBuilder:
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_column("No", width=40)
    for (col, header), kw in columns.items():
        gb.configure_column(col, header, wrapHeaderText=True, **kw)
    gb.configure_selection(
        selection_mode=selection_mode,
        use_checkbox=use_checkbox,
        # pre_selected_rows=st.session_state.get("selected_rows", [0]),
    )
    return gb


def file_exists(kb: str, selected_rows: List) -> Tuple[str, str]:
    '''
    check whether a doc file exists in local knowledge base folder.
    return the file's name and path if it exists.
    '''
    if selected_rows:
        file_name = selected_rows[0]["file_name"]
        file_path = get_file_path(kb, file_name)
        if os.path.isfile(file_path):
            return file_name, file_path
    return "", ""

def paragraph_page(api: ApiRequest):
    try:
        original_text = PROMPT_TEMPLATES["knowledge_base_chat"]["default"]
        # 提取 ``` 之间的内容
        start_marker = '"""'
        end_marker = '"""'
        start = original_text.find(start_marker) + len(start_marker)
        end = original_text.rfind(end_marker)
        editable_text = original_text[start:end].strip()

        st.write(f"编辑内容:")
        editable_text = st.text_area("编辑内容:", value=editable_text, height=300, max_chars=None, key=None,
                               help=None, on_change=None, args=None, kwargs=None, label_visibility="hidden")
        # 处理用户的编辑结果
        if st.button("更新"):
            # 将修改后的内容写回原格式
            updated_text = original_text[:start] + '\r\n' + editable_text + '\r\n' + original_text[end:]
            print(updated_text)
            st.toast(f"段落结构更新成功")
            PROMPT_TEMPLATES["knowledge_base_chat"]["default"] = updated_text
            with open(os.path.join(os.path.dirname(__file__), '..', '..', 'configs', "custom_prompt_templates.txt"), "w") as file:
                file.write(updated_text)
    except Exception as e:
        st.error(e)

def knowledge_base_page(api: ApiRequest):
    try:
        kb_list = {x["kb_name"]: x for x in get_kb_details()}
    except Exception as e:
        st.error("获取知识库信息错误，请检查是否已按照 `README.md` 中 `4 知识库初始化与迁移` 步骤完成初始化或迁移，或是否为数据库连接错误。")
        st.stop()
    kb_names = list(kb_list.keys())

    if "selected_kb_name" in st.session_state and st.session_state["selected_kb_name"] in kb_names:
        selected_kb_index = kb_names.index(st.session_state["selected_kb_name"])
    else:
        selected_kb_index = 0

    if "selected_kb_info" not in st.session_state:
        st.session_state["selected_kb_info"] = ""

    def format_selected_kb(kb_name: str) -> str:
        if kb := kb_list.get(kb_name):
            return f"{kb_name} ({kb['vs_type']} @ {kb['embed_model']})"
        else:
            return kb_name

    selected_kb = st.selectbox(
        "请选择或新建知识库：",
        kb_names + ["新建知识库"],
        format_func=format_selected_kb,
        index=selected_kb_index
    )

    if selected_kb == "新建知识库":
        with st.form("新建知识库"):

            kb_name = st.text_input(
                "新建知识库名称",
                placeholder="新知识库名称，不支持中文命名",
                key="kb_name",
            )
            kb_info = st.text_input(
                "知识库简介",
                placeholder="知识库简介，方便Agent查找",
                key="kb_info",
            )

            cols = st.columns(2)

            vs_types = list(kbs_config.keys())
            vs_type = cols[0].selectbox(
                "向量库类型",
                vs_types,
                index=vs_types.index(DEFAULT_VS_TYPE),
                key="vs_type",
            )

            embed_models = list_embed_models()

            embed_model = cols[1].selectbox(
                "Embedding 模型",
                embed_models,
                index=embed_models.index(EMBEDDING_MODEL),
                key="embed_model",
            )

            submit_create_kb = st.form_submit_button(
                "新建",
                # disabled=not bool(kb_name),
                use_container_width=True,
            )

        if submit_create_kb:
            if not kb_name or not kb_name.strip():
                st.error(f"知识库名称不能为空！")
            elif kb_name in kb_list:
                st.error(f"名为 {kb_name} 的知识库已经存在！")
            else:
                ret = api.create_knowledge_base(
                    knowledge_base_name=kb_name,
                    vector_store_type=vs_type,
                    embed_model=embed_model,
                )
                st.toast(ret.get("msg", " "))
                st.session_state["selected_kb_name"] = kb_name
                st.session_state["selected_kb_info"] = kb_info
                st.experimental_rerun()

    elif selected_kb:
        kb = selected_kb
        st.session_state["selected_kb_info"] = kb_list[kb]['kb_info']
        # 上传文件
        files = st.file_uploader("上传知识文件：",
                                 [i for ls in LOADER_DICT.values() for i in ls],
                                 accept_multiple_files=True,
                                 )
        kb_info = st.text_area("请输入知识库介绍:", value=st.session_state["selected_kb_info"], max_chars=None, key=None,
                               help=None, on_change=None, args=None, kwargs=None)

        if kb_info != st.session_state["selected_kb_info"]:
            st.session_state["selected_kb_info"] = kb_info
            api.update_kb_info(kb, kb_info)

        # with st.sidebar:
        with st.expander(
                "文件处理配置",
                expanded=True,
        ):
            cols = st.columns(3)
            chunk_size = cols[0].number_input("单段文本最大长度：", 1, 1000, CHUNK_SIZE)
            chunk_overlap = cols[1].number_input("相邻文本重合长度：", 0, chunk_size, OVERLAP_SIZE)
            cols[2].write("")
            cols[2].write("")
            zh_title_enhance = cols[2].checkbox("开启中文标题加强", ZH_TITLE_ENHANCE)

        if st.button(
                "添加文件到知识库",
                # use_container_width=True,
                disabled=len(files) == 0,
        ):
            ret = api.upload_kb_docs(files,
                                     knowledge_base_name=kb,
                                     override=True,
                                     chunk_size=chunk_size,
                                     chunk_overlap=chunk_overlap,
                                     zh_title_enhance=zh_title_enhance)
            if msg := check_success_msg(ret):
                st.toast(msg, icon="✔")
            elif msg := check_error_msg(ret):
                st.toast(msg, icon="✖")

        st.write(':red[注意，需先创建知识库后才能上传文件]')
        st.write(f"请手动上传文件，导入文件的路径为服务器上的:{IMPORT_FILE_PATH}对应的知识库目录下")
        
        # 初始化 session state
        if 'button_clicked' not in st.session_state:
            st.session_state['button_clicked'] = False

        # 定义按钮的行为
        def on_button_click():
            try:
                for root, dirs, files in os.walk(IMPORT_FILE_PATH):
                    for file in files:
                        if file.lower().endswith(('.doc', '.docx', '.wps', '.pdf')):
                            # 构建目标目录中的相对路径
                            relative_path = os.path.relpath(root, IMPORT_FILE_PATH)
                            # target_path = os.path.join(target_directory, relative_path)
                            target_path = os.path.join(KB_ROOT_PATH, kb, 'content')

                            # 如果目标目录不存在，则跳过，需要从界面上创建它
                            if not os.path.exists(target_path):
                                print(target_path)
                                logger.error(f'知识库 `{kb}` 不存在，请先创建')
                                continue

                            source_file_path = os.path.join(root, file)
                            target_file_path = os.path.join(target_path, file + '.txt')

                            try:
                                # 使用Tika解析文档并提取文本内容
                                parsed = tika.parser.from_file(source_file_path)
                                # print(parsed["metadata"])
                                text = parsed["content"]
                                if text is None:
                                    shutil.copy2(source_file_path, os.path.join(target_path, file))
                                    logger.info(f'Tika无法提取,源文件拷贝: {source_file_path}')
                                    continue
                                with open(target_file_path, 'w', encoding='utf-8') as txt_file:
                                    txt_file.write(text)
                                logger.info(f'提取并保存：{target_file_path}')
                            except Exception as e:
                                logger.info(f'处理文件时出错：{source_file_path}')
                                logger.error(str(e))
                # st.success("已成功导入文件到服务器知识库本地目录")
                # st.toast(f"已成功导入文件到服务器知识库本地目录")
                st.session_state['button_clicked'] = True
            except Exception as e:
                st.error(e)

        # 显示按钮并关联动作
        if st.button('批量导入文件到知识库', type="primary", on_click=on_button_click):
            pass  # 按钮点击逻辑已经在 on_click 函数中定义

        # 根据按钮点击状态显示消息
        if st.session_state['button_clicked']:
            st.success(f'已成功导入文件到服务器知识库 `{kb}` 的本地目录')
            # del st.session_state['button_clicked']
            
        st.divider()

        # 知识库详情
        # st.info("请选择文件，点击按钮进行操作。")
        doc_details = pd.DataFrame(get_kb_file_details(kb))
        if not len(doc_details):
            st.info(f"知识库 `{kb}` 中暂无文件")
        else:
            st.write(f"知识库 `{kb}` 中已有文件:")
            st.info("知识库中包含源文件与向量库，请从下表中选择文件后操作")
            doc_details.drop(columns=["kb_name"], inplace=True)
            doc_details = doc_details[[
                "No", "file_name", "document_loader", "text_splitter", "docs_count", "in_folder", "in_db",
            ]]
            # doc_details["in_folder"] = doc_details["in_folder"].replace(True, "✓").replace(False, "×")
            # doc_details["in_db"] = doc_details["in_db"].replace(True, "✓").replace(False, "×")
            gb = config_aggrid(
                doc_details,
                {
                    ("No", "序号"): {},
                    ("file_name", "文档名称"): {},
                    # ("file_ext", "文档类型"): {},
                    # ("file_version", "文档版本"): {},
                    ("document_loader", "文档加载器"): {},
                    ("docs_count", "文档数量"): {},
                    ("text_splitter", "分词器"): {},
                    # ("create_time", "创建时间"): {},
                    ("in_folder", "源文件"): {"cellRenderer": cell_renderer},
                    ("in_db", "向量库"): {"cellRenderer": cell_renderer},
                },
                "multiple",
            )

            doc_grid = AgGrid(
                doc_details,
                gb.build(),
                columns_auto_size_mode="FIT_CONTENTS",
                theme="alpine",
                custom_css={
                    "#gridToolBar": {"display": "none"},
                },
                allow_unsafe_jscode=True,
                enable_enterprise_modules=False
            )

            selected_rows = doc_grid.get("selected_rows", [])

            cols = st.columns(4)
            file_name, file_path = file_exists(kb, selected_rows)
            if file_path:
                with open(file_path, "rb") as fp:
                    cols[0].download_button(
                        "下载选中文档",
                        fp,
                        file_name=file_name,
                        use_container_width=True, )
            else:
                cols[0].download_button(
                    "下载选中文档",
                    "",
                    disabled=True,
                    use_container_width=True, )

            st.write()
            # 将文件分词并加载到向量库中
            if cols[1].button(
                    "重新添加至向量库" if selected_rows and (pd.DataFrame(selected_rows)["in_db"]).any() else "添加至向量库",
                    disabled=not file_exists(kb, selected_rows)[0],
                    use_container_width=True,
            ):
                file_names = [row["file_name"] for row in selected_rows]
                api.update_kb_docs(kb,
                                   file_names=file_names,
                                   chunk_size=chunk_size,
                                   chunk_overlap=chunk_overlap,
                                   zh_title_enhance=zh_title_enhance)
                st.experimental_rerun()

            # 将文件从向量库中删除，但不删除文件本身。
            if cols[2].button(
                    "从向量库删除",
                    disabled=not (selected_rows and selected_rows[0]["in_db"]),
                    use_container_width=True,
            ):
                file_names = [row["file_name"] for row in selected_rows]
                api.delete_kb_docs(kb, file_names=file_names)
                st.experimental_rerun()

            if cols[3].button(
                    "从知识库中删除",
                    type="primary",
                    use_container_width=True,
            ):
                file_names = [row["file_name"] for row in selected_rows]
                api.delete_kb_docs(kb, file_names=file_names, delete_content=True)
                st.experimental_rerun()

        st.divider()

        cols = st.columns(3)

        if cols[0].button(
                "增量入库",
                # help="无需上传文件，通过其它方式将文档拷贝到对应知识库content目录下，点击本按钮即可重建知识库。",
                use_container_width=True,
                type="primary",
        ):
            with st.spinner("增量导入中，请耐心等待。"):
                # 使用os.system来调用外部Python脚本
                print(f"增量知识库 `{kb}` 中的文件")
                expy = os.path.abspath(os.path.join(os.path.abspath(__file__), '..', '..', '..')) + os.sep + 'init_database.py'
                cmd = 'python ' + expy + ' -i --import-file --kb-name ' + kb
                print(cmd)
                os.system(cmd)

                exlog = LOG_PATH + os.sep + 'doc2txt.log'
                print(exlog)

                text_area = st.empty()

                # 读取日志文件的内容并显示在st.text_area中
                with open(exlog, 'r') as file:
                    initial_output = file.read()
                    text_area.text_area("**日志输出:**", initial_output, height=500)

                # 自动间隔读取输出并更新st.text_area
                while True:
                    with open(exlog, 'r') as file:
                        updated_output = file.read()
                    
                    if updated_output != initial_output:
                        text_area.text_area("**日志输出:**", updated_output, height=500)
                        initial_output = updated_output

                    time.sleep(1)  # 1秒钟更新一次

                # empty = st.empty()
                # empty.progress(0.0, "")
                # for d in api.recreate_vector_store(kb,
                #                                 chunk_size=chunk_size,
                #                                 chunk_overlap=chunk_overlap,
                #                                 zh_title_enhance=zh_title_enhance):
                #     if msg := check_error_msg(d):
                #         st.toast(msg)
                #     else:
                #         empty.progress(d["finished"] / d["total"], d["msg"])
                # st.experimental_rerun()

        if cols[2].button(
                "删除知识库",
                use_container_width=True,
        ):
            ret = api.delete_knowledge_base(kb)
            st.toast(ret.get("msg", " "))
            time.sleep(1)
            st.experimental_rerun()
