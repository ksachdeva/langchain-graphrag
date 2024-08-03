# Simple app

This app shows how you would create various components from `langchain_graphrag` and use them to create a simple app.

The `cli` uses `typer` to create a command line interface.

## Install

Normally `rye sync` at the root of the repo will install all the dependenceis

## Run

```bash
# assuming you are at the root of the repo
python examples/simple-app/app/main.py --help
```

```bash
# assuming you are at the root of the repo
python examples/simple-app/app/main.py indexer --input-dir examples/input-data --output-dir temp --prompts-dir examples/prompts --cache-dir temp/cache
```
Or, you can run it via `rye`. The below command can take additional args of simple-app

```bash
rye run simple-app
```