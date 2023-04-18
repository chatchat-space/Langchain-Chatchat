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


def get_file_list():
    if not os.path.exists("content"):
        return []
    return [f for f in os.listdir("content")]


def get_vs_list():
    if not os.path.exists("vector_store"):
        return []
    return ["新建知识库"] + os.listdir("vector_store")


file_list = get_file_list()
vs_list = get_vs_list()

embedding_model_dict_list = list(embedding_model_dict.keys())

llm_model_dict_list = list(llm_model_dict.keys())

local_doc_qa = LocalDocQA()


def upload_file(file, chatbot):
    if not os.path.exists("content"):
        os.mkdir("content")
    filename = os.path.basename(file.name)
    shutil.move(file.name, "content/" + filename)
    # file_list首位插入新上传的文件
    file_list.insert(0, filename)
    status = "已将xx上传至xxx"
    return chatbot + [None, status]


def get_answer(query, vs_path, history):
    if vs_path:
        resp, history = local_doc_qa.get_knowledge_based_answer(
            query=query, vs_path=vs_path, chat_history=history)
        source = "".join([f"""<details> <summary>出处 {i + 1}</summary>
{doc.page_content}

<b>所属文件：</b>{doc.metadata["source"]}
</details>""" for i, doc in enumerate(resp["source_documents"])])
        history[-1][-1] += source
    else:
        resp = local_doc_qa.llm._call(query)
        history = history + [[None, resp + "\n如需基于知识库进行问答，请先加载知识库后，再进行提问。"]]
    return history, ""


def update_status(history, status):
    history = history + [[None, status]]
    print(status)
    return history


def init_model():
    try:
        local_doc_qa.init_cfg()
        local_doc_qa.llm._call("你好")
        return """模型已成功加载，请选择文件后点击"加载文件"按钮"""
    except Exception as e:
        print(e)
        return """模型未成功加载，请重新选择后点击"加载模型"按钮"""


def reinit_model(llm_model, embedding_model, llm_history_len, use_ptuning_v2, top_k, history):
    try:
        local_doc_qa.init_cfg(llm_model=llm_model,
                              embedding_model=embedding_model,
                              llm_history_len=llm_history_len,
                              use_ptuning_v2=use_ptuning_v2,
                              top_k=top_k)
        model_status = """模型已成功重新加载，请选择文件后点击"加载文件"按钮"""
    except Exception as e:
        print(e)
        model_status = """模型未成功重新加载，请重新选择后点击"加载模型"按钮"""
    return history + [[None, model_status]]


def get_vector_store(filepath, history):
    if local_doc_qa.llm and local_doc_qa.embeddings:
        vs_path = local_doc_qa.init_knowledge_vector_store(["content/" + filepath])
        if vs_path:
            file_status = "文件已成功加载，请开始提问"
        else:
            file_status = "文件未成功加载，请重新上传文件"
    else:
        file_status = "模型未完成加载，请先在加载模型后再导入文件"
        vs_path = None
    return vs_path, history + [[None, file_status]]


def change_vs_name_input(vs):
    if vs == "新建知识库":
        return gr.update(lines=1, visible=True)
    else:
        return gr.update(visible=False)


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

init_message = """欢迎使用 langchain-ChatGLM Web UI，开始提问前，请依次如下 3 个步骤：
1. 选择语言模型、Embedding 模型及相关参数，如果使用 ptuning-v2 方式微调过模型，将 PrefixEncoder 模型放在 ptuning-v2 文件夹里并勾选相关选项，然后点击"重新加载模型"，并等待加载完成提示
2. 上传或选择已有文件作为本地知识文档输入后点击"重新加载文档"，并等待加载完成提示
3. 输入要提交的问题后，点击回车提交 """

model_status = init_model()

with gr.Blocks(css=block_css) as demo:
    vs_path, file_status, model_status = gr.State(""), gr.State(""), gr.State(model_status)
    gr.Markdown(webui_title)
    with gr.Tab("聊天"):
        with gr.Row():
            with gr.Column(scale=2):
                chatbot = gr.Chatbot([[None, init_message], [None, model_status.value]],
                                     elem_id="chat-box",
                                     show_label=False).style(height=750)
                query = gr.Textbox(show_label=False,
                                   placeholder="请输入提问内容，按回车进行提交",
                                   ).style(container=False)
            with gr.Column(scale=1):
                gr.Markdown("请选择使用模式")
                gr.Radio(["默认", "知识库问答"],
                         label="请选择使用模式",
                         info="默认模式将不使用知识库")
                with gr.Accordion("配置知识库"):
                # gr.Markdown("配置知识库")
                    select_vs = gr.Dropdown(vs_list,
                                            label="请选择要加载的知识库",
                                            interactive=True,
                                            value=vs_list[0] if len(vs_list) > 0 else None)
                    vs_name = gr.Textbox(label="请输入新建知识库名称",
                                         lines=1,
                                         interactive=True)
                    select_vs.change(fn=change_vs_name_input,
                                     inputs=select_vs,
                                     outputs=vs_name)
                    gr.Markdown("向知识库中添加文件")
                    with gr.Tab("上传文件"):
                        files = gr.File(label="添加文件",
                                        file_types=['.txt', '.md', '.docx', '.pdf'],
                                        file_count="multiple",
                                        show_label=False
                                        )
                        load_file_button = gr.Button("上传文件")
                    with gr.Tab("上传文件夹"):
                        folder_files = gr.File(label="添加文件",
                                               file_types=['.txt', '.md', '.docx', '.pdf'],
                                               file_count="directory",
                                               show_label=False
                                               )
                        load_folder_button = gr.Button("上传文件夹")
    with gr.Tab("模型配置"):
        llm_model = gr.Radio(llm_model_dict_list,
                             label="LLM 模型",
                             value=LLM_MODEL,
                             interactive=True)
        llm_history_len = gr.Slider(0,
                                    10,
                                    value=LLM_HISTORY_LEN,
                                    step=1,
                                    label="LLM history len",
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
    # 将上传的文件保存到content文件夹下,并更新下拉框
    files.upload(upload_file,
                 inputs=[files, chatbot],
                 outputs=chatbot)
    load_file_button.click(get_vector_store,
                           show_progress=True,
                           inputs=[select_vs, chatbot],
                           outputs=[vs_path, chatbot],
                           )
    query.submit(get_answer,
                 [query, vs_path, chatbot],
                 [chatbot, query],
                 )

demo.queue(concurrency_count=3
           ).launch(server_name='0.0.0.0',
                    server_port=7860,
                    show_api=False,
                    share=False,
                    inbrowser=False)
