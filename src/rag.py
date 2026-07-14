"""LlamaIndex 文档检索：Markdown → 切分 → ChromaDB → 相似度检索。"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

from llama_index.core import (
    SimpleDirectoryReader,
    StorageContext,
    VectorStoreIndex,
    load_index_from_storage,
)
from llama_index.core.node_parser import SentenceSplitter
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

from src.config import get_settings, project_root


PERSIST_DIR = ".chroma_cache"


class DocSearcher:
    """封装 LlamaIndex + 本地 HuggingFace embedding 的文档检索器。"""

    def __init__(self, docs_dir: Optional[str] = None, persist_dir: Optional[str] = None):
        s = get_settings()
        self.docs_dir = docs_dir or s.docs_dir
        self.persist_dir = persist_dir or str(project_root() / PERSIST_DIR)
        self._index = None
        self._embed_model = None

    def _ensure_loaded(self):
        if self._index is not None:
            return
        # embedding 模型（首次会下载 ~120MB）
        self._embed_model = HuggingFaceEmbedding(
            model_name=get_settings().embed_model,
            cache_folder=str(project_root() / ".embed_cache"),
        )
        # 优先从持久化加载
        if os.path.exists(self.persist_dir) and os.listdir(self.persist_dir):
            storage = StorageContext.from_defaults(persist_dir=self.persist_dir)
            self._index = load_index_from_storage(
                storage, embed_model=self._embed_model
            )
        else:
            docs = SimpleDirectoryReader(
                input_dir=self.docs_dir, recursive=False, required_exts=[".md"]
            ).load_data()
            parser = SentenceSplitter(chunk_size=200, chunk_overlap=30)
            nodes = parser.get_nodes_from_documents(docs)
            self._index = VectorStoreIndex(nodes, embed_model=self._embed_model)
            self._index.storage_context.persist(persist_dir=self.persist_dir)

    def search(self, query: str, top_k: int = 3) -> list[dict]:
        self._ensure_loaded()
        retriever = self._index.as_retriever(similarity_top_k=top_k)
        results = retriever.retrieve(query)
        out = []
        for r in results:
            out.append({
                "text": r.node.text,
                "source": r.node.metadata.get("file_name", "unknown"),
                "score": float(r.score) if r.score is not None else 0.0,
            })
        return out