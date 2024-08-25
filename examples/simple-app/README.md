# Simple app

This app shows how you would create various components from `langchain_graphrag` and use them to create a simple app.

The `cli` uses `typer` to create a command line interface.

## Install

Normally `rye sync` at the root of the repo will install all the dependenceis

## Run

**Note**:

Make sure to rename `.env.example` with `.env` if you are using OpenAI or AzureOpenAI
and fill in the necessary environment variables.

```bash
# assuming you are at the root of the repo
rye run python examples/simple-app/app/main.py --help
```

```bash
# assuming you are at the root of the repo
rye run python examples/simple-app/app/main.py indexer --input-file examples/input-data/book.txt --output-dir temp --cache-dir temp/cache
```
Or, you can run it via `rye`. The below command can take additional args of simple-app

```bash
# Step 1 - Index
# make sure to run this from the root of the repository
rye run simple-app-indexer
```

```bash
# Step 2 - Global Search
# make sure to run this from the root of the repository
rye run simple-app-global-search --query "What are the top themes in this story?"
```

```bash
# Step 3 - Local Search
# make sure to run this from the root of the repository
rye run simple-app-local-search --query "Who is Scrooge, and what are his main relationships?"
```
