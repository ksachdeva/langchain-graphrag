from pathlib import Path

import pandas as pd
import networkx as nx
from tqdm import tqdm

from langchain_core.document_loaders.base import BaseLoader

from .text_unit_extractor import TextUnitExtractor
from .entity_extraction import EntityRelationshipExtractor
from .entity_summarization import EntityRelationshipDescriptionSummarizer
from .graph_clustering import HierarchicalLeidenCommunityDetector

FILE_NAME_BASE_TEXT_UNITS = "create_base_text_units.parquet"


class Indexer:
    def __init__(
        self,
        output_dir: Path | str,
        data_loader: BaseLoader,
        text_unit_extractor: TextUnitExtractor,
        er_extractor: EntityRelationshipExtractor,
        er_description_summarizer: EntityRelationshipDescriptionSummarizer,
        community_detector: HierarchicalLeidenCommunityDetector,
    ):
        self._output_dir = (
            output_dir if isinstance(output_dir, Path) else Path(output_dir)
        )
        self._data_loader = data_loader
        self._text_unit_extractor = text_unit_extractor
        self._er_extractor = er_extractor
        self._er_description_summarizer = er_description_summarizer
        self._community_detector = community_detector

    def _create_text_units(self) -> pd.DataFrame:
        self._output_dir.mkdir(parents=True, exist_ok=True)
        text_units_df_path = self._output_dir / FILE_NAME_BASE_TEXT_UNITS
        if text_units_df_path.exists():
            return pd.read_parquet(text_units_df_path)

        all_text_units = []
        for d in tqdm(self._data_loader.load()):
            text_units = self._text_unit_extractor.run(d)
            all_text_units.extend(text_units)

        df = pd.DataFrame.from_dict(all_text_units)
        df.to_parquet(text_units_df_path)
        return df

    def run(self):
        # Step 1 - Text Unit extraction
        text_units_df = self._create_text_units()
        # Step 2 - ER extraction & Graph creation
        er_graph = self._er_extractor.invoke(text_units_df)
        # Step 3 - Summarize descriptions in Graph
        er_graph_summarized = self._er_description_summarizer.invoke(er_graph)
        # Step 4 - Detect communities in Graph
        self._community_detector.run(er_graph_summarized)