import logging

from open_chatcaht.chatchat_api import ChatChat

chatchat = ChatChat(log_level=logging.DEBUG)
# print('create_kb', chatchat.knowledge.create_kb(knowledge_base_name="example_kb"))
# print('update_kb_info', chatchat.knowledge.update_kb_info(knowledge_base_name="example_kb", kb_info='aaaaaaa'))
# print('list_kb', chatchat.knowledge.list_kb())
# print('list_kb_docs_file', chatchat.knowledge.list_kb_docs_file(knowledge_base_name="samples"))
# print('delete_kb', chatchat.knowledge.delete_kb(knowledge_base_name="example_kb"))
# print('search_kb_docs', chatchat.knowledge.search_kb_docs(knowledge_base_name="example_kb", query="hello"))
# print('upload_kb_docs', chatchat.knowledge.upload_kb_docs(
#     files=["data/upload_file1.txt", "data/upload_file2.txt"],
#     knowledge_base_name="samples",
# ))
# print('search_kb_docs', chatchat.knowledge.search_kb_docs(knowledge_base_name="example_kb", query="hello"))
# print('recreate_vector_store', chatchat.knowledge.recreate_vector_store(
#     knowledge_base_name="samples",
# ))
# print('recreate_summary_vector_store', chatchat.knowledge.recreate_summary_vector_store(
#     knowledge_base_name="samples",
#     embed_model="embedding-2",
#     model_name="glm-4",
# ))
print('summary_file_to_vector_store', chatchat.knowledge.summary_file_to_vector_store(
    knowledge_base_name="samples",
    file_name="data/upload_file1.txt",
    embed_model="embedding-2",
))
# print('summary_file_to_vector_store', chatchat.knowledge.summary_doc_ids_to_vector_store(
#     knowledge_base_name="samples",
#     file_name="data/upload_file1.txt",
# ))
# print('delete_kb_docs', chatchat.knowledge.delete_kb_docs(
#     knowledge_base_name="samples",
#     file_names=["upload_file1.txt"],
# ))

# print(chatchat.tool.list())
# print(chatchat.tool.call('calculate', {"text": "3+5/2"}))
