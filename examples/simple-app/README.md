# Simple app

This app shows how you would create various components from `langchain_graphrag` and use them to create a simple app.

The `cli` uses `typer` to create a command line interface.

## Install

```bash
pip install -r requirements.txt
```

## Run

Make sure the `langchain_graphrag` in your PYTHONPATH

```bash
# assuming you are at the root of the repo
python examples/simple-app/app/main.py --help
```

```bash
# assuming you are at the root of the repo
python examples/simple-app/app/main.py indexer --input-dir examples/input-data --output-dir temp --prompts-dir examples/prompts --llm-cache-dir temp/cache
```