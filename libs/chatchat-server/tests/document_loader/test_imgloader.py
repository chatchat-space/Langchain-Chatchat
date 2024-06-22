import sys
from pathlib import Path

root_path = Path(__file__).parent.parent.parent
sys.path.append(str(root_path))
from pprint import pprint

test_files = {
    "ocr_test.jpg": str(root_path / "tests" / "samples" / "ocr_test.jpg"),
}


def test_rapidocrloader():
    img_path = test_files["ocr_test.jpg"]
    from document_loaders import RapidOCRLoader

    loader = RapidOCRLoader(img_path)
    docs = loader.load()
    pprint(docs)
    assert (
        isinstance(docs, list)
        and len(docs) > 0
        and isinstance(docs[0].page_content, str)
    )
