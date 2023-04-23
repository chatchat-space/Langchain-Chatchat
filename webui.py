import gradio as gr
import os
import shutil
from chains.local_doc_qa import LocalDocQA
from configs.model_config import *
import nltk

nltk.data.path = [os.path.join(os.path.dirname(__file__), "nltk_data")] + nltk.data.path

# return top-k text chunk from vector store
VECTOR_SEARCH_TOP_K = 6

# LLM input history length
LLM_HISTORY_LEN = 3


def get_vs_list():
    if not os.path.exists(VS_ROOT_PATH):
        return []
    return os.listdir(VS_ROOT_PATH)


vs_list = ["新建知识库"] + get_vs_list()

embedding_model_dict_list = list(embedding_model_dict.keys())

llm_model_dict_list = list(llm_model_dict.keys())

local_doc_qa = LocalDocQA()


def get_answer(query, vs_path, history, mode):
    if vs_path and mode == "知识库问答":
        resp, history = local_doc_qa.get_knowledge_based_answer(
            query=query, vs_path=vs_path, chat_history=history)
        source = "".join([f"""<details> <summary>出处 {i + 1}</summary>
{doc.page_content}

<b>所属文件：</b>{doc.metadata["source"]}
</details>""" for i, doc in enumerate(resp["source_documents"])])
        history[-1][-1] += source
    else:
        resp = local_doc_qa.llm._call(query)
        history = history + [[query, resp + ("\n\n当前知识库为空，如需基于知识库进行问答，请先加载知识库后，再进行提问。" if mode == "知识库问答" else "")]]
    return history, ""


def update_status(history, status):
    history = history + [[None, status]]
    print(status)
    return history


def init_model():
    try:
        local_doc_qa.init_cfg()
        local_doc_qa.llm._call("你好")
        return """模型已成功加载，可以开始对话，或从右侧选择模式后开始对话"""
    except Exception as e:
        print(e)
        return """模型未成功加载，请到页面左上角"模型配置"选项卡中重新选择后点击"加载模型"按钮"""


def reinit_model(llm_model, embedding_model, llm_history_len, use_ptuning_v2, top_k, history):
    try:
        local_doc_qa.init_cfg(llm_model=llm_model,
                              embedding_model=embedding_model,
                              llm_history_len=llm_history_len,
                              use_ptuning_v2=use_ptuning_v2,
                              top_k=top_k)
        model_status = """模型已成功重新加载，可以开始对话，或从右侧选择模式后开始对话"""
    except Exception as e:
        print(e)
        model_status = """模型未成功重新加载，请到页面左上角"模型配置"选项卡中重新选择后点击"加载模型"按钮"""
    return history + [[None, model_status]]


def get_vector_store(vs_id, files, history):
    vs_path = VS_ROOT_PATH + vs_id
    filelist = []
    for file in files:
        filename = os.path.split(file.name)[-1]
        shutil.move(file.name, UPLOAD_ROOT_PATH + filename)
        filelist.append(UPLOAD_ROOT_PATH + filename)
    if local_doc_qa.llm and local_doc_qa.embeddings:
        vs_path, loaded_files = local_doc_qa.init_knowledge_vector_store(filelist, vs_path)
        if len(loaded_files):
            file_status = f"已上传 {'、'.join([os.path.split(i)[-1] for i in loaded_files])} 至知识库，并已加载知识库，请开始提问"
        else:
            file_status = "文件未成功加载，请重新上传文件"
    else:
        file_status = "模型未完成加载，请先在加载模型后再导入文件"
        vs_path = None
    return vs_path, None, history + [[None, file_status]]


def change_vs_name_input(vs_id):
    if vs_id == "新建知识库":
        return gr.update(visible=True), gr.update(visible=True), gr.update(visible=False), None
    else:
        return gr.update(visible=False), gr.update(visible=False), gr.update(visible=True), VS_ROOT_PATH + vs_id


def change_mode(mode):
    if mode == "知识库问答":
        return gr.update(visible=True)
    else:
        return gr.update(visible=False)


def add_vs_name(vs_name, vs_list, chatbot):
    if vs_name in vs_list:
        chatbot = chatbot + [[None, "与已有知识库名称冲突，请重新选择其他名称后提交"]]
        return gr.update(visible=True), vs_list, chatbot
    else:
        chatbot = chatbot + [
            [None, f"""已新增知识库"{vs_name}",将在上传文件并载入成功后进行存储。请在开始对话前，先完成文件上传。 """]]
        return gr.update(visible=True, choices=vs_list + [vs_name], value=vs_name), vs_list + [vs_name], chatbot


block_css = """.importantButton {
    background: linear-gradient(45deg, #7e0570,#5d1c99, #6e00ff) !important;
    border: none !important;
}

.importantButton:hover {
    background: linear-gradient(45deg, #ff00e0,#8500ff, #6e00ff) !important;
    border: none !important;
}"""

