# ruff: noqa: B008
# ruff: noqa: E402
# ruff: noqa: ERA001

import logging
from pathlib import Path

import typer
from dotenv import load_dotenv
from typer import Typer

_LOGGER = logging.getLogger("main:indexer")

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
    save_artifacts,
)
from langchain_chroma.vectorstores import Chroma as ChromaVectorStore
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import TokenTextSplitter

from langchain_graphrag.indexing import SimpleIndexer, TextUnitExtractor
from langchain_graphrag.indexing.artifacts import IndexerArtifacts
from langchain_graphrag.indexing.artifacts_generation import (
    CommunitiesReportsArtifactsGenerator,
    EntitiesArtifactsGenerator,
    RelationshipsArtifactsGenerator,
    TextUnitsArtifactsGenerator,
)
from langchain_graphrag.indexing.embedding_generation.graph import (
    Node2VectorGraphEmbeddingGenerator,  # noqa: F401
)
from langchain_graphrag.indexing.graph_clustering.leiden_community_detector import (
    HierarchicalLeidenCommunityDetector,
)
from langchain_graphrag.indexing.graph_generation import (
    EntityRelationshipDescriptionSummarizer,
    EntityRelationshipExtractor,
    GraphGenerator,
    GraphsMerger,
)
from langchain_graphrag.indexing.report_generation import (
    CommunityReportGenerator,
    CommunityReportWriter,
)

app = Typer()


@app.command()
def index(
    input_file: Path = typer.Option(..., dir_okay=False, file_okay=True),
    output_dir: Path = typer.Option(..., dir_okay=True, file_okay=False),
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
    vector_store_dir = output_dir / "vector_stores"
    artifacts_dir = output_dir / get_artifacts_dir_name(llm_model)

    _LOGGER.info("Input file - %s", input_file)
    _LOGGER.info("Output directory - %s", output_dir)
    _LOGGER.info("Cache directory - %s", cache_dir)
    _LOGGER.info("Vector store directory - %s", vector_store_dir)
    _LOGGER.info("Artifacts directory - %s", artifacts_dir)

    ######### Start of creation of various objects/dependencies #############

    # Dataloader that loads all the text files from
    # the supplied directory
    documents = TextLoader(file_path=input_file).load()

    # TextSplitter required by TextUnitExtractor
    text_splitter = TokenTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )

    # TextUnitExtractor that extracts text units from the text files
    text_unit_extractor = TextUnitExtractor(text_splitter=text_splitter)

    # Entity Relationship Extractor
    entity_extractor = EntityRelationshipExtractor.build_default(
        llm=make_llm_instance(llm_type, llm_model, cache_dir)
    )

    # Entity Relationship Description Summarizer
    entity_summarizer = EntityRelationshipDescriptionSummarizer.build_default(
        llm=make_llm_instance(llm_type, llm_model, cache_dir)
    )

    # Graph Generator
    graph_generator = GraphGenerator(
        er_extractor=entity_extractor,
        graphs_merger=GraphsMerger(),
        er_description_summarizer=entity_summarizer,
    )

    # Community Detector
    community_detector = HierarchicalLeidenCommunityDetector()

    # Entities artifacts Generator
    # We need the vector Store (mandatory) for entities

    # let's create a collection name based on
    # the embedding model name
    entities_collection_name = f"entity-{embedding_model.name}"
    entities_vector_store = ChromaVectorStore(
        collection_name=entities_collection_name,
        persist_directory=str(vector_store_dir),
        embedding_function=make_embedding_instance(
            embedding_type=embedding_type,
            embedding_model=embedding_model,
            cache_dir=cache_dir,
        ),
    )
    # Graph Embedding Generator (Optional)
    # Not used in the search implementation but you needed this is
    # how you would create it
    # graph_embedding_generator = Node2VectorGraphEmbeddingGenerator()
    graph_embedding_generator = None
    entities_artifacts_generator = EntitiesArtifactsGenerator(
        entities_vector_store=entities_vector_store,  # mandatory
        graph_embedding_generator=graph_embedding_generator,  # optional
    )

    # Relationships artifacts Generator
    # VectorStore for relationships is optional
    # Below is an example if you needed one
    # relationships_collection_name = f"relationship-{embedding_model.name}"
    # relationships_vector_store = ChromaVectorStore(
    #     collection_name=relationships_collection_name,
    #     persist_directory=str(output_dir / "vector_stores"),
    #     embedding_function=make_embedding_instance(
    #         embedding_type=embedding_type,
    #         embedding_model=embedding_model,
    #         cache_dir=cache_dir,
    #     ),
    # )
    # Since the search implementation does not use it
    # we pass None
    relationships_vector_store = None
    relationships_artifacts_generator = RelationshipsArtifactsGenerator(
        relationships_vector_store=relationships_vector_store
    )

    # Community Report Generator
    report_gen_llm = make_llm_instance(llm_type, llm_model, cache_dir)
    report_generator = CommunityReportGenerator.build_default(llm=report_gen_llm)

    report_writer = CommunityReportWriter()

    communities_report_artifacts_generator = CommunitiesReportsArtifactsGenerator(
        report_generator=report_generator,
        report_writer=report_writer,
    )

    # TextUnits Artifacts Generator
    # The vector store for text units embedding is optional
    # Below is an example of how you would create it
    # text_units_collection_name = f"text_units-{embedding_model.name}"
    # text_units_vector_store = ChromaVectorStore(
    #     collection_name=text_units_collection_name,
    #     persist_directory=str(output_dir / "vector_stores"),
    #     embedding_function=make_embedding_instance(
    #         embedding_type=embedding_type,
    #         embedding_model=embedding_model,
    #         cache_dir=cache_dir,
    #     ),
    # )
    # Since the search implementation does not use it
    # we pass None
    text_units_vector_store = None
    text_units_artifacts_generator = TextUnitsArtifactsGenerator(
        vector_store=text_units_vector_store,
    )

    ######### End of creation of various objects/dependencies #############

    indexer = SimpleIndexer(
        text_unit_extractor=text_unit_extractor,
        graph_generator=graph_generator,
        community_detector=community_detector,
        entities_artifacts_generator=entities_artifacts_generator,
        relationships_artifacts_generator=relationships_artifacts_generator,
        text_units_artifacts_generator=text_units_artifacts_generator,
        communities_report_artifacts_generator=communities_report_artifacts_generator,
    )

    artifacts = indexer.run(documents)

    # save the artifacts
    # we would append the llm model
    # name in the artifacts directory
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    save_artifacts(artifacts, artifacts_dir)

    artifacts.report()


@app.command()
def report(
    artifacts_dir: Path = typer.Option(
        ...,
        dir_okay=True,
        file_okay=False,
    ),
):
    _LOGGER.info("Artifacts directory - %s", artifacts_dir)

    artifacts: IndexerArtifacts = load_artifacts(artifacts_dir)
    artifacts.report()
