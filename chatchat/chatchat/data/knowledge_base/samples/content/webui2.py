from nicegui import ui, Client, app, run
from nicegui.events import ValueChangeEventArguments
from configs import (VERSION, LLM_MODELS, TEMPERATURE, HISTORY_LEN,
                     VECTOR_SEARCH_TOP_K, SEARCH_ENGINE_TOP_K)
from webui_pages.utils import AsyncApiRequest
import asyncio
from typing import Any, List, Dict, Any


app.add_static_files("/image", "img")


class Session:
    def __init__(self) -> None:
        user = app.storage.user
        for k, v in self._attrs().items():
            user.setdefault(k, v)

    def _attrs(self) -> Dict[str, Any]:
        return {
            "messages": [],
            "query": "",
            "thinking": False,
            "cur_kb": "",
            "cur_temperature": TEMPERATURE,
            "chat_list": [],
            "cur_chat": "",
        }

    @property
    def user(self):
        return app.storage.user

    def __getattr__(self, attr: str) -> Any:
        if attr in self._attrs():
            return self.user[attr]
        else:
            raise AttributeError(attr)

    def __setattr__(self, attr: str, val: Any) -> None:
        if attr in self._attrs():
            self.user[attr] = val
        else:
            raise AttributeError(attr)


def make_header(left_drawer, right_drawer):
    with ui.header().classes("bg-black p-2") as header:
        with ui.link():
            ui.icon("menu", size="md").on("click", lambda: left_drawer.toggle())
        ui.image("img/logo-long-chatchat-trans-v2.png").props("fit=scale-down").classes("h-8 w-48 float-left")
        left_header = ui.row().props('id="left-header"')
        ui.element("q-space")
        right_header = ui.row().props('id="right-header"')
        ui.label(f"(Version: {VERSION})").classes("text-grey text-xs pt-4")
        with ui.link():
            ui.icon("menu", size="md").on("click", lambda: right_drawer.toggle())
        return left_header, right_header


def make_left_drawer(links: List, current: str):
    with ui.left_drawer(bordered=True, elevated=True) as drawer:
        return drawer


@ui.refreshable
async def output_messages():
    session = Session()

    for msg in session.messages:
        is_user = msg["role"] == "user"
        if is_user:
            name = "User"
            avatar = "/image/user_avatar.png"
        else:
            name = "AI"
            avatar = "/image/chatchat_icon_blue_square_v2.png"
        ele = ui.chat_message([], sent=False, name=None, avatar=avatar)
        with ele.add_slot("default"):
            ui.markdown(msg["content"])
    
    ui.query("img.q-message-avatar").classes("self-start")
    (ui.query("div.q-message-text--received")
     .classes("bg-green-100")
     .style("border-radius: 5px;"))
    # (ui.query("div.q-message-text--received")
    #  .run_method("remove_classes", ["q-message-text--received"]))
    # await ui.run_javascript("window.sc")


