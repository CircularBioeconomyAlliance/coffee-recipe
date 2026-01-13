# Technology Stack

## Core Framework

- **Strands Agents**: Primary framework for building the AI agent
- **AWS Bedrock**: Claude model hosting and Knowledge Base integration
- **Streamlit**: Web UI framework for the chat interface
- **Python 3.12+**: Required Python version

## Key Dependencies

- `strands-agents>=1.21.0` - Core agent framework
- `strands-agents-tools>=0.2.19` - Pre-built tools (memory, use_llm, etc.)
- `streamlit>=1.40.0` - Web interface
- `openpyxl>=3.1.0` - Excel file processing
- `pypdf>=4.0.0` - PDF text extraction

## Package Management

- **uv**: Modern Python package manager (required)
- Configuration in `pyproject.toml`
- Lock file: `uv.lock`

## AWS Configuration

- **Region**: `us-west-2` (hardcoded)
- **Model**: `us.anthropic.claude-sonnet-4-5-20250929-v1:0`
- **Knowledge Base ID**: `0ZQBMXEKDI`
- **Authentication**: AWS credentials via environment variables

## Common Commands

```bash
# Install dependencies
uv sync

# Run CLI agent
uv run src/agent.py

# Run web UI
uv run streamlit run src/app.py

# Run tests
uv run python tests/test_functions.py
uv run python tests/test_cba_ui.py
uv run python tests/test_chat_app.py
```

## Framework Patterns

### Strands Agents
- Import: `from strands import Agent` (not `strands_agents`)
- Tools: `from strands_tools import memory, use_llm`
- Model ID passed as string directly to Agent
- Cross-region model IDs require `us.` prefix

### Memory Tool Usage
- `memory(action="retrieve", query="...", min_score=0.4, max_results=10)` - search KB
- `memory(action="store", content="...")` - store to KB
- Knowledge Base is the authoritative source for all indicator data

### Environment Variables
- `AWS_DEFAULT_REGION` - Set programmatically to `us-west-2`
- `STRANDS_KNOWLEDGE_BASE_ID` - Set programmatically in config
- AWS credentials must be provided externally (never hardcoded)