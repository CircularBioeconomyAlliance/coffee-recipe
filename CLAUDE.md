# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Install dependencies
uv sync

# Run the CLI chatbot agent
uv run src/agent.py

# Run the Streamlit web UI
uv run streamlit run src/app.py

# Run tests
uv run python tests/test_chat_app.py
uv run python tests/test_cba_ui.py
uv run python tests/test_functions.py
```

## Project Structure

```
coffee-recipe/
├── src/
│   ├── agent.py          # CLI chatbot agent
│   ├── app.py            # Streamlit web UI
│   └── prompts/
│       ├── system.txt    # Main system prompt
│       └── prompt_2.txt  # Alternate prompt
├── tests/
│   ├── test_chat_app.py  # App integration tests
│   ├── test_cba_ui.py    # Branding tests
│   └── test_functions.py # Unit tests
├── pyproject.toml
├── CLAUDE.md
└── README.md
```

## Architecture

This is a Strands Agents chatbot integrated with AWS Bedrock Knowledge Base for the Circular Bioeconomy Alliance (CBA).

### Key Components

- **`src/agent.py`**: CLI entry point. Creates a Strands Agent with `memory` and `use_llm` tools, loads the system prompt from a text file, and runs an interactive conversation loop.

- **`src/app.py`**: Streamlit web UI. Provides CBA-branded chat interface with session management, file upload, and agent integration.

- **`src/prompts/system.txt`**: Plain text system prompt (kept outside Python for easier editing). Instructs the agent to use `memory(action="retrieve", ...)` to query the knowledge base before answering.

### Strands Framework Patterns

- Import from `strands` (not `strands_agents`): `from strands import Agent`
- Tools come from `strands_tools`: `from strands_tools import memory, use_llm`
- Pass model ID as a string directly to Agent, not wrapped in BedrockModel
- Model IDs need `us.` prefix for cross-region inference: `us.anthropic.claude-sonnet-4-5-20250929-v1:0`

### AWS Configuration

Set these environment variables before running (do not hardcode credentials in code):
```bash
export AWS_DEFAULT_REGION=us-west-2
```

The Knowledge Base ID is configured via `STRANDS_KNOWLEDGE_BASE_ID` environment variable (set programmatically in agent.py and app.py).

### Memory Tool Usage

The `memory` tool interfaces with AWS Bedrock Knowledge Base:
- `memory(action="retrieve", query="...", min_score=0.4, max_results=5)` - searches the knowledge base
- `memory(action="store", content="...")` - stores information to the knowledge base
