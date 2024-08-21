from langchain_core.documents import Document
from langchain_core.language_models import BaseLLM
from langchain_core.retrievers import BaseRetriever
from langchain_core.runnables import Runnable, RunnablePassthrough

from langchain_graphrag.types.prompts import PromptBuilder


def _format_docs(documents: list[Document]) -> str:
    context_data = [d.page_content for d in documents]
    context_data_str: str = "\n".join(context_data)
    return context_data_str


def make_local_search_chain(
    llm: BaseLLM,
    prompt_builder: PromptBuilder,
    retriever: BaseRetriever,
) -> Runnable:
    prompt, output_parser = prompt_builder.build()

    search_chain: Runnable = (
        {
            "context_data": retriever | _format_docs,
            "local_query": RunnablePassthrough(),
        }
        | prompt
        | llm
        | output_parser
    )

    return search_chain
