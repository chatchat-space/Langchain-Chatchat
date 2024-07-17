from open_chatcaht.chatchat_api import ChatChat

chatchat = ChatChat()
print(chatchat.tool.list())
print(chatchat.tool.call('calculate', {"text": "3+5/2"}))