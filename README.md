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

It should look like this,

<img width="1920" height="1036" alt="image" src="https://github.com/user-attachments/assets/3ebe56ce-39c6-4025-9013-3bd679e6e126" />

in the above example, the answer is evaluated 3 times and then passed as `max_loops` has been set to 3.

## Configuration file

The configuration file is located at `~/.sidekick/config.yaml`. It supports **role-based model configuration**, allowing each node (plan, research, answer, factcheck, critic) to use different models and parameters.

### Example Configuration

```yaml
# Define base models for tier selection (name + URL only)
models:
  small: # Used for answer/critic nodes (text generation & viewing full context)
    base_url: http://localhost:11434
    name: llama2  # or another model with large context window support
  large: # Used for plan/research/factcheck nodes (reasoning tasks)
    base_url: http://localhost:11434
    name: mixtral-8x7b-instruct-q4_0

roles: # Configure which model + parameters each node uses

  plan:                    # Defaults to large model with optimized settings
    model: large           # Use small? Override to "small" if desired.
    num_ctx: 4096          # Context window for planning topic selection
    temperature: 0.3       # Low temperature for deliberate, predictable outputs
  
  research:                # Defaults to large model
    model: large          
    num_ctx: 4096         
    temperature: 0.7      
  
  answer:                  # Defaults to small model for efficient text generation
    model: small           
    num_ctx: 32768        
    temperature: 0.9
      
  factcheck:               # Defaults to large model for accuracy-critical tasks
    model: large
    num_ctx: 4096         
    temperature: 0.5
      
  critic:          # Evaluation benefits from large context window
    model: small           # Override if needed
    num_ctx: 32768        
    temperature: 0.7
   
# Other optional configurations below

logging: # Optional
  mode: w      # 'w' to overwrite log file, 'a' to append
  level: INFO  # DEBUG/INFO/WARNING/ERROR/FATAL - adjust verbosity

web:  # REQUIRED for Tavily web searches
  url: https://api.tavily.com
  api_key: your_tavily_api_key_here  # Get a free key from tavily.com

max_loops: 3  # Optional. Maximum number of researcher-critic refinement cycles.
```

## Configuration Guide

### Where to Put What

| Section | Purpose |
|---------|---------|
| **`models:`** | Define your Ollama model definitions (base model metadata only - name and base_url) |
| **`roles:`** | Configure which model + parameters each node uses (temp, num_ctx, and model size selection go here) |
| **`web:`** | Required - Tavily API credentials for web search |
| **`logging:`** | Optional - control log verbosity and file overwriting mode |

### Default Behavior & Defaults

If you don't specify a `roles:` section (or skip certain roles), Sidekick uses built-in defaults:

| Role | Default Model | Context | Temperature | Use Case |
|------|--------------|---------|-------------|----------|
| **plan** | large (from models.large) | 4096 | 0.3 | Complex topic breakdown - needs reasoning power |
| **research** | large (from models.large) | 4096 | 0.7 | Synthesizing multiple sources - needs smart model |
| **answer** | small (from models.small) | 32768 | 0.9 | Text drafting - doesn't need large model, generate creatively |
| **factcheck** | large (from models.large) | 4096 | 0.5 | Accuracy-critical verification |
| **critic** | small (from models.small) | 32768 | 0.7 | Evaluation needs to see full research document |

### Model Tier Selection Guide

**Choose `small` for roles that:**
- Generate straightforward text (answer drafting, creative writing at high temperature)
- Evaluate based on gathered information (critique)
- Need larger context windows to view full documents

**Choose `large` for roles that:**
- Break down complex queries into sub-topics (planning)
- Synthesize information from multiple sources (research)
- Verify factual accuracy through careful reasoning (factchecking)

### Context Window Considerations

- **Default ctx-size**: 4096 tokens (unless overridden in role config)
- **Answer generation**: Uses large context (32768) to view entire research document
- **Recommendation**: Leave at default unless you know your model's maximum context limit; setting `num_ctx` higher than a model supports may cause issues

### Temperature Considerations

| Range | Description | Appropriate For |
|-------|-------------|-----------------|
| Lower (0.3-0.5) | Careful/reasoning tasks where predictability matters most | Planning & Factchecking |
| Medium (0.7) | Balanced exploration vs convergence | Research & Critique |
| Higher (0.9+) | Creative text generation (answers) | Answer drafting |

### Best Practices

1. **Specify `web:`** - Required for external searches via Tavily API
2. **Define both model tiers in `models:`** - Even if not using, prevents errors
3. **Leave `num_ctx` as-is** - Default values work well; don't exceed model's max context size
4. **Use sensible defaults for `temperature`** - Unless you have specific needs (e.g., temperature=0.7 is a safe middle ground)

### Minimum Working Configuration

You only need to configure the required sections:

```yaml
models:
  small:
    base_url: http://localhost:11434
    name: llama2
  large:
    base_url: http://localhost:11434
    name: mixtral-8x7b-instruct-q4_0

roles:       # Optional - use defaults if omitted
  plan:
    model: large
  research: 
    model: large
  factcheck:
    model: large
  answer:
    model: small
  critic:
    model: small

web:
  url: https://api.tavily.com
  api_key: your_key_here

max_loops: 3  # Optional
```

---

## Agent Graph

The following diagram illustrates the general research agent flow for each query.

<div style="display:flex; justify-content:center;">
  <img width="2760" height="1800" alt="research agent flow" src="https://github.com/user-attachments/assets/5dbe273d-5b41-4d96-9189-07c0b1a73619" />
</div>

---

## How It Works

Sidekick uses a dual-model strategy with the default configuration optimizing for quality:

### Reasoning vs Generation Tasks

**Use large models for:**
- **Planning**: Breaking down complex queries into research topics requires reasoning
- **Research**: Synthesizing information from multiple sources needs smart models
- **Factchecking**: Verifying factual accuracy benefits from careful, accurate reasoning

**Use small models for:**
- **Answer generation**: Drafting text doesn't need large model reasoning power; uses full context window (32768)
- **Critic/evaluation**: Evaluating based on gathered facts benefits from seeing the entire research document in one context window

**Why this matters:**

- **Quality first**: Defaulting to smart models for complex tasks ensures better outcomes out-of-the-box
- **Resource efficiency**: Simple text generation can use smaller, faster models when appropriate
- **Context optimization**: Larger models get moderate context sizes (4096), while generation tasks get maximum context (32768)

### The Research Loop

The agent graph features iterative refinement:

1. **Researcher → Critic loop** (quality gate): Ensures thorough coverage and research across multiple topics
   - Can consume token budget; controlled by `max_loops` setting
   
2. **Factchecker → Planner loop** (accuracy gate): Improves factual accuracy when needed
   
3. **Web search sub-agent**: Planning/Research/Factcheck nodes all call external searches via Tavily API

### Default Configuration Behavior

Without a custom `roles:` section, Sidekick uses built-in defaults that optimize quality:

- Large models for planning/research/factchecking (reasoning-heavy tasks)
- Small models for answer/critic generation and evaluation
- All temperatures tuned to their default values; context sizes optimized per task

This ensures Sidekick works well immediately without requiring you to configure anything, while still allowing full customization when needed.

---