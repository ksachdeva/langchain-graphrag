from typing import Iterator

from langchain_core.runnables import Runnable, RunnablePassthrough

from .key_points_aggregator import KeyPointsAggregator
from .key_points_generator import KeyPointsGenerator


class GlobalSearch:
    def __init__(
        self,
        kp_generator: KeyPointsGenerator,
        kp_aggregator: KeyPointsAggregator,
    ):
        self._kp_generator = kp_generator
        self._kp_aggregator = kp_aggregator

    def invoke(self, query: str) -> str:
        generation_chain = self._kp_generator()
        aggregation_chain = self._kp_aggregator()

        response = generation_chain.invoke(query)

        return aggregation_chain.invoke(
            input=dict(report_data=response, global_query=query)
        )

    def stream(self, query: str) -> Iterator:
        generation_chain = self._kp_generator()
        aggregation_chain = self._kp_aggregator()

        response = generation_chain.invoke(query)

        return aggregation_chain.stream(
            input=dict(report_data=response, global_query=query)
        )
