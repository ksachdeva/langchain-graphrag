# Simple App

This app shows how you would create various components from `langchain_graphrag` and use them to create a simple app.

The CLI uses `typer` to create a command line interface.

## Install

At the root of the repository, install all dependencies:

```bash
uv sync
```

## Setup

Copy `.env.example` to `.env` and fill in your API keys and choose your provider:

```bash
cp examples/simple-app/.env.example examples/simple-app/.env
```

Edit `.env` to set your provider:

```bash
# Provider — pick one: openai | azure_openai | ollama
LLM_TYPE=openai
LLM_MODEL=gpt-4o
EMBEDDING_TYPE=openai
EMBEDDING_MODEL=text-embedding-3-small
```

All poe tasks read provider config from this `.env` file — to switch providers, just edit it.

## Usage

### Help Commands

```bash
uv run poe app-help        # Main help
uv run poe indexer-help    # Indexer help
uv run poe query-help      # Query help
```

### Step 1 - Indexing

```bash
uv run poe index
```

### Step 2 - Global Search

```bash
uv run poe global-search --query "What are the main themes in this story?"
```

### Step 3 - Local Search

```bash
uv run poe local-search --query "Who is Scrooge, and what are his main relationships?"
```

### Generate Reports

```bash
uv run poe report
```

### Development Commands

```bash
uv run poe test        # Run tests
uv run poe lint        # Check code quality
uv run poe docs-serve  # View documentation locally
```

## Notes

- All commands should be run from the root of the repository
- Make sure to index your data before running search queries
- Use your own queries by replacing the `--query` parameter
