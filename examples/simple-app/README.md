# Simple App

This app shows how you would create various components from `langchain_graphrag` and use them to create a simple app.

The CLI uses `typer` to create a command line interface.

## Install

At the root of the repository, install all dependencies:

```bash
uv sync
```

## Setup

**Note**: Make sure to rename `.env.example` to `.env` if you are using OpenAI or AzureOpenAI and fill in the necessary environment variables.

## Usage

### Help Commands

```bash
# Main help
uv run poe simple-app-help

# Indexer help  
uv run poe simple-app-indexer-help

# Query help
uv run poe simple-app-query-help
```

### Step 1 - Indexing

```bash
# Azure OpenAI (recommended)
uv run poe simple-app-indexer-azure

# OpenAI
uv run poe simple-app-indexer-openai

# Ollama (local)
uv run poe simple-app-indexer-ollama
```

### Step 2 - Global Search

```bash
# Azure OpenAI
uv run poe simple-app-global-search-azure --query "What are the main themes in this story?"

# OpenAI
uv run poe simple-app-global-search-openai --query "What are the main themes in this story?"

# Ollama
uv run poe simple-app-global-search-ollama --query "What are the main themes in this story?"
```

### Step 3 - Local Search

```bash
# Azure OpenAI
uv run poe simple-app-local-search-azure --query "Who is Scrooge, and what are his main relationships?"

# OpenAI
uv run poe simple-app-local-search-openai --query "Who is Scrooge, and what are his main relationships?"

# Ollama
uv run poe simple-app-local-search-ollama --query "Who is Scrooge, and what are his main relationships?"
```

### Generate Reports

```bash
# Generate reports
uv run poe simple-app-report
```

### Development Commands

```bash
# Run tests
uv run poe test

# Check code quality
uv run poe lint

# View documentation locally
uv run poe docs-serve
```

## Notes

- All commands should be run from the root of the repository
- Azure OpenAI is recommended for best results
- Make sure to index your data before running search queries
- Use your own queries by replacing the `--query` parameter
