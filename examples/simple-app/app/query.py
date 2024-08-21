# ruff: noqa: B008
# ruff: noqa: E402

from pathlib import Path
from typing import cast

import typer
from dotenv import load_dotenv
from typer import Typer

# going to do load_dotenv() here
# as OLLAMA_HOST needs to be in the environment
# before the imports below
load_dotenv()

from common import (
    EmbeddingModel,
    EmbeddingModelType,
    LLMModel,
    LLMType,
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
    LocalSearchPromptBuilder,
    LocalSearchRetriever,
    make_local_search_chain,
)
from langchain_graphrag.query.local_search.context_builders import (
    CommunitiesReportsContextBuilder,
    ContextBuilder,
    EntitiesContextBuilder,
    RelationshipsContextBuilder,
    TextUnitsContextBuilder,
)
from langchain_graphrag.query.local_search.context_selectors import (
    CommunitiesReportsSelector,
    ContextSelector,
    EntitiesSelector,
    RelationshipsSelector,
    TextUnitsSelector,
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
    artifacts_dir = output_dir / "artifacts"

    artifacts = load_artifacts(artifacts_dir)

    report_context_builder = CommunityReportContextBuilder(
        community_level=cast(CommunityLevel, level),
        weight_calculator=CommunityWeightCalculator(),
        artifacts=artifacts,
    )

    kp_generator = KeyPointsGenerator(
        llm=make_llm_instance(llm_type, llm_model, cache_dir),
        prompt_builder=KeyPointsGeneratorPromptBuilder(),
        context_builder=report_context_builder,
    )

    kp_aggregator = KeyPointsAggregator(
        llm=make_llm_instance(llm_type, llm_model, cache_dir),
        prompt_builder=KeyPointsAggregatorPromptBuilder(),
        context_builder=KeyPointsContextBuilder(),
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
    artifacts_dir = output_dir / "artifacts"

    entities_vector_store = ChromaVectorStore(
        collection_name="entity_name_description",
        persist_directory=str(vector_store_dir),
        embedding_function=make_embedding_instance(
            embedding_type=embedding_type,
            embedding_model=embedding_model,
            cache_dir=cache_dir,
        ),
    )

    entities_selector = EntitiesSelector(vector_store=entities_vector_store, top_k=10)

    context_selector = ContextSelector(
        entities_selector=entities_selector,
        text_units_selector=TextUnitsSelector(),
        relationships_selector=RelationshipsSelector(),
        communities_reports_selector=CommunitiesReportsSelector(
            cast(CommunityLevel, level)
        ),
    )

    token_counter = TiktokenCounter()

    context_builder = ContextBuilder(
        entities_context_builder=EntitiesContextBuilder(token_counter=token_counter),
        realtionships_context_builder=RelationshipsContextBuilder(
            token_counter=token_counter
        ),
        text_units_context_builder=TextUnitsContextBuilder(token_counter=token_counter),
        communities_reports_context_builder=CommunitiesReportsContextBuilder(
            token_counter=token_counter
        ),
    )

    artifacts = load_artifacts(artifacts_dir)

    retriever = LocalSearchRetriever(
        context_selector=context_selector,
        context_builder=context_builder,
        artifacts=artifacts,
    )

    search_chain = make_local_search_chain(
        prompt_builder=LocalSearchPromptBuilder(),
        llm=make_llm_instance(llm_type, llm_model, cache_dir),
        retriever=retriever,
    )

    # you could invoke
    # print(search_chain.invoke(query))

    # or, you could stream
    for chunk in search_chain.stream(query):
        print(chunk, end="", flush=True)
