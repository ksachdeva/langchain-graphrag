# ruff: noqa: B008

from pathlib import Path

import typer
from dotenv import load_dotenv
from typer import Typer

# going to do load_dotenv() here
# as OLLAMA_HOST needs to be in the environment
# before the imports below
load_dotenv()

from common import (
    LLMModel,
    LLMType,
    make_llm_instance,
)
from langchain_core.output_parsers.string import StrOutputParser
from langchain_graphrag.query.global_search import GlobalQuerySearch
from langchain_graphrag.query.global_search.community_weight_calculator import (
    CommunityWeightCalculator,
)
from langchain_graphrag.query.global_search.key_points_aggregator import (
    DefaultAggregatorPromptBuilder,
    KeyPointsAggregator,
)
from langchain_graphrag.query.global_search.key_points_generator import (
    DefaultKeyPointsGeneratorPromptBuilder,
    KeyPointsGenerator,
    KeyPointsOutputParser,
)

app = Typer()


@app.command()
def global_search(  # noqa: PLR0913
    output_dir: Path = typer.Option(..., dir_okay=True, file_okay=False),
    cache_dir: Path = typer.Option(..., dir_okay=True, file_okay=False),
    llm_type: LLMType = typer.Option(LLMType.azure_openai, case_sensitive=False),
    llm_model: LLMModel = typer.Option(LLMModel.gpt4o, case_sensitive=False),
    query: str = typer.Option(...),
    level: int = typer.Option(2, help="Community level to search"),
):
    points_generator = KeyPointsGenerator(
        prompt_builder=DefaultKeyPointsGeneratorPromptBuilder(),
        llm=make_llm_instance(llm_type, llm_model, cache_dir),
        output_parser=KeyPointsOutputParser(),
    )

    points_aggregator = KeyPointsAggregator(
        prompt_builder=DefaultAggregatorPromptBuilder(),
        llm=make_llm_instance(llm_type, llm_model, cache_dir),
        output_parser=StrOutputParser(),
    )

    searcher = GlobalQuerySearch(
        artifacts_dir=output_dir / "artifacts",
        community_level=level,
        weight_calculator=CommunityWeightCalculator(),
        key_points_generator=points_generator,
        key_points_aggregator=points_aggregator,
    )

    response = searcher.invoke(query)

    print(response)
