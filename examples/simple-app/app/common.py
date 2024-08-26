# ruff: noqa: B008

import logging
import os
import pickle
import sys
from enum import Enum
from pathlib import Path

import pandas as pd
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

from langchain_graphrag.indexing import IndexerArtifacts

_LOGGER = logging.getLogger("main:common")

_OLLAMA_NUM_CTX_DEFAULT_CHOICES: dict[str, int] = {
    "gemma2": 8192,
    "llama3.1": 8192,
    "phi3.5": 8192,
}


class LLMType(str, Enum):
    openai: str = "openai"
    azure_openai: str = "azure_openai"
    ollama: str = "ollama"


class EmbeddingModelType(str, Enum):
    openai: str = "openai"
    azure_openai: str = "azure_openai"
    ollama: str = "ollama"


def check_required_envs(envs_to_check: list[str]):
    for e in envs_to_check:
        if not os.getenv(e):
            msg = f"""
                Please set the environment variable - {e}
                Look in .env.example file for the required environment variables.
                Rename the .env.example file to .env and 
                set the values of the required environment variables.
            """
            print(msg)

            sys.exit(-1)


def check_if_necessary_azure_env_set():
    azure_envs = [
        "LANGCHAIN_GRAPHRAG_AZURE_OPENAI_CHAT_API_KEY",
        "LANGCHAIN_GRAPHRAG_AZURE_OPENAI_CHAT_ENDPOINT",
        "LANGCHAIN_GRAPHRAG_AZURE_OPENAI_CHAT_DEPLOYMENT",
        "LANGCHAIN_GRAPHRAG_AZURE_OPENAI_EMBED_API_KEY",
        "LANGCHAIN_GRAPHRAG_AZURE_OPENAI_EMBED_ENDPOINT",
        "LANGCHAIN_GRAPHRAG_AZURE_OPENAI_EMBED_DEPLOYMENT",
    ]

    check_required_envs(azure_envs)


def check_if_necessary_openai_env_set():
    openai_envs = [
        "LANGCHAIN_GRAPHRAG_OPENAI_CHAT_API_KEY",
        "LANGCHAIN_GRAPHRAG_OPENAI_EMBED_API_KEY",
    ]

    check_required_envs(openai_envs)


def trace_via_langsmith():
    check_required_envs(["LANGCHAIN_API_KEY"])

    assert os.getenv("LANGCHAIN_API_KEY") is not None, "Required LANGCHAIN_API_KEY"

    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"
    os.environ["LANGCHAIN_PROJECT"] = "langchain-graphrag"


def make_llm_instance(
    llm_type: LLMType,
    model: str,
    cache_dir: Path,
    ollama_num_context: int | None = None,
    temperature: float = 0.0,
    top_p: float = 1.0,
) -> BaseLLM:
    if llm_type == LLMType.openai:
        check_if_necessary_openai_env_set()
        return ChatOpenAI(
            model=model,
            api_key=os.getenv("LANGCHAIN_GRAPHRAG_OPENAI_CHAT_API_KEY"),
            cache=SQLiteCache(str(cache_dir / "openai_cache.db")),
            temperature=temperature,
            top_p=top_p,
        )

    if llm_type == LLMType.azure_openai:
        check_if_necessary_azure_env_set()
        return AzureChatOpenAI(
            model=model,
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
        if ollama_num_context is None:
            for k, v in _OLLAMA_NUM_CTX_DEFAULT_CHOICES.items():
                if k in model:
                    ollama_num_context = v
                    _LOGGER.warning(
                        f"******* Forcing num_context={v} for {model} *******"
                    )
                    break

            if ollama_num_context is None:
                _LOGGER.warning(
                    "******* Note - Good idea to provide num_context for Ollama Model *******"
                )

        return OllamaLLM(
            model=model,
            cache=SQLiteCache(str(cache_dir / f"ollama-{model.replace(':','-')}.db")),
            temperature=temperature,
            top_p=top_p,
            num_ctx=ollama_num_context,
            num_predict=-1,
        )

    raise ValueError


def make_embedding_instance(
    embedding_type: EmbeddingModelType,
    model: str,
    cache_dir: Path,
) -> Embeddings:
    underlying_embedding: Embeddings

    if embedding_type == EmbeddingModelType.openai:
        check_if_necessary_openai_env_set()
        underlying_embedding = OpenAIEmbeddings(
            model=model,
            api_key=os.getenv("LANGCHAIN_GRAPHRAG_OPENAI_EMBED_API_KEY"),
        )
    elif embedding_type == EmbeddingModelType.azure_openai:
        check_if_necessary_azure_env_set()
        underlying_embedding = AzureOpenAIEmbeddings(
            model=model,
            api_version="2024-02-15-preview",
            api_key=os.getenv("LANGCHAIN_GRAPHRAG_AZURE_OPENAI_EMBED_API_KEY"),
            azure_endpoint=os.getenv("LANGCHAIN_GRAPHRAG_AZURE_OPENAI_EMBED_ENDPOINT"),
            azure_deployment=os.getenv(
                "LANGCHAIN_GRAPHRAG_AZURE_OPENAI_EMBED_DEPLOYMENT"
            ),
        )
    elif embedding_type == EmbeddingModelType.ollama:
        underlying_embedding = OllamaEmbeddings(model=model)

    embedding_db_path = "sqlite:///" + str(cache_dir.joinpath("embedding.db"))
    store = SQLStore(namespace=model, db_url=embedding_db_path)
    store.create_schema()

    return CacheBackedEmbeddings.from_bytes_store(
        underlying_embeddings=underlying_embedding,
        document_embedding_cache=store,
    )


def save_artifacts(artifacts: IndexerArtifacts, path: Path):
    artifacts.entities.to_parquet(f"{path}/entities.parquet")
    artifacts.relationships.to_parquet(f"{path}/relationships.parquet")
    artifacts.text_units.to_parquet(f"{path}/text_units.parquet")
    artifacts.communities_reports.to_parquet(f"{path}/communities_reports.parquet")

    if artifacts.graph is not None:
        with path.joinpath("graph.pickle").open("wb") as fp:
            pickle.dump(artifacts.graph, fp)

    if artifacts.communities is not None:
        with path.joinpath("community_info.pickle").open("wb") as fp:
            pickle.dump(artifacts.communities, fp)


def load_artifacts(path: Path) -> IndexerArtifacts:
    entities = pd.read_parquet(f"{path}/entities.parquet")
    relationships = pd.read_parquet(f"{path}/relationships.parquet")
    text_units = pd.read_parquet(f"{path}/text_units.parquet")
    communities_reports = pd.read_parquet(f"{path}/communities_reports.parquet")

    graph = None
    communities = None

    graph_pickled = path.joinpath("graph.pickle")
    if graph_pickled.exists():
        with graph_pickled.open("rb") as fp:
            graph = pickle.load(fp)  # noqa: S301

    community_info_pickled = path.joinpath("community_info.pickle")
    if community_info_pickled.exists():
        with community_info_pickled.open("rb") as fp:
            communities = pickle.load(fp)  # noqa: S301

    return IndexerArtifacts(
        entities,
        relationships,
        text_units,
        communities_reports,
        graph=graph,
        communities=communities,
    )


def get_artifacts_dir_name(model: str) -> str:
    return f"artifacts-{model.replace(':','-')}"
