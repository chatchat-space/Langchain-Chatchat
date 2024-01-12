from pathlib import Path
from pprint import pprint
import os
import shutil
import sys
root_path = Path(__file__).parent.parent
sys.path.append(str(root_path))

from server.knowledge_base.kb_service.base import KBServiceFactory
from server.knowledge_base.utils import get_kb_path, get_doc_path, KnowledgeFile
from server.knowledge_base.migrate import folder2db, prune_db_docs, prune_folder_files


# setup test knowledge base
kb_name = "test_kb_for_migrate"
test_files = {
    "readme.md": str(root_path / "readme.md"),
}


kb_path = get_kb_path(kb_name)
doc_path = get_doc_path(kb_name)

if not os.path.isdir(doc_path):
    os.makedirs(doc_path)

for k, v in test_files.items():
    shutil.copy(v, os.path.join(doc_path, k))


def test_recreate_vs():
    folder2db([kb_name], "recreate_vs")

    kb = KBServiceFactory.get_service_by_name(kb_name)
    assert kb and kb.exists()

    files = kb.list_files()
    print(files)
    for name in test_files:
        assert name in files
        path = os.path.join(doc_path, name)

        # list docs based on file name
        docs = kb.list_docs(file_name=name)
        assert len(docs) > 0
        pprint(docs[0])
        for doc in docs:
            assert doc.metadata["source"] == name

        # list docs base on metadata
        docs = kb.list_docs(metadata={"source": name})
        assert len(docs) > 0

        for doc in docs:
            assert doc.metadata["source"] == name


def test_increment():
    kb = KBServiceFactory.get_service_by_name(kb_name)
    kb.clear_vs()
    assert kb.list_files() == []
    assert kb.list_docs() == []

    folder2db([kb_name], "increment")

    files = kb.list_files()
    print(files)
    for f in test_files:
        assert f in files

        docs = kb.list_docs(file_name=f)
        assert len(docs) > 0
        pprint(docs[0])

        for doc in docs:
            assert doc.metadata["source"] == f


def test_prune_db():
    del_file, keep_file = list(test_files)[:2]
    os.remove(os.path.join(doc_path, del_file))

    prune_db_docs([kb_name])

    kb = KBServiceFactory.get_service_by_name(kb_name)
    files = kb.list_files()
    print(files)
    assert del_file not in files
    assert keep_file in files

    docs = kb.list_docs(file_name=del_file)
    assert len(docs) == 0

    docs = kb.list_docs(file_name=keep_file)
    assert len(docs) > 0
    pprint(docs[0])

    shutil.copy(test_files[del_file], os.path.join(doc_path, del_file))


def test_prune_folder():
    del_file, keep_file = list(test_files)[:2]
    kb = KBServiceFactory.get_service_by_name(kb_name)

    # delete docs for file
    kb.delete_doc(KnowledgeFile(del_file, kb_name))
    files = kb.list_files()
    print(files)
    assert del_file not in files
    assert keep_file in files

    docs = kb.list_docs(file_name=del_file)
    assert len(docs) == 0

    docs = kb.list_docs(file_name=keep_file)
    assert len(docs) > 0

    docs = kb.list_docs(file_name=del_file)
    assert len(docs) == 0

    assert os.path.isfile(os.path.join(doc_path, del_file))

    # prune folder
    prune_folder_files([kb_name])

    # check result
    assert not os.path.isfile(os.path.join(doc_path, del_file))
    assert os.path.isfile(os.path.join(doc_path, keep_file))


def test_drop_kb():
    kb = KBServiceFactory.get_service_by_name(kb_name)
    kb.drop_kb()
    assert not kb.exists()
    assert not os.path.isdir(kb_path)

    kb = KBServiceFactory.get_service_by_name(kb_name)
    assert kb is None
