from langchain.embeddings import HuggingFaceEmbeddings
from ImageBind import data
import torch
from ImageBind.models import imagebind_model
from ImageBind.models.imagebind_model import ModalityType
from typing import Any, List

device = "cuda:0" if torch.cuda.is_available() else "cpu"

model = imagebind_model.imagebind_huge(pretrained=True)
model.eval()
model.to(device)
print("ImageBind loaded")


class MyEmbeddings(HuggingFaceEmbeddings):
    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)
        
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Compute doc embeddings using a HuggingFace transformer model.

        Args:
            texts: The list of texts to embed.

        Returns:
            List of embeddings, one for each text.
        """
        texts = list(map(lambda x: x.replace("\n", " "), texts))
        print("ImageBind used")
        embeddings = data.load_and_transform_text(texts, device)
        return embeddings.tolist()

    def embed_query(self, text: str) -> List[float]:
        """Compute query embeddings using a HuggingFace transformer model.

        Args:
            text: The text to embed.

        Returns:
            Embeddings for the text.
        """
        text = text.replace("\n", " ")
        print("ImageBind used")
        embedding = data.load_and_transform_text(texts, device)
        return embedding.tolist()
