import torch
from langchain.agents import ZeroShotAgent, Tool, AgentExecutor
from langchain.llms import OpenAI
from langchain.memory import ConversationBufferMemory, ReadOnlySharedMemory
from langchain.chains import LLMChain, RetrievalQA
from langchain.embeddings.huggingface import HuggingFaceEmbeddings
from langchain.prompts import PromptTemplate
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.document_loaders import TextLoader
from models import ChatGLM
import sentence_transformers
import os
import readline
from pathlib import Path


class ChatglmWithSharedMemoryOpenaiLLM:

    def __init__(self, params: dict = None):
        params = params or {}
        self.embedding_model = params.get('embedding_model', 'text2vec')
        self.vector_search_top_k = params.get('vector_search_top_k', 6)
        self.llm_model = params.get('llm_model', 'chatglm-6b')
        self.llm_history_len = params.get('llm_history_len', 10)
        self.device = 'cuda' if params.get('use_cuda', False) else 'cpu'
        self._embedding_model_dict = {
            "ernie-tiny": "nghuyong/ernie-3.0-nano-zh",
            "ernie-base": "nghuyong/ernie-3.0-base-zh",
            "text2vec": "GanymedeNil/text2vec-large-chinese",
        }
        self._llm_model_dict = {
            "chatglm-6b-int4-qe": "THUDM/chatglm-6b-int4-qe",
            "chatglm-6b-int4": "THUDM/chatglm-6b-int4",
            "chatglm-6b": "THUDM/chatglm-6b",
        }
        self.init_cfg()
        self.init_docsearch()
        self.init_state_of_history()
        self.summry_chain, self.memory = self.agents_answer()
        self.agent_chain = self.create_agent_chain()

    def init_cfg(self):
        self.chatglm = ChatGLM()
        self.chatglm.load_model(model_name_or_path=self._llm_model_dict[self.llm_model])
        self.chatglm.history_len = self.llm_history_len
        self.embeddings = HuggingFaceEmbeddings(model_name=self._embedding_model_dict[self.embedding_model],)
        self.embeddings.client = sentence_transformers.SentenceTransformer(self.embeddings.model_name,
                                                                           device=self.device)

    def init_docsearch(self):
        doc_path = str(Path.cwd() / "content/state_of_the_search.txt")
        loader = TextLoader(doc_path)
        documents = loader.load()
        text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
        texts = text_splitter.split_documents(documents)
        docsearch = Chroma.from_documents(texts, self.embeddings, collection_name="state-of-search")
        self.state_of_search = RetrievalQA.from_chain_type(llm=self.chatglm, chain_type="stuff", retriever=docsearch.as_retriever())

    def init_state_of_history(self):
        doc_path = str(Path.cwd() / "content/state_of_the_history.txt")
        loader = TextLoader(doc_path)
        documents = loader.load()
        text_splitter = CharacterTextSplitter(chunk_size=100, chunk_overlap=0)
        texts = text_splitter.split_documents(documents)
        docsearch = Chroma.from_documents(texts, self.embeddings, collection_name="state-of-history")
        self.state_of_history = RetrievalQA.from_chain_type(llm=self.chatglm, chain_type="stuff", retriever=docsearch.as_retriever())

    def agents_answer(self):
        template = """This is a conversation between a human and a bot:

        {chat_history}

        Write a summary of the conversation for {input}:
        """

        prompt = PromptTemplate(
            input_variables=["input", "chat_history"],
            template=template
        )
        memory = ConversationBufferMemory(memory_key="chat_history")
        readonlymemory = ReadOnlySharedMemory(memory=memory)
        summry_chain = LLMChain(
            llm=self.chatglm,
            prompt=prompt,
            verbose=True,
            memory=readonlymemory,  # use the read-only memory to prevent the tool from modifying the memory
        )
        return summry_chain, memory

    def create_agent_chain(self):
        tools = [
            Tool(
                name="State of Search QA System",
                func=self.state_of_search.run,
                description="当您需要搜索有关问题时非常有用。输入应该是一个完整的问题。"
            ),
            Tool(
                name="state-of-history-qa",
                func=self.state_of_history.run,
                description="跟露露的历史对话 - 当提出我们之间发生了什么事请时，这里面的回答是很有用的"
            ),
            Tool(
                name="Summary",
                func=self.summry_chain.run,
                description="useful for when you summarize a conversation. The input to this tool should be a string, representing who will read this summary."
            )
        ]

        prefix = """你需要充当一个倾听者,尽量回答人类的问题,你可以使用这里工具,它们非常有用:"""
        suffix = """Begin!

        {chat_history}
        Question: {input}
        {agent_scratchpad}"""

        prompt = ZeroShotAgent.create_prompt(
            tools,
            prefix=prefix,
            suffix=suffix,
            input_variables=["input", "chat_history", "agent_scratchpad"]
        )

        llm_chain = LLMChain(llm=OpenAI(temperature=0), prompt=prompt)
        agent = ZeroShotAgent(llm_chain=llm_chain, tools=tools, verbose=True)
        agent_chain = AgentExecutor.from_agent_and_tools(agent=agent, tools=tools, verbose=True, memory=self.memory)

        return agent_chain
