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
from langchain_core.output_parsers.string import StrOutputParser
from langchain_graphrag.query.global_search import GlobalSearch
from langchain_graphrag.query.global_search.community_weight_calculator import (
    CommunityWeightCalculator,
)
from langchain_graphrag.query.global_search.key_points_aggregator import (
    KeyPointsAggregator,
)
from langchain_graphrag.query.global_search.key_points_generator import (
    KeyPointsGenerator,
)
from langchain_graphrag.query.local_search import (
    LocalSearch,
    LocalSearchPromptBuilder,
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

    points_generator = KeyPointsGenerator.build_default(
        llm=make_llm_instance(llm_type, llm_model, cache_dir)
    )

    points_aggregator = KeyPointsAggregator.build_default(
        llm=make_llm_instance(llm_type, llm_model, cache_dir)
    )

    searcher = GlobalSearch(
        community_level=cast(CommunityLevel, level),
        weight_calculator=CommunityWeightCalculator(),
        key_points_generator=points_generator,
        key_points_aggregator=points_aggregator,
    )

    artifacts = load_artifacts(artifacts_dir)
    response = searcher.invoke(query, artifacts)

    print(response)


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

    searcher = LocalSearch(
        prompt_builder=LocalSearchPromptBuilder(),
        llm=make_llm_instance(llm_type, llm_model, cache_dir),
        output_parser=StrOutputParser(),
        context_selector=context_selector,
        context_builder=context_builder,
    )

    artifacts = load_artifacts(artifacts_dir)
    response = searcher.invoke(query, artifacts)

    print(response)
