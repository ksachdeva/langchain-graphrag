import networkx as nx
from langchain_core.language_models import FakeListLLM

from langchain_graphrag.indexing.graph_generation import (
    EntityRelationshipDescriptionSummarizer,
    SummarizeDescriptionPromptBuilder,
)


def test_summarizer():
    llm = FakeListLLM(responses=["fake summary 1", "fake summary 2", "fake summary 3"])
    prompt_builder = SummarizeDescriptionPromptBuilder()
    summarizer = EntityRelationshipDescriptionSummarizer(
        prompt_builder,
        llm,
    )

    graph1 = nx.Graph()
    graph1.add_node("node1", source_id=["1"], description=[" "])
    graph1.add_node(
        "node2",
        source_id=["2"],
        description=["description1 of node 2", "description2 of node 2"],
    )
    graph1.add_node("node3", source_id=["3"], description=["description3"])

    graph1.add_edge(
        "node1",
        "node2",
        source_id=["1"],
        description=["edge description1", "This edge has another description"],
        weight=2,
    )

    graph1_updated = summarizer.invoke(graph1)

    print("\n")
    print(graph1_updated.nodes(data=True))

    print("\n")
    print(graph1_updated.edges(data=True))
