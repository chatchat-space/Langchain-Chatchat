from typing import List
from langchain.document_loaders.unstructured import UnstructuredFileLoader
from langchain.docstore.document import Document

# https://github.com/langchain-ai/langchain/blob/master/libs/langchain/langchain/document_loaders/csv_loader.py

class RapidCSVLoader(UnstructuredFileLoader):
    def _get_elements(self) -> List:
        def csv2text(filepath):
            import csv
            with open(filepath, 'r') as file:
                csv_reader = csv.reader(file)
                documents = []
                for row in csv_reader:
                    if row:
                        doc = Document(page_content=row[0], metadata={"source": self.file_path, "is_qa": True, "answer": row[1]})
                        documents.append(doc)
            return documents

        return csv2text(self.file_path)
  
        

if __name__ == "__main__":
    loader = RapidCSVLoader(file_path="../tests/samples/ocr_test.csv")
    docs = loader.load()
    print(docs)
    for doc in docs:
        print(doc)