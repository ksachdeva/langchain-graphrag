# ruff: noqa: B008

import os
from enum import StrEnum
from pathlib import Path

from langchain.embeddings.cache import CacheBackedEmbeddings
from langchain_community.cache import SQLiteCache
from langchain_community.storage import SQLStore
from langchain_core.embeddings import Embeddings
from langchain_core.language_models import BaseLLM
from langchain_ollama import OllamaEmbeddings, OllamaLLM
from langchain_openai import (
    AzureChatOpenAI,
    AzureOpenAIEmbeddings,
    ChatOpenAI,
    OpenAIEmbeddings,
)


class LLMType(StrEnum):
    openai: str = "openai"
    azure_openai: str = "azure_openai"
    ollama: str = "ollama"


class LLMModel(StrEnum):
    gpt4o: str = "gpt-4o"
    gpt4omini: str = "gpt-4o-mini"
    gemma2_9b_instruct_q8_0: str = "gemma2:9b-instruct-q8_0"
    gemma2_27b_instruct_q6_K: str = "gemma2:27b-instruct-q6_K"  # noqa: N815


class EmbeddingModelType(StrEnum):
    openai: str = "openai"
    azure_openai: str = "azure_openai"
    ollama: str = "ollama"


class EmbeddingModel(StrEnum):
    text_embedding_3_small: str = "text-embedding-3-small"
    nomic_embed_text: str = "nomic_embed_text"


def make_llm_instance(
    llm_type: LLMType,
    llm_model: LLMModel,
    cache_dir: Path,
    temperature: float = 0.0,
    top_p: float = 1.0,
) -> BaseLLM:
    if llm_type == LLMType.openai:
        return ChatOpenAI(
            model=llm_model,
            api_key=os.getenv("LANGCHAIN_GRAPHRAG_OPENAI_CHAT_API_KEY"),
            cache=SQLiteCache(str(cache_dir / "openai_cache.db")),
            temperature=temperature,
            top_p=top_p,
        )

    if llm_type == LLMType.azure_openai:
        return AzureChatOpenAI(
            model=llm_model,
            api_version="2024-05-01-preview",
            api_key=os.getenv("LANGCHAIN_GRAPHRAG_AZURE_OPENAI_CHAT_API_KEY"),
            azure_endpoint=os.getenv("LANGCHAIN_GRAPHRAG_AZURE_OPENAI_CHAT_ENDPOINT"),
            azure_deployment=os.getenv(
                "LANGCHAIN_GRAPHRAG_AZURE_OPENAI_CHAT_DEPLOYMENT"
            ),
            cache=SQLiteCache(str(cache_dir / "azure_openai_cache.db")),
            temperature=temperature,
            top_p=top_p,
        )

    if llm_type == LLMType.ollama:
        return OllamaLLM(
            model=llm_model,
            cache=SQLiteCache(str(cache_dir / "ollama.db")),
            temperature=temperature,
            top_p=top_p,
        )

    raise ValueError


def make_embedding_instance(
    embedding_type: EmbeddingModelType,
    embedding_model: EmbeddingModel,
    cache_dir: Path,
) -> Embeddings:
    underlying_embedding: Embeddings

    if embedding_type == EmbeddingModelType.openai:
        underlying_embedding = OpenAIEmbeddings(
            model=embedding_model,
            api_key=os.getenv("LANGCHAIN_GRAPHRAG_OPENAI_EMBED_API_KEY"),
        )
    elif embedding_type == EmbeddingModelType.azure_openai:
        underlying_embedding = AzureOpenAIEmbeddings(
            model=embedding_model,
            api_version="2024-02-15-preview",
            api_key=os.getenv("LANGCHAIN_GRAPHRAG_AZURE_OPENAI_EMBED_API_KEY"),
            azure_endpoint=os.getenv("LANGCHAIN_GRAPHRAG_AZURE_OPENAI_EMBED_ENDPOINT"),
            azure_deployment=os.getenv(
                "LANGCHAIN_GRAPHRAG_AZURE_OPENAI_EMBED_DEPLOYMENT"
            ),
        )
    elif embedding_type == EmbeddingModelType.ollama:
        underlying_embedding = OllamaEmbeddings(model=embedding_model)

    embedding_db_path = "sqlite:///" + str(cache_dir.joinpath("embedding.db"))
    store = SQLStore(namespace=embedding_model, db_url=embedding_db_path)
    store.create_schema()

    return CacheBackedEmbeddings.from_bytes_store(
        underlying_embeddings=underlying_embedding,
        document_embedding_cache=store,
    )
