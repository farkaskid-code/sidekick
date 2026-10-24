# Sidekick

A research assistant designed for topical and deep research on any given query using local AI.

## Prerequisites
- A local [Ollama](https://ollama.com/) server.
- [UV](https://docs.astral.sh/uv/getting-started/installation/) package manager.
- A [Tavily](https://www.tavily.com/) API key.

## Getting Started

- Clone the repository.
- Install it using: `uv tool install .`.
- Create a configuration file. Details below.
- Run using `sidekick {query}`

## Configuration file
The file is located at `~/.sidekick/config.yaml` with the following format,

```markdown
models:
  small: # used for the critic and answer node. Smaller models are used to maximise the context size on a given hardware.
    base_url: {ollama server URL}
    name: {model_name}
    num_ctx: 32768
  large: # used for planning and research nodes. Larger models help with thorough research.
    base_url: {ollama server URL}
    name: {model_name}
    num_ctx: 8192

web: # Required for the "research" sub-agent
  url: {Tavily URL}
  api_key: {Tavily API key}

logging: # Optional
  mode: w # logging mode. `w` for write and `a` for append.
  level: INFO # logging level. DEBUG, INFO, ERROR etc.

max_loops: 3 # Optional, caps the number of research <-> Critic loops.
```

## Agent Graph
Following diagram illustrates the general flow for each query.

<img width="2760" height="1680" alt="research_agent_flow_dark_factcheck" src="https://github.com/user-attachments/assets/2aaa3f70-c7b4-49e6-829d-328cf52e9e9c" />


## Notes

- Sidekick features a `researcher` <-> `critic` loop as a quality gate that ensures the coverage and research of numerous possible topics pertaining to a query. This can consume significant time and token budget.
- It also features a `factcheck` <-> `planning` loop for factual accuracy. 
- Planning and Research nodes call a search sub-agent for research with access to `web_search`.
- Uses different size models for different roles. 
- `Planning` and `Research` will use larger and smarter models as they don't need as much context.
- `Critic` and `Answer` nodes will use a smaller model to fit more context.
