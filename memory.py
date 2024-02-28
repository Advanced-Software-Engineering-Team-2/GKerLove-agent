import faiss

from langchain_community.docstore import InMemoryDocstore
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain.memory import VectorStoreRetrieverMemory

from config import config


def create_memory(messages_num=10):
    embedding_size = 1536
    index = faiss.IndexFlatL2(embedding_size)
    embedding_fn = OpenAIEmbeddings(base_url=config.openai_base_url).embed_query
    vectorstore = FAISS(embedding_fn, index, InMemoryDocstore({}), {})
    retriever = vectorstore.as_retriever(search_kwargs=dict(k=messages_num))
    memory = VectorStoreRetrieverMemory(retriever=retriever, memory_key="chat_history")
    return memory
