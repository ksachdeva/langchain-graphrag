import os
from enum import StrEnum
from pathlib import Path

from dotenv import load_dotenv

import typer
from typer import Typer

# going to do load_dotenv() here
# as OLLAMA_HOST needs to be in the environment
# before the imports below
load_dotenv()

from langchain_core.language_models import BaseLLM
from langchain_text_splitters import TokenTextSplitter

from langchain_community.cache import SQLiteCache
from langchain_community.document_loaders.directory import DirectoryLoader

from langchain_openai import ChatOpenAI, AzureChatOpenAI
from langchain_community.llms.ollama import Ollama

import langchain_graphrag.indexing.entity_extraction as er
import langchain_graphrag.indexing.entity_summarization as es

from langchain_graphrag.indexing.indexer import Indexer
from langchain_graphrag.indexing.text_unit_extractor import TextUnitExtractor
from langchain_graphrag.indexing.graph_clustering.community_detector import (
    HierarchicalLeidenCommunityDetector,
)

app = Typer()


class LLMType(StrEnum):
    openai: str = "openai"
    azure_openai: str = "azure_openai"
    ollama: str = "ollama"


class LLMModel(StrEnum):
    gpt4o: str = "gpt-4o"
    gpt4omini: str = "gpt-4o-mini"
    gemma2_9b_instruct_q8_0: str = "gemma2:9b-instruct-q8_0"


def make_llm_instance(
    llm_type: LLMType,
    llm_model: LLMModel,
    cache_dir: Path,
) -> BaseLLM:
    if llm_type == LLMType.openai:
        return ChatOpenAI(
            model=llm_model,
            openai_api_key=os.getenv("LANGCHAIN_GRAPHRAG_OPENAI_CHAT_API_KEY"),
            cache=SQLiteCache(cache_dir / "openai_cache.db"),
        )
    elif llm_type == LLMType.azure_openai:
        return AzureChatOpenAI(
            mode=llm_model,
            openai_api_version="2024-05-01-preview",
            openai_api_key=os.getenv("LANGCHAIN_GRAPHRAG_AZURE_OPENAI_CHAT_API_KEY"),
            azure_endpoint=os.getenv("LANGCHAIN_GRAPHRAG_AZURE_OPENAI_CHAT_ENDPOINT"),
            azure_deployment=os.getenv(
                "LANGCHAIN_GRAPHRAG_AZURE_OPENAI_CHAT_DEPLOYMENT"
            ),
            cache=SQLiteCache(cache_dir / "azure_openai_cache.db"),
        )
    elif llm_type == LLMType.ollama:
        return Ollama(
            model=llm_model,
            base_url=os.getenv("OLLAMA_HOST"),
            cache=SQLiteCache(cache_dir / "ollama.db"),
        )


@app.command()
def indexer(
    input_dir: Path = typer.Option(..., dir_okay=True, file_okay=False),
    output_dir: Path = typer.Option(..., dir_okay=True, file_okay=False),
    prompts_dir: Path = typer.Option(..., dir_okay=True, file_okay=False),
    llm_cache_dir: Path = typer.Option(..., dir_okay=True, file_okay=False),
    llm_type: LLMType = typer.Option(LLMType.openai, case_sensitive=False),
    llm_model: LLMModel = typer.Option(LLMModel.gpt4omini, case_sensitive=False),
    chunk_size: int = typer.Option(1200),
    chunk_overlap: int = typer.Option(100),
):

    ######### Start of creation of various objects/dependencies #############

    # Dataloader that loads all the text files from
    # the supplied directory
    data_loader = DirectoryLoader(input_dir, glob="*.txt")

    # TextSplitter required by TextUnitExtractor
    text_splitter = TokenTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )

    # TextUnitExtractor that extracts text units from the text files
    text_unit_extractor = TextUnitExtractor(text_splitter=text_splitter)

    # Prompt Builder for Entity Extraction
    er_extraction_prompt = prompts_dir / "entity_extraction.txt"
    er_prompt_builder = er.DefaultEntityExtractionPromptBuilder(er_extraction_prompt)

    # LLM
    er_llm = make_llm_instance(llm_type, llm_model, llm_cache_dir)
    # Output Parser
    er_op = er.EntityExtractionOutputParser()
    # Graph Merger
    er_gm = er.GraphsMerger()

    # Entity Extractor
    entity_extractor = er.EntityRelationshipExtractor(
        prompt_builder=er_prompt_builder,
        llm=er_llm,
        output_parser=er_op,
        graphs_merger=er_gm,
    )

    # Prompt Builder for Entity Extraction
    es_extraction_prompt = prompts_dir / "summarize_descriptions.txt"
    es_prompt_builder = es.DefaultSummarizeDescriptionPromptBuilder(
        es_extraction_prompt
    )

    # LLM
    es_llm = make_llm_instance(llm_type, llm_model, llm_cache_dir)

    # Entity Summarizer
    entity_summarizer = es.EntityRelationshipDescriptionSummarizer(
        prompt_builder=es_prompt_builder,
        llm=es_llm,
    )

    # Community Detector
    community_detector = HierarchicalLeidenCommunityDetector()

    ######### End of creation of various objects/dependencies #############

    indexer = Indexer(
        output_dir=output_dir,
        data_loader=data_loader,
        text_unit_extractor=text_unit_extractor,
        er_extractor=entity_extractor,
        er_description_summarizer=entity_summarizer,
        community_detector=community_detector,
    )

    indexer.run()


@app.command()
def query():
    pass


if __name__ == "__main__":
    app()