@ui.page("/", title="Langchain-Chatchat WebUI")
async def index(client: Client):
    ui.add_head_html('''<style>
                     p > code {color: green;padding: 2px;}
                     pre:has(code) {background-color: #eee; padding: 10px;} !important
                     </style>''')

    async def send():
        question = query.value.strip()
        query.value = ""

        if not question:
            return

        if question == "/clear":
            session.messages = []
            output_messages.refresh()
            return
        
        session.thinking = True
        session.messages.append({"role": "user", "content": question})
        session.messages.append({"role": "assistant", "content": "Thinking..."})
        output_messages.refresh()
        await asyncio.sleep(0.1)

        text = ""
        async for chunk in api.chat_chat(question,
                                   stream=True,
                                   conversation_id=None,
                                   model=cur_llm_model.value,
                                   temperature=temperature.value):
            text += chunk.get("text", "")
            tail = " ▌"
            if text.count("```") % 2 == 1:
                if text[-1] != "`":
                    tail += "\n```\n"
                elif text[-2:] == "``":
                    tail += "`\n"
                elif text[-1:] == "`":
                    tail += "``\n"
            session.messages[-1]["content"] = text + tail
            output_messages.refresh()
            await asyncio.sleep(0.1)

        session.messages[-1]["content"] = text
        output_messages.refresh()
        await asyncio.sleep(0.1)
        session.thinking = False

    session = Session()
    api = AsyncApiRequest()

    left_drawer = make_left_drawer([], "")

    with ui.right_drawer(bordered=True, elevated=True) as right_drawer:
        ui.markdown("### 灵感大全")
        user_name = ui.input("用户名称", value="用户")
        system_message = (ui.input("AI系统消息",
                                   value="你是一个聪明的人工智能助手，可以回答用户提出的问题。")
                            .props("autogrow"))
        chat_image = ui.upload(label="上传图片").classes("w-full mt-5")
        chat_file = ui.upload(label="上传文件").classes("w-full mt-5")

    left_header, right_header = make_header(left_drawer, right_drawer)

    with left_header:
        chat_session = (ui.radio(["会话1", "会话2"], value="会话1")
                        .props("inline")
                        .classes("p-0"))

    with left_drawer:
        ui.markdown("### 配置项")

        def on_chat_mode_change(e: ValueChangeEventArguments):
            if e.value == "Agent对话":
                session.cur_temperature = temperature.value
                temperature.set_value(0.01)
            else:
                temperature.set_value(session.cur_temperature)

        chat_mode = ui.select(["LLM 对话", "知识库问答", "搜索引擎问答", "Agent对话"],
                            label="对话模式",
                            value="LLM 对话",
                            on_change=on_chat_mode_change,
                            )
        ui.separator()

        with ui.expansion("模型配置", icon="psychology", value=True):
            running_models = await api.list_running_models()
            config_models = await api.list_config_models()
            models = {x: f"{x}(running)" for x in running_models}
            for v in config_models.values():
                for m in v:
                    if m not in running_models:
                        models.update({m: m})
            cur_llm_model = ui.select(models, label="LLM模型", value=LLM_MODELS[0], with_input=True, clearable=True)
            temperature = ui.number("Temperature", value=TEMPERATURE, min=0, max=1, step=0.01)
            history_len = ui.number("历史对话轮数", value=HISTORY_LEN, min=0, max=10)

        with (ui.expansion("知识库配置", icon="book", value=True)
              .bind_visibility_from(chat_mode, "value", value="知识库问答")):
            def on_kb_change(e: ValueChangeEventArguments):
                session.cur_kb = e.value

            kb_names = await api.list_knowledge_bases()
            kb_name = ui.select(kb_names,
                                label="知识库",
                                value=session.cur_kb or kb_names[0],
                                on_change=on_kb_change,
                                )
            vector_top_k = ui.number("Top K", value=VECTOR_SEARCH_TOP_K, min=1, max=10)

        with (ui.expansion("搜索引擎配置", icon="travel_explore", value=True)
              .bind_visibility_from(chat_mode, "value", value="搜索引擎问答")):
            search_engine = ui.select(["Bing", "Duckduckgo"], value="Bing")
            search_top_k = ui.number("Top K", value=SEARCH_ENGINE_TOP_K, min=1, max=10)

    await client.connected()
    with ui.column():
        await output_messages()

    with ui.row().classes("absolute bottom-2 left-20 right-20"):
        # command = ui.select(["/clear", "/upload"]).classes("w-1/4")
        query = (ui.input(autocomplete=["/clear", "/upload"],
                          placeholder="input your question here.")
                          .classes("flex-grow")
                          .props('autogrow outlined autofocus counter dense clearable')
                          .bind_value(session, "query")
                          .on("keydown.enter.prevent", send)
        )
        with query.add_slot("after"):
            ui.button(icon="send", on_click=send).classes("self-center").props("small dense p-0 m-0")
        # query._props["autofocus"] = True
        # query._props["autogrow"] = True
        # query._props["placeholder"] = "input your question here."
        # query._props[":list"] = '["/clear", "/upload"]'
        # query._props["shadow-text"] = ["/clear", "/upload"]
        # ui.input(autocomplete=["/clear", "/upload"])



# TODO: 
# 右侧栏上下文：system_message, picture, file, 知识库文档预览


if __name__ in {"__main__", "__mp_main__"}:
    ui.run(port=5000, storage_secret="111111", reload=True)
