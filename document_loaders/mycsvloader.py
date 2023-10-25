from typing import List
from langchain.document_loaders.unstructured import UnstructuredFileLoader


class RapidCSVLoader(UnstructuredFileLoader):
    def _get_elements(self) -> List:
        def csv2text(filepath):
            import csv
            resp = ""
            with open(filepath, 'r') as file:
                csv_reader = csv.reader(file)
                for row in csv_reader:
                    if row:
                        resp += row[0] + "\n"
            return resp

        text = csv2text(self.file_path)
        from unstructured.partition.text import partition_text
        return partition_text(text=text, **self.unstructured_kwargs)
  
        

if __name__ == "__main__":
    loader = RapidCSVLoader(file_path="../tests/samples/ocr_test.csv")
    docs = loader.load()
    print(docs)