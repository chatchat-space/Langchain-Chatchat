from open_chatcaht.chatchat_api import ChatChat

chatchat = ChatChat()
# for data in chatchat.chat.kb_chat(query='你好',kb_name="example_kb",model='glm-4'):
#     print(data)

for data in chatchat.chat.kb_chat(query='你好', kb_name="example_kb", model='glm-4'):
    print(data)
