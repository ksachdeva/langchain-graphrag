from pathlib import Path

import pandas as pd
from tqdm import tqdm

from langchain_core.document_loaders.base import BaseLoader

from .text_unit_extractor import TextUnitExtractor
from .entity_extraction import EntityRelationshipExtractor

FILE_NAME_BASE_TEXT_UNITS = "create_base_text_units.parquet"


class Indexer:
    def __init__(
        self,
        output_dir: Path | str,
        data_loader: BaseLoader,
        text_unit_extractor: TextUnitExtractor,
        entity_relationship_extractor: EntityRelationshipExtractor,
    ):
        self._output_dir = (
            output_dir if isinstance(output_dir, Path) else Path(output_dir)
        )
        self._data_loader = data_loader
        self._text_unit_extractor = text_unit_extractor
        self._entity_relationship_extractor = entity_relationship_extractor

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

    def _create_entity_relationships(self, text_units_df: pd.DataFrame):
        graph = self._entity_relationship_extractor.invoke(text_units_df)
        print(graph)
        return graph

    def run(self):
        # Step 1
        text_units_df = self._create_text_units()
        # Step 2
        entity_df = self._create_entity_relationships(text_units_df)