webui_title = """
# 🎉langchain-ChatGLM WebUI🎉

👍 [https://github.com/imClumsyPanda/langchain-ChatGLM](https://github.com/imClumsyPanda/langchain-ChatGLM)

"""

init_message = """欢迎使用 langchain-ChatGLM Web UI！

请在右侧切换模式，目前支持直接与 LLM 模型对话或基于本地知识库问答。

知识库问答模式中，选择知识库名称后，即可开始问答，如有需要可以在选择知识库名称后上传文件/文件夹至知识库。

知识库暂不支持文件删除，该功能将在后续版本中推出。
"""

model_status = init_model()

with gr.Blocks(css=block_css) as demo:
    vs_path, file_status, model_status, vs_list = gr.State(""), gr.State(""), gr.State(model_status), gr.State(vs_list)
    gr.Markdown(webui_title)
    with gr.Tab("对话"):
        with gr.Row():
            with gr.Column(scale=10):
                chatbot = gr.Chatbot([[None, init_message], [None, model_status.value]],
                                     elem_id="chat-box",
                                     show_label=False).style(height=750)
                query = gr.Textbox(show_label=False,
                                   placeholder="请输入提问内容，按回车进行提交",
                                   ).style(container=False)
            with gr.Column(scale=5):
                mode = gr.Radio(["LLM 对话", "知识库问答"],
                                label="请选择使用模式",
                                value="知识库问答", )
                vs_setting = gr.Accordion("配置知识库")
                mode.change(fn=change_mode,
                            inputs=mode,
                            outputs=vs_setting)
                with vs_setting:
                    select_vs = gr.Dropdown(vs_list.value,
                                            label="请选择要加载的知识库",
                                            interactive=True,
                                            value=vs_list.value[0] if len(vs_list.value) > 0 else None
                                            )
                    vs_name = gr.Textbox(label="请输入新建知识库名称",
                                         lines=1,
                                         interactive=True)
                    vs_add = gr.Button(value="添加至知识库选项")
                    vs_add.click(fn=add_vs_name,
                                 inputs=[vs_name, vs_list, chatbot],
                                 outputs=[select_vs, vs_list, chatbot])

                    file2vs = gr.Column(visible=False)
                    with file2vs:
                        # load_vs = gr.Button("加载知识库")
                        gr.Markdown("向知识库中添加文件")
                        with gr.Tab("上传文件"):
                            files = gr.File(label="添加文件",
                                            file_types=['.txt', '.md', '.docx', '.pdf'],
                                            file_count="multiple",
                                            show_label=False
                                            )
                            load_file_button = gr.Button("上传文件并加载知识库")
                        with gr.Tab("上传文件夹"):
                            folder_files = gr.File(label="添加文件",
                                                   # file_types=['.txt', '.md', '.docx', '.pdf'],
                                                   file_count="directory",
                                                   show_label=False
                                                   )
                            load_folder_button = gr.Button("上传文件夹并加载知识库")
                    # load_vs.click(fn=)
                    select_vs.change(fn=change_vs_name_input,
                                     inputs=select_vs,
                                     outputs=[vs_name, vs_add, file2vs, vs_path])
                    # 将上传的文件保存到content文件夹下,并更新下拉框
                    load_file_button.click(get_vector_store,
                                           show_progress=True,
                                           inputs=[select_vs, files, chatbot],
                                           outputs=[vs_path, files, chatbot],
                                           )
                    load_folder_button.click(get_vector_store,
                                             show_progress=True,
                                             inputs=[select_vs, folder_files, chatbot],
                                             outputs=[vs_path, folder_files, chatbot],
                                             )
                    query.submit(get_answer,
                                 [query, vs_path, chatbot, mode],
                                 [chatbot, query],
                                 )
    with gr.Tab("模型配置"):
        llm_model = gr.Radio(llm_model_dict_list,
                             label="LLM 模型",
                             value=LLM_MODEL,
                             interactive=True)
        llm_history_len = gr.Slider(0,
                                    10,
                                    value=LLM_HISTORY_LEN,
                                    step=1,
                                    label="LLM 对话轮数",
                                    interactive=True)
        use_ptuning_v2 = gr.Checkbox(USE_PTUNING_V2,
                                     label="使用p-tuning-v2微调过的模型",
                                     interactive=True)
        embedding_model = gr.Radio(embedding_model_dict_list,
                                   label="Embedding 模型",
                                   value=EMBEDDING_MODEL,
                                   interactive=True)
        top_k = gr.Slider(1,
                          20,
                          value=VECTOR_SEARCH_TOP_K,
                          step=1,
                          label="向量匹配 top k",
                          interactive=True)
        load_model_button = gr.Button("重新加载模型")
    load_model_button.click(reinit_model,
                            show_progress=True,
                            inputs=[llm_model, embedding_model, llm_history_len, use_ptuning_v2, top_k, chatbot],
                            outputs=chatbot
                            )

demo.queue(concurrency_count=3
           ).launch(server_name='0.0.0.0',
                    server_port=7860,
                    show_api=False,
                    share=False,
                    inbrowser=False)
