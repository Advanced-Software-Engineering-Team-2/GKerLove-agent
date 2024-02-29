from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import TextLoader
from langchain.tools.retriever import create_retriever_tool

from config import config


def create_experience_tool(file_path: str):
    loader = TextLoader(file_path)
    documents = loader.load()
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    texts = text_splitter.split_documents(documents)
    embeddings = OpenAIEmbeddings(base_url=config.openai_base_url)
    db = FAISS.from_documents(texts, embeddings)
    retriever = db.as_retriever()
    return create_retriever_tool(
        retriever,
        "search_experience_about_yourself",
        "Searches experience about yourself. When it comes to your information or experiences, you must use this tool to retrieve.",
    )
