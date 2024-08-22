# ruff: noqa: B008
# ruff: noqa: E402

import logging
from pathlib import Path
from typing import cast

import typer
from dotenv import load_dotenv
from typer import Typer

_LOGGER = logging.getLogger("main:query")

# going to do load_dotenv() here
# as OLLAMA_HOST needs to be in the environment
# before the imports below
load_dotenv()

from common import (
    EmbeddingModel,
    EmbeddingModelType,
    LLMModel,
    LLMType,
    get_artifacts_dir_name,
    load_artifacts,
    make_embedding_instance,
    make_llm_instance,
)
from langchain_chroma.vectorstores import Chroma as ChromaVectorStore

from langchain_graphrag.query.global_search import GlobalSearch
from langchain_graphrag.query.global_search.community_weight_calculator import (
    CommunityWeightCalculator,
)
from langchain_graphrag.query.global_search.key_points_aggregator import (
    KeyPointsAggregator,
    KeyPointsAggregatorPromptBuilder,
    KeyPointsContextBuilder,
)
from langchain_graphrag.query.global_search.key_points_generator import (
    CommunityReportContextBuilder,
    KeyPointsGenerator,
    KeyPointsGeneratorPromptBuilder,
)
from langchain_graphrag.query.local_search import (
    LocalSearch,
    LocalSearchPromptBuilder,
    LocalSearchRetriever,
)
from langchain_graphrag.query.local_search.context_builders import (
    ContextBuilder,
)
from langchain_graphrag.query.local_search.context_selectors import (
    ContextSelector,
)
from langchain_graphrag.types.graphs.community import CommunityLevel
from langchain_graphrag.utils import TiktokenCounter

app = Typer()


@app.command()
def global_search(
    output_dir: Path = typer.Option(..., dir_okay=True, file_okay=False),
    cache_dir: Path = typer.Option(..., dir_okay=True, file_okay=False),
    llm_type: LLMType = typer.Option(LLMType.azure_openai, case_sensitive=False),
    llm_model: LLMModel = typer.Option(LLMModel.gpt4o, case_sensitive=False),
    query: str = typer.Option(...),
    level: int = typer.Option(2, help="Community level to search"),
):
    artifacts_dir = output_dir / get_artifacts_dir_name(llm_model)

    _LOGGER.info("Artifacts directory - %s", artifacts_dir)

    artifacts = load_artifacts(artifacts_dir)

    report_context_builder = CommunityReportContextBuilder(
        community_level=cast(CommunityLevel, level),
        weight_calculator=CommunityWeightCalculator(),
        artifacts=artifacts,
        token_counter=TiktokenCounter(),
    )

    kp_generator = KeyPointsGenerator(
        llm=make_llm_instance(llm_type, llm_model, cache_dir),
        prompt_builder=KeyPointsGeneratorPromptBuilder(),
        context_builder=report_context_builder,
    )

    kp_aggregator = KeyPointsAggregator(
        llm=make_llm_instance(llm_type, llm_model, cache_dir),
        prompt_builder=KeyPointsAggregatorPromptBuilder(),
        context_builder=KeyPointsContextBuilder(
            token_counter=TiktokenCounter(),
        ),
    )

    global_search = GlobalSearch(
        kp_generator=kp_generator,
        kp_aggregator=kp_aggregator,
    )

    # A synchronous invoke
    # response = global_search.invoke(query)
    # print(response)

    # A streaming invoke
    for chunk in global_search.stream(query):
        print(chunk, end="", flush=True)


@app.command()
def local_search(
    output_dir: Path = typer.Option(..., dir_okay=True, file_okay=False),
    cache_dir: Path = typer.Option(..., dir_okay=True, file_okay=False),
    llm_type: LLMType = typer.Option(LLMType.azure_openai, case_sensitive=False),
    llm_model: LLMModel = typer.Option(LLMModel.gpt4o, case_sensitive=False),
    query: str = typer.Option(...),
    level: int = typer.Option(2, help="Community level to search"),
    embedding_type: EmbeddingModelType = typer.Option(
        EmbeddingModelType.azure_openai, case_sensitive=False
    ),
    embedding_model: EmbeddingModel = typer.Option(
        EmbeddingModel.text_embedding_3_small, case_sensitive=False
    ),
):
    vector_store_dir = output_dir / "vector_stores"
    artifacts_dir = output_dir / get_artifacts_dir_name(llm_model)

    _LOGGER.info("Vector store directory - %s", vector_store_dir)
    _LOGGER.info("Artifacts directory - %s", artifacts_dir)

    # Reload the vector Store that stores
    # the entity name & description embeddings
    entities_collection_name = f"entity-{embedding_model.name}"
    _LOGGER.info("[Vector Store] Entities Collection - %s", entities_collection_name)
    entities_vector_store = ChromaVectorStore(
        collection_name=entities_collection_name,
        persist_directory=str(vector_store_dir),
        embedding_function=make_embedding_instance(
            embedding_type=embedding_type,
            embedding_model=embedding_model,
            cache_dir=cache_dir,
        ),
    )

    # Build the Context Selector using the default
    # components; You can supply the various components
    # and achieve as much extensibility as you want
    # Below builds the one using default components.
    context_selector = ContextSelector.build_default(
        entities_vector_store=entities_vector_store,
        entities_top_k=10,
        community_level=cast(CommunityLevel, level),
    )

    # Context Builder is responsible for taking the
    # result of Context Selector & building the
    # actual context to be inserted into the prompt
    # Keeping these two separate further increases
    # extensibility & maintainability
    context_builder = ContextBuilder.build_default(
        token_counter=TiktokenCounter(),
    )

    # load the artifacts
    artifacts = load_artifacts(artifacts_dir)

    # Make a langchain retriever that relies on
    # context selection & builder
    retriever = LocalSearchRetriever(
        context_selector=context_selector,
        context_builder=context_builder,
        artifacts=artifacts,
    )

    local_search = LocalSearch(
        prompt_builder=LocalSearchPromptBuilder(),
        llm=make_llm_instance(llm_type, llm_model, cache_dir),
        retriever=retriever,
    )

    # get the chain
    search_chain = local_search()

    # you could invoke
    # print(search_chain.invoke(query))

    # or, you could stream
    for chunk in search_chain.stream(query):
        print(chunk, end="", flush=True)
