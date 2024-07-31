from pathlib import Path

from langchain_core.document_loaders.base import BaseLoader

from .text_unit_extractor import TextUnitExtractor
from .entity_extraction import EntityRelationshipExtractor
from .entity_summarization import EntityRelationshipDescriptionSummarizer

from .graph_clustering import HierarchicalLeidenCommunityDetector

from .table_generation import EntitiesTableGenerator
from .table_generation import CommunitiesTableGenerator
from .table_generation import RelationshipsTableGenerator
from .table_generation import TextUnitsTableGenerator


class Indexer:
    def __init__(
        self,
        output_dir: Path | str,
        data_loader: BaseLoader,
        text_unit_extractor: TextUnitExtractor,
        er_extractor: EntityRelationshipExtractor,
        er_description_summarizer: EntityRelationshipDescriptionSummarizer,
        community_detector: HierarchicalLeidenCommunityDetector,
        entities_table_generator: EntitiesTableGenerator,
        relationships_table_generator: RelationshipsTableGenerator,
        communities_table_generator: CommunitiesTableGenerator,
        text_units_table_generator: TextUnitsTableGenerator,
    ):
        self._output_dir = (
            output_dir if isinstance(output_dir, Path) else Path(output_dir)
        )
        self._data_loader = data_loader
        self._text_unit_extractor = text_unit_extractor
        self._er_extractor = er_extractor
        self._er_description_summarizer = er_description_summarizer
        self._community_detector = community_detector
        self._entities_table_generator = entities_table_generator
        self._relationships_table_generator = relationships_table_generator
        self._communities_table_generator = communities_table_generator
        self._text_units_table_generator = text_units_table_generator

    def run(self):

        # Step 0 - For now only 1 document is supported
        document = self._data_loader.load()[0]

        # Step 1 - Text Unit extraction
        df_base_text_units = self._text_unit_extractor.run(document)
        # Step 2 - ER extraction & Graph creation
        er_graph = self._er_extractor.invoke(df_base_text_units)
        # Step 3 - Summarize descriptions in Graph
        er_graph_summarized = self._er_description_summarizer.invoke(er_graph)
        # Step 4 - Detect communities in Graph
        clustered_graphs = self._community_detector.run(er_graph_summarized)

        # Step 5 - Final Entities generation (depends on Step 3)
        df_final_entities = self._entities_table_generator.run(er_graph_summarized)

        # Step 6 - Final Entities generation (depends on Step 3)
        df_final_relationships = self._relationships_table_generator.run(
            er_graph_summarized
        )

        # Step 7 - Final Text Units generation
        df_final_text_units = self._text_units_table_generator.run(
            df_base_text_units,
            df_final_entities,
            df_final_relationships,
        )

        # Step 8 - Final Communities generation (depends on Step 4)
        df_final_communities = self._communities_table_generator.run(clustered_graphs)
