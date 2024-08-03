from typing import cast

import numpy as np
import pandas as pd
from pandas._typing import Suffixes

from tqdm import tqdm

from langchain_core.embeddings import Embeddings


def _array_agg_distinct(series: pd.Series) -> list[pd.Series]:
    return [e for e in series.unique()]


def _make_temporary_frame(
    entities_or_relationships: pd.DataFrame,
    rename_id_to: str,
) -> pd.DataFrame:
    # select only id & text_unit_ids columns
    tmp = entities_or_relationships[["id", "text_unit_ids"]]

    # flatten the text_unit_ids
    tmp = tmp.explode("text_unit_ids")

    # group by text_unit_ids
    grouped = tmp.groupby("text_unit_ids", sort=False)

    aggregations = {"id": _array_agg_distinct}

    output = cast(pd.DataFrame, grouped.agg(aggregations))
    output.rename(columns={"id": rename_id_to}, inplace=True)

    # REVISIT
    # some how it does not change the column name
    # output.rename(columns={"text_unit_ids": "id"}, inplace=True)

    return output.reset_index()


class TextUnitsTableGenerator:
    def __init__(self, embedding_model: Embeddings):
        self._embedding_model = embedding_model

    def run(
        self,
        base_text_units: pd.DataFrame,
        entities: pd.DataFrame,
        relationships: pd.DataFrame,
    ) -> pd.DataFrame:
        entities_df = _make_temporary_frame(
            entities,
            rename_id_to="entity_ids",
        )
        entities_df.rename(columns={"text_unit_ids": "id"}, inplace=True)

        relationships_df = _make_temporary_frame(
            relationships,
            rename_id_to="relationship_ids",
        )
        relationships_df.rename(columns={"text_unit_ids": "id"}, inplace=True)

        text_units_entities = base_text_units.merge(
            entities_df,
            left_on="id",
            right_on="id",
            how="left",
            suffixes=cast(Suffixes, ["_1", "_2"]),
            indicator=True,
        )

        text_units_entities = base_text_units.merge(
            entities_df,
            left_on="id",
            right_on="id",
            how="left",
            suffixes=cast(Suffixes, ["_1", "_2"]),
            indicator=True,
        ).drop("_merge", axis=1)

        text_units = text_units_entities.merge(
            relationships_df,
            left_on="id",
            right_on="id",
            how="left",
            suffixes=cast(Suffixes, ["_1", "_2"]),
            indicator=True,
        ).drop("_merge", axis=1)

        def _run_embedder(series: pd.Series) -> np.ndarray:
            chunk_to_embedd = series["text"]
            document_embeddings = self._embedding_model.embed_documents(
                [chunk_to_embedd]
            )

            return np.array(document_embeddings[0])

        tqdm.pandas(desc="Generating chunk embedding ...")
        chunk_embeddings: list[np.ndarray] = text_units.progress_apply(
            _run_embedder,
            axis=1,
        )

        text_units["text_embedding"] = chunk_embeddings

        return text_units
