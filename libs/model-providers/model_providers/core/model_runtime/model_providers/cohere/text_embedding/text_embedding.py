import time
from typing import Optional

import cohere
import numpy as np
from cohere.responses import Tokens

from model_providers.core.model_runtime.entities.model_entities import PriceType
from model_providers.core.model_runtime.entities.text_embedding_entities import (
    EmbeddingUsage,
    TextEmbeddingResult,
)
from model_providers.core.model_runtime.errors.invoke import (
    InvokeAuthorizationError,
    InvokeBadRequestError,
    InvokeConnectionError,
    InvokeError,
    InvokeRateLimitError,
    InvokeServerUnavailableError,
)
from model_providers.core.model_runtime.errors.validate import (
    CredentialsValidateFailedError,
)
from model_providers.core.model_runtime.model_providers.__base.text_embedding_model import (
    TextEmbeddingModel,
)


class CohereTextEmbeddingModel(TextEmbeddingModel):
    """
    Model class for Cohere text embedding model.
    """

    def _invoke(
        self,
        model: str,
        credentials: dict,
        texts: List[str],
        user: Optional[str] = None,
    ) -> TextEmbeddingResult:
        """
        Invoke text embedding model

        :param model: model name
        :param credentials: model credentials
        :param texts: texts to embed
        :param user: unique user id
        :return: embeddings result
        """
        # get model properties
        context_size = self._get_context_size(model, credentials)
        max_chunks = self._get_max_chunks(model, credentials)

        embeddings: List[List[float]] = [[] for _ in range(len(texts))]
        tokens = []
        indices = []
        used_tokens = 0

        for i, text in enumerate(texts):
            tokenize_response = self._tokenize(
                model=model, credentials=credentials, text=text
            )

            for j in range(0, tokenize_response.length, context_size):
                tokens += [tokenize_response.token_strings[j : j + context_size]]
                indices += [i]

        batched_embeddings = []
        _iter = range(0, len(tokens), max_chunks)

        for i in _iter:
            # call embedding model
            embeddings_batch, embedding_used_tokens = self._embedding_invoke(
                model=model,
                credentials=credentials,
                texts=["".join(token) for token in tokens[i : i + max_chunks]],
            )

            used_tokens += embedding_used_tokens
            batched_embeddings += embeddings_batch

        results: List[List[list[float]]] = [[] for _ in range(len(texts))]
        num_tokens_in_batch: List[List[int]] = [[] for _ in range(len(texts))]
        for i in range(len(indices)):
            results[indices[i]].append(batched_embeddings[i])
            num_tokens_in_batch[indices[i]].append(len(tokens[i]))

        for i in range(len(texts)):
            _result = results[i]
            if len(_result) == 0:
                embeddings_batch, embedding_used_tokens = self._embedding_invoke(
                    model=model, credentials=credentials, texts=[" "]
                )

                used_tokens += embedding_used_tokens
                average = embeddings_batch[0]
            else:
                average = np.average(_result, axis=0, weights=num_tokens_in_batch[i])
            embeddings[i] = (average / np.linalg.norm(average)).tolist()

        # calc usage
        usage = self._calc_response_usage(
            model=model, credentials=credentials, tokens=used_tokens
        )

        return TextEmbeddingResult(embeddings=embeddings, usage=usage, model=model)

    def get_num_tokens(self, model: str, credentials: dict, texts: List[str]) -> int:
        """
        Get number of tokens for given prompt messages

        :param model: model name
        :param credentials: model credentials
        :param texts: texts to embed
        :return:
        """
        if len(texts) == 0:
            return 0

        full_text = " ".join(texts)

        try:
            response = self._tokenize(
                model=model, credentials=credentials, text=full_text
            )
        except Exception as e:
            raise self._transform_invoke_error(e)

        return response.length

    def _tokenize(self, model: str, credentials: dict, text: str) -> Tokens:
        """
        Tokenize text
        :param model: model name
        :param credentials: model credentials
        :param text: text to tokenize
        :return:
        """
        if not text:
            return Tokens([], [], {})

        # initialize client
        client = cohere.Client(credentials.get("api_key"))

        response = client.tokenize(text=text, model=model)

        return response

    def validate_credentials(self, model: str, credentials: dict) -> None:
        """
        Validate model credentials

        :param model: model name
        :param credentials: model credentials
        :return:
        """
        try:
            # call embedding model
            self._embedding_invoke(model=model, credentials=credentials, texts=["ping"])
        except Exception as ex:
            raise CredentialsValidateFailedError(str(ex))

    def _embedding_invoke(
        self, model: str, credentials: dict, texts: List[str]
    ) -> tuple[List[list[float]], int]:
        """
        Invoke embedding model

        :param model: model name
        :param credentials: model credentials
        :param texts: texts to embed
        :return: embeddings and used tokens
        """
        # initialize client
        client = cohere.Client(credentials.get("api_key"))

        # call embedding model
        response = client.embed(
            texts=texts,
            model=model,
            input_type="search_document" if len(texts) > 1 else "search_query",
        )

        return response.embeddings, response.meta["billed_units"]["input_tokens"]

    def _calc_response_usage(
        self, model: str, credentials: dict, tokens: int
    ) -> EmbeddingUsage:
        """
        Calculate response usage

        :param model: model name
        :param credentials: model credentials
        :param tokens: input tokens
        :return: usage
        """
        # get input price info
        input_price_info = self.get_price(
            model=model,
            credentials=credentials,
            price_type=PriceType.INPUT,
            tokens=tokens,
        )

        # transform usage
        usage = EmbeddingUsage(
            tokens=tokens,
            total_tokens=tokens,
            unit_price=input_price_info.unit_price,
            price_unit=input_price_info.unit,
            total_price=input_price_info.total_amount,
            currency=input_price_info.currency,
            latency=time.perf_counter() - self.started_at,
        )

        return usage

    @property
    def _invoke_error_mapping(self) -> Dict[Type[InvokeError], List[Type[Exception]]]:
        """
        Map model invoke error to unified error
        The key is the error type thrown to the caller
        The value is the error type thrown by the model,
        which needs to be converted into a unified error type for the caller.

        :return: Invoke error mapping
        """
        return {
            InvokeConnectionError: [cohere.CohereConnectionError],
            InvokeServerUnavailableError: [],
            InvokeRateLimitError: [],
            InvokeAuthorizationError: [],
            InvokeBadRequestError: [
                cohere.CohereAPIError,
                cohere.CohereError,
            ],
        }
