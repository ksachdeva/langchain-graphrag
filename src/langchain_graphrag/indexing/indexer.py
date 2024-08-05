from pathlib import Path

from langchain_core.document_loaders.base import BaseLoader

from langchain_graphrag.types.graphs.community import CommunityDetector

from .graph_generation import GraphGenerator
from .table_generation import (
    CommunitiesReportsTableGenerator,
    CommunitiesTableGenerator,
    EntitiesTableGenerator,
    RelationshipsTableGenerator,
    TextUnitsTableGenerator,
)
from .text_unit_extractor import TextUnitExtractor


class Indexer:
    def __init__(  # noqa: PLR0913
        self,
        output_dir: Path | str,
        data_loader: BaseLoader,
        text_unit_extractor: TextUnitExtractor,
        graph_generator: GraphGenerator,
        community_detector: CommunityDetector,
        entities_table_generator: EntitiesTableGenerator,
        relationships_table_generator: RelationshipsTableGenerator,
        communities_table_generator: CommunitiesTableGenerator,
        communities_report_table_generator: CommunitiesReportsTableGenerator,
        text_units_table_generator: TextUnitsTableGenerator,
    ):
        self._output_dir = (
            output_dir if isinstance(output_dir, Path) else Path(output_dir)
        )
        self._data_loader = data_loader
        self._text_unit_extractor = text_unit_extractor
        self._graph_generator = graph_generator
        self._community_detector = community_detector
        self._entities_table_generator = entities_table_generator
        self._relationships_table_generator = relationships_table_generator
        self._communities_table_generator = communities_table_generator
        self._communities_report_table_generator = communities_report_table_generator
        self._text_units_table_generator = text_units_table_generator

    def run(self):
        # Step 0 - For now only 1 document is supported
        document = self._data_loader.load()[0]

        # Step 1 - Text Unit extraction
        df_base_text_units = self._text_unit_extractor.run(document)

        # Step 2 - Generate graph
        graph = self._graph_generator.run(df_base_text_units)

        # Step 3 - Detect communities in Graph
        community_detection_result = self._community_detector.run(graph)

        # Step 4 - Reports for detected Communities (depends on Step 2 & Step 3)
        df_community_reports = self._communities_report_table_generator.run(
            community_detection_result,
            graph,
        )

        # Step 5 - Final Entities generation (depends on Step 2)
        df_final_entities = self._entities_table_generator.run(graph)

        # Step 6 - Final Relationships generation (depends on Step 2)
        df_final_relationships = self._relationships_table_generator.run(graph)

        # Step 7 - Final Text Units generation (depends on Steps 1, 5, 6)
        df_final_text_units = self._text_units_table_generator.run(
            df_base_text_units,
            df_final_entities,
            df_final_relationships,
        )
