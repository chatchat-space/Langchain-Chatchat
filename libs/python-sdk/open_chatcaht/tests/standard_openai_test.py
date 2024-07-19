from open_chatcaht.chatchat_api import ChatChat
from open_chatcaht.types.standard_openai.chat_input import OpenAIChatInput

chatchat = ChatChat()

# print(chatchat.openai_adapter.list_models())
# for data in chatchat.openai_adapter.kb_chat(query='你好', kb_name="example_kb", model='glm-4'):
#     print(data)
open_ai_chat_input = OpenAIChatInput()
open_ai_chat_input.model = 'glm-4'
open_ai_chat_input.messages = [{"role": "system", "content": "你是一个 helpful assistant."}, ]
for data in chatchat.openai_adapter.completions(open_ai_chat_input):
    print(data)
