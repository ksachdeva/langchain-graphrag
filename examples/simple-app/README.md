# Simple app

This app shows how you would create various components from `langchain_graphrag` and use them to create a simple app.

The `cli` uses `typer` to create a command line interface.

## ⚠️ Important Notes

### Troubleshooting Common Issues

#### **Warning: Failed to hardlink files; falling back to full copy**

If you encounter this warning, you can fix it by setting the UV link mode:

```powershell
# For PowerShell (Windows)
$env:UV_LINK_MODE = "copy"
```

```bash
# For bash/zsh (Linux/macOS)
export UV_LINK_MODE=copy
```

#### **OneDrive Sync Issues**

Make sure your project is located **outside of OneDrive** (or any other cloud sync folder) as it can cause various errors due to file synchronization conflicts during the build and execution process.

> **Note**: This example has been updated to use `uv` instead of `rye`. All commands now use `uv run` and task management via `poe`.

## Install

At the root of the repo, install all dependencies:

```bash
# setup environment and install dependencies
uv sync
```

## Run

**Note**:

Make sure to rename `.env.example` with `.env` if you are using OpenAI or AzureOpenAI
and fill in the necessary environment variables.

```bash
# assuming you are at the root of the repo
uv run python examples/simple-app/app/main.py --help

(or)

uv run poe simple-app-help
```


### Examples

```bash
# Step 1 - Index (run from the root of the repository)
uv run python examples/simple-app/app/main.py indexer index --input-file examples/input-data/book.txt --output-dir tmp --cache-dir tmp/cache --llm-type azure_openai --llm-model gpt-4o --embedding-type azure_openai --embedding-model text-embedding-3-large

(or) 

uv run poe simple-app-indexer --input-file examples/input-data/book.txt --output-dir tmp --cache-dir tmp/cache --llm-type azure_openai --llm-model gpt-4o --embedding-type azure_openai --embedding-model text-embedding-3-large

(or)

uv run poe simple-app-indexer-azure
```

```bash
# Step 2 - Global Search (run from the root of the repository)
uv run poe simple-app-global-search --output-dir tmp --cache-dir tmp/cache --llm-type azure_openai --llm-model gpt-4o --query "What are the top themes in this story?"

(or) 

uv run poe simple-app-global-search-azure --query "What are the top themes in this story?"
```

```bash
# Step 3 - Local Search (run from the root of the repository)
uv run poe simple-app-local-search --output-dir tmp --cache-dir tmp/cache --llm-type azure_openai --llm-model gpt-4o --embedding-type azure_openai --embedding-model text-embedding-3-large  --query "Who is Scrooge, and what are his main relationships?"

(or) 

uv run poe simple-app-local-search-azure --query "Who is Scrooge, and what are his main relationships?"
```

### Quick commands (poe tasks)

For convenience, several poe tasks are available (from `pyproject.toml`):

```bash
# Help
uv run poe simple-app-help           # Main help
uv run poe simple-app-query-help     # Query-specific help

# Indexing (choose your provider)
uv run poe simple-app-indexer-azure    # Azure OpenAI (recommended)
uv run poe simple-app-indexer-openai   # OpenAI
uv run poe simple-app-indexer-ollama   # Ollama (local)

# Searching (after indexing)
uv run poe simple-app-global-search-azure --query "What are the themes?"
uv run poe simple-app-local-search-azure --query "Who are the characters?"

# Reports  
uv run poe simple-app-report         # Generate reports (uses tmp/artifacts_gpt-4o)
```
### Additional options

```bash
# Base commands (with minimal required args - you can add more)
uv run poe simple-app-indexer        # Custom indexing (add your own args)
uv run poe simple-app-local-search --query "your question"   # Basic local search
uv run poe simple-app-global-search --query "your question"  # Basic global search

# Example with custom args
uv run poe simple-app-indexer --input-file your-file.txt --output-dir output --llm-type openai --llm-model gpt-4o-mini

# Note: Basic search commands require you to specify --llm-type and --llm-model  
# Use the -azure versions for pre-configured commands

# Development helpers (from root directory)
uv run poe test                      # Run tests
uv run poe lint                      # Check code quality
uv run poe docs-serve                # View docs locally
```
