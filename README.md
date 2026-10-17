# Sidekick

A research assistant designed for topical and deep research on any given query using local AI.

## Prerequisites
- A local [Ollama](https://ollama.com/) server.
- [UV](https://docs.astral.sh/uv/getting-started/installation/) package manager.

## Getting Started

- Clone the repository.
- Install it using: `uv tool install .`.
- Create a configuration file.
- Run using `sidekick {query}`

## Configuration file
The file is located at `~/.sidekick/config.yaml` with the following format,

```markdown
model:
  base_url: {ollama server URL}
  name: {model_name}
  num_ctx: 4096 # Set the largest possible value for your local setup, this helps with research context.

web:
  url: {Tavily URL}
  api_key: {Tavily API key}
```

## Notes

Sidekick features a `researcher` <-> `critic` quality gate loop that ensures the coverages and research of all possible topics pertaining to a query. This can consume significant time and token budget.
