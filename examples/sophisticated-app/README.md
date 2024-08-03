# A hydra configuration based app

The purpose of this app is to use `hydra` to easily experiment with different
configurations for e.g. different tokenizers, llms, community detection algorithms etc.

## Install

If you are in devcontainer, nothing to do!

If not then
`rye sync` at the root of the repo will install all the dependenceis

## Run


### Using Azure OpenAI or OpenAI

- See .env.example for the environment variables that need to be set.
- Rename .env.example to .env

```bash
# run via rye
rye run sophisticated-app indexing/experiment=azure_openai_gpt4o
```

```bash
# or directly run it
python examples/sophisticated-app/app/main.py indexing/experiment=azure_openai_gpt4o
```

### Using Ollama

```bash
# run via rye
rye run sophisticated-app indexing/experiment=gemma2_9b
```

```bash
# or directly run it
python examples/sophisticated-app/app/main.py indexing/experiment=gemma2_9b
```

Look in the `examples/sophisticated-app/app/configs/experiment/gemma2_9b.yaml`
for more details.

