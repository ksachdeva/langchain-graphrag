# ruff: noqa: B008

from pathlib import Path

import typer
from dotenv import load_dotenv
from typer import Typer

# going to do load_dotenv() here
# as OLLAMA_HOST needs to be in the environment
# before the imports below
load_dotenv()

import langchain_graphrag.indexing.graph_generation.entity_relationship_extraction as er
import langchain_graphrag.indexing.graph_generation.entity_relationship_summarization as es  # noqa: E501
from common import (
    EmbeddingModel,
    EmbeddingModelType,
    LLMModel,
    LLMType,
    make_embedding_instance,
    make_llm_instance,
)
from langchain_chroma.vectorstores import Chroma as ChromaVectorStore
from langchain_community.document_loaders.directory import DirectoryLoader
from langchain_core.output_parsers.string import StrOutputParser
from langchain_graphrag.indexing.artifacts import IndexerArtifacts
from langchain_graphrag.indexing.embedding_generation.graph import (
    Node2VectorGraphEmbeddingGenerator,
)
from langchain_graphrag.indexing.graph_clustering.leiden_community_detector import (
    HierarchicalLeidenCommunityDetector,
)
from langchain_graphrag.indexing.graph_generation.generator import GraphGenerator
from langchain_graphrag.indexing.indexer import Indexer
from langchain_graphrag.indexing.report_generation import (
    CommunityReportGenerator,
    CommunityReportOutputParser,
    CommunityReportWriter,
    DefaulReportGenerationPromptBuilder,
)
from langchain_graphrag.indexing.table_generation import (
    CommunitiesReportsTableGenerator,
    CommunitiesTableGenerator,
    EntitiesTableGenerator,
    RelationshipsTableGenerator,
    TextUnitsTableGenerator,
)
from langchain_graphrag.indexing.text_unit_extractor import TextUnitExtractor
from langchain_text_splitters import TokenTextSplitter

app = Typer()


@app.command()
def index(  # noqa: PLR0913
    input_dir: Path = typer.Option(..., dir_okay=True, file_okay=False),
    output_dir: Path = typer.Option(..., dir_okay=True, file_okay=False),
    prompts_dir: Path = typer.Option(..., dir_okay=True, file_okay=False),
    cache_dir: Path = typer.Option(..., dir_okay=True, file_okay=False),
    llm_type: LLMType = typer.Option(LLMType.azure_openai, case_sensitive=False),
    llm_model: LLMModel = typer.Option(LLMModel.gpt4o, case_sensitive=False),
    embedding_type: EmbeddingModelType = typer.Option(
        EmbeddingModelType.azure_openai, case_sensitive=False
    ),
    embedding_model: EmbeddingModel = typer.Option(
        EmbeddingModel.text_embedding_3_small, case_sensitive=False
    ),
    chunk_size: int = typer.Option(1200),
    chunk_overlap: int = typer.Option(100),
):
    output_dir.mkdir(parents=True, exist_ok=True)
    cache_dir.mkdir(parents=True, exist_ok=True)

    ######### Start of creation of various objects/dependencies #############

    # Dataloader that loads all the text files from
    # the supplied directory
    data_loader = DirectoryLoader(str(input_dir), glob="*.txt")

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
    er_llm = make_llm_instance(llm_type, llm_model, cache_dir)
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
    es_llm = make_llm_instance(llm_type, llm_model, cache_dir)

    # Entity Summarizer
    entity_summarizer = es.EntityRelationshipDescriptionSummarizer(
        prompt_builder=es_prompt_builder, llm=es_llm, output_parser=StrOutputParser()
    )

    # Graph Generator
    graph_generator = GraphGenerator(
        er_extractor=entity_extractor,
        er_description_summarizer=entity_summarizer,
    )

    # Community Detector
    community_detector = HierarchicalLeidenCommunityDetector()

    # Graph Embedding Generator
    graph_embedding_generator = Node2VectorGraphEmbeddingGenerator()

    # Entity Vector Store
    entities_vector_store = ChromaVectorStore(
        collection_name="entity_name_description",
        persist_directory=str(output_dir / "vector_stores"),
        embedding_function=make_embedding_instance(
            embedding_type=embedding_type,
            embedding_model=embedding_model,
            cache_dir=cache_dir,
        ),
    )

    # Relationship Embedding Generator
    relationships_vector_store = ChromaVectorStore(
        collection_name="relationship_description",
        persist_directory=str(output_dir / "vector_stores"),
        embedding_function=make_embedding_instance(
            embedding_type=embedding_type,
            embedding_model=embedding_model,
            cache_dir=cache_dir,
        ),
    )

    # TextUnits vector store
    text_units_vector_store = ChromaVectorStore(
        collection_name="text_units",
        persist_directory=str(output_dir / "vector_stores"),
        embedding_function=make_embedding_instance(
            embedding_type=embedding_type,
            embedding_model=embedding_model,
            cache_dir=cache_dir,
        ),
    )

    # Final Entities Generator
    entities_table_generator = EntitiesTableGenerator(
        entities_vector_store=entities_vector_store,
        graph_embedding_generator=graph_embedding_generator,
    )

    # Final Relationships Generator
    relationships_table_generator = RelationshipsTableGenerator(
        relationships_vector_store=relationships_vector_store
    )

    # Final Communities Generator
    communities_table_generator = CommunitiesTableGenerator()

    # Community Report Generator

    report_gen_llm = make_llm_instance(llm_type, llm_model, cache_dir)

    report_generation_prompt = prompts_dir / "community_report.txt"
    report_prompt_builder = DefaulReportGenerationPromptBuilder(
        prompt_path=report_generation_prompt
    )
    report_generator = CommunityReportGenerator(
        prompt_builder=report_prompt_builder,
        llm=report_gen_llm,
        output_parser=CommunityReportOutputParser(),
    )

    report_writer = CommunityReportWriter()

    communities_report_table_generator = CommunitiesReportsTableGenerator(
        report_generator=report_generator,
        report_writer=report_writer,
    )

    text_units_table_generator = TextUnitsTableGenerator(
        vector_store=text_units_vector_store,
    )

    ######### End of creation of various objects/dependencies #############

    indexer = Indexer(
        data_loader=data_loader,
        text_unit_extractor=text_unit_extractor,
        graph_generator=graph_generator,
        community_detector=community_detector,
        entities_table_generator=entities_table_generator,
        relationships_table_generator=relationships_table_generator,
        communities_table_generator=communities_table_generator,
        text_units_table_generator=text_units_table_generator,
        communities_report_table_generator=communities_report_table_generator,
    )

    artifacts = indexer.run()

    # save the artifacts
    artifacts_dir = output_dir / "artifacts"
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    artifacts.save(artifacts_dir)

    artifacts.report()


@app.command()
def report(
    artifacts_dir: Path = typer.Option(..., dir_okay=True, file_okay=False),
):
    artifacts = IndexerArtifacts.load(artifacts_dir)
    artifacts.report()
