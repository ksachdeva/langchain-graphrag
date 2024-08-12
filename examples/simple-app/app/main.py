import logging

from indexer import app as indexer_app
from query import app as query_app
from typer import Typer

app = Typer()
app.add_typer(indexer_app, name="indexer")
app.add_typer(query_app, name="query")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("gensim").setLevel(logging.WARNING)
    logging.getLogger("langchain_graphrag").setLevel(logging.INFO)
    app()
