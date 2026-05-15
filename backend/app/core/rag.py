"""
RAG 检索器 — Chroma 向量库 + DashScope Embedding
"""
import os
import tempfile
from typing import List, Optional

from langchain_chroma import Chroma
from langchain_community.document_loaders import (
    TextLoader,
    PyPDFLoader,
    CSVLoader,
)
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.config.settings import settings


def load_documents(uploaded_files: list) -> list:
    """从上传的文件中提取文档"""
    docs = []
    temp_dir = tempfile.TemporaryDirectory()

    for file in uploaded_files:
        temp_filepath = os.path.join(temp_dir.name, file.filename)
        with open(temp_filepath, "wb") as f:
            f.write(file.file.read())

        ext = os.path.splitext(file.filename)[1].lower()
        try:
            if ext == ".txt":
                loader = TextLoader(temp_filepath, encoding="utf-8")
            elif ext == ".pdf":
                loader = PyPDFLoader(temp_filepath)
            elif ext == ".csv":
                loader = CSVLoader(temp_filepath, encoding="utf-8")
            else:
                continue
            docs.extend(loader.load())
        except Exception:
            continue

    return docs


def build_retriever(docs: list) -> Optional[object]:
    """构建向量检索器"""
    if not docs:
        return None

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.CHUNK_SIZE,
        chunk_overlap=settings.CHUNK_OVERLAP,
    )
    splits = text_splitter.split_documents(docs)

    embeddings = DashScopeEmbeddings(
        model=settings.EMBEDDING_MODEL,
        dashscope_api_key=settings.DASHSCOPE_API_KEY,
    )

    vectordb = Chroma.from_documents(splits, embeddings)
    return vectordb.as_retriever(search_kwargs={"k": settings.RETRIEVER_K})
