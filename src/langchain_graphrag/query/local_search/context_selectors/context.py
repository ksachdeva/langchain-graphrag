from typing import NamedTuple

import pandas as pd

from .entities_selector import EntitiesSelector
from .text_units_selector import TextUnitsSelector


class ContextSelectionResult(NamedTuple):
    entities: pd.DataFrame
    text_units: pd.DataFrame


class ContextSelector:
    def __init__(
        self,
        entities_selector: EntitiesSelector,
        text_units_selector: TextUnitsSelector,
    ):
        self._entities_selector = entities_selector
        self._text_units_selector = text_units_selector

    def run(
        self,
        query: str,
        df_entities: pd.DataFrame,
        df_text_units: pd.DataFrame,
        df_relationships: pd.DataFrame,
    ):
        # Step 1
        # Select the entities to be used in the local search
        df_selected_entities = self._entities_selector.run(query, df_entities)

        # Step 2
        # Select the text units to be used in the local search
        df_selected_text_units = self._text_units_selector.run(
            df_entities=df_selected_entities,
            df_relationships=df_relationships,
            df_text_units=df_text_units,
        )

        return ContextSelectionResult(
            entities=df_selected_entities,
            text_units=df_selected_text_units,
        )
