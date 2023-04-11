import gradio as gr
import os
import shutil
import knowledge_based_chatglm as kb


# class kb:
#     def __init__(self):
#         pass

#     def init_knowledge_vector_store(filepath):
#         return filepath

#     def get_knowledge_based_answer(*args):
#         return args


def get_file_list():
    if not os.path.exists("content"):
        return []
    return [f for f in os.listdir("content")]


file_list = get_file_list()

embedding_model_dict_list = list(kb.embedding_model_dict.keys())

llm_model_dict_list = list(kb.llm_model_dict.keys())


def upload_file(file):
    if not os.path.exists("content"):
        os.mkdir("content")
    filename = os.path.basename(file.name)
    shutil.move(file.name, "content/"+filename)
    # file_list首位插入新上传的文件
    file_list.insert(0, filename)
    return gr.Dropdown.update(choices=file_list, value=filename)


def getAnswer(q, v, h):
    resp, history = kb.get_knowledge_based_answer(
        query=q, vector_store=v, chat_history=h)
    return history, history


with gr.Blocks(css="""
.importantButton {
    background: linear-gradient(45deg, #7e0570,#5d1c99, #6e00ff) !important;
    border: none !important;
}

.importantButton:hover {
    background: linear-gradient(45deg, #ff00e0,#8500ff, #6e00ff) !important;
    border: none !important;
}

""") as demo:
    gr.Markdown(
        f"""
# 🎉langchain-ChatGLM WebUI🎉

👍 [https://github.com/imClumsyPanda/langchain-ChatGLM](https://github.com/imClumsyPanda/langchain-ChatGLM)

""")
    with gr.Row():
        with gr.Column(scale=2):
            chatbot = gr.Chatbot(elem_id="chat-box",
                                 show_label=False).style(height=600)
        with gr.Column(scale=1):
            with gr.Column():
                llm_model = gr.Radio(
                    llm_model_dict_list, label="llm model",
                    value="chatglm-6b", interactive=True)
                LLM_HISTORY_LEN = gr.Slider(
                    1, 10, value=3, step=1, label="LLM history len", interactive=True)
                embedding_model = gr.Radio(
                    embedding_model_dict_list, label="embedding model",
                    value="text2vec", interactive=True)
                VECTOR_SEARCH_TOP_K = gr.Slider(
                    1, 20, value=6, step=1, label="vector search top k", interactive=True)
                load_model_button = gr.Button("step.1：setting")
                load_model_button.click(lambda *args:
                                        kb.init_cfg(args[0], args[1], args[2], args[3]),
                                        show_progress=True,
                                        api_name="init_cfg",
                                        inputs=[llm_model, embedding_model, VECTOR_SEARCH_TOP_K, LLM_HISTORY_LEN])

            with gr.Column():
                with gr.Tab("select"):
                    selectFile = gr.Dropdown(
                        file_list, label="content file", interactive=True, value=file_list[0] if len(file_list) > 0 else None)
                with gr.Tab("upload"):
                    file = gr.File(label="content file", file_types=[
                                   '.txt', '.md', '.docx']).style(height=100)
                    # 将上传的文件保存到content文件夹下,并更新下拉框
                    file.upload(upload_file, inputs=file, outputs=selectFile)
                history = gr.State([])
                vector_store = gr.State()
                load_button = gr.Button("step.2：loading")
                load_button.click(lambda fileName:
                                  kb.init_knowledge_vector_store(
                                      "content/"+fileName),
                                  show_progress=True,
                                  api_name="init_knowledge_vector_store",
                                  inputs=selectFile, outputs=vector_store)

    with gr.Row():
        with gr.Column(scale=2):
            query = gr.Textbox(show_label=False, placeholder="Prompts", lines=1, value="用200字总结一下").style(
                container=False)
        with gr.Column(scale=1):
            generate_button = gr.Button(
                "step.3：asking", elem_classes="importantButton")
            generate_button.click(getAnswer, [query, vector_store, history],
                                [chatbot, history],api_name="get_knowledge_based_answer")


demo.queue(concurrency_count=3).launch(
    server_name='0.0.0.0', share=False, inbrowser=False)
